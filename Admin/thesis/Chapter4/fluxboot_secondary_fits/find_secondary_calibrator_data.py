#!/usr/bin/env python3
"""
Extract secondary calibrator fluxboot fit tables from VLA pipeline weblog.tgz archives.

Assumed layout:
<ROOT>/
  24A-411.XXXX/                  # observation folder
    products/
      weblog.tgz                  # pipeline weblog archive
  25A-411.XXXX/
    products/
      weblog.tgz

The script:
1) finds all weblog.tgz under ROOT
2) extracts each to a temporary directory
3) locates pipeline-*/html/stage*/t2-4m_details.html for the fluxboot stage
4) parses:
   - "Spectral Indices" table (one row per source/band, typically includes X band)
   - "Data, error, fit, and residuals" table (per-SPW rows; frequency, data, error, fitted, residual)
5) writes one CSV for spectral summary and one CSV for per-SPW points
6) cleans up extracted pipeline directories automatically (tempdir)

Tested parsing expectation against your example t2-4m_details.html structure
(includes both the Spectral Indices table and the per-frequency residuals table). :contentReference[oaicite:0]{index=0}
"""

from __future__ import annotations

import argparse
import os
import re
import tarfile
import tempfile
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


PIPELINE_DIR_RE = re.compile(r"^pipeline-\d+", re.IGNORECASE)
STAGE_DIR_RE = re.compile(r"^stage\d+$", re.IGNORECASE)
_NUM_RE = re.compile(r"^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$")

@dataclass
class WeblogResult:
    obs_folder: str
    weblog_tgz: str
    pipeline_dir: str
    stage_dir: str
    t2_details_html: str


def find_weblog_archives(root: Path) -> list[Path]:
    # Most reliable: look specifically for products/weblog.tgz, but fall back to any weblog.tgz
    candidates = list(root.rglob("products/weblog.tgz"))
    if candidates:
        return sorted(set(candidates))
    return sorted(set(root.rglob("weblog.tgz")))


def safe_extract_tgz(tgz_path: Path, dest_dir: Path) -> None:
    """
    Extract tgz into dest_dir with basic path traversal protection.
    """
    with tarfile.open(tgz_path, "r:gz") as tf:
        members = tf.getmembers()
        for m in members:
            # prevent absolute paths / parent traversal
            if m.name.startswith("/") or ".." in Path(m.name).parts:
                raise RuntimeError(f"Unsafe path in tar member: {m.name}")
        tf.extractall(dest_dir, members=members)


def guess_fluxboot_stage_dirs(pipeline_html_dir: Path) -> list[Path]:
    """
    Your heuristic: find stageX dirs that contain 'bootstrappedFluxDensities-*.png'
    and then check for 't2-4m_details.html' in that same stage dir.
    """
    stage_dirs = [p for p in pipeline_html_dir.iterdir() if p.is_dir() and STAGE_DIR_RE.match(p.name)]
    stage_dirs = sorted(stage_dirs, key=lambda p: int(re.sub(r"\D+", "", p.name)))

    fluxboot_stages = []
    for sd in stage_dirs:
        pngs = list(sd.glob("bootstrappedFluxDensities-*.png"))
        if not pngs:
            # some weblogs use "-summary.png" naming; include that too
            pngs = list(sd.glob("bootstrappedFluxDensities-*-summary.png"))
        if pngs and (sd / "t2-4m_details.html").exists():
            fluxboot_stages.append(sd)

    # If none matched the PNG heuristic, fall back to any stage with t2-4m_details.html
    if not fluxboot_stages:
        for sd in stage_dirs:
            if (sd / "t2-4m_details.html").exists():
                fluxboot_stages.append(sd)

    return fluxboot_stages


def locate_t2_details(extracted_root: Path) -> list[WeblogResult]:
    """
    Find pipeline-*/html/stage*/t2-4m_details.html inside extracted_root.
    Prefer those stages that look like fluxboot based on bootstrappedFluxDensities PNG presence.
    """
    results: list[WeblogResult] = []

    # find pipeline-* directories anywhere under extraction (weblog.tgz layout can vary)
    pipeline_dirs = []
    for p in extracted_root.rglob("*"):
        if p.is_dir() and PIPELINE_DIR_RE.match(p.name):
            pipeline_dirs.append(p)
    pipeline_dirs = sorted(set(pipeline_dirs))

    for pdir in pipeline_dirs:
        html_dir = pdir / "html"
        if not html_dir.exists():
            continue

        stage_dirs = guess_fluxboot_stage_dirs(html_dir)
        for sd in stage_dirs:
            t2 = sd / "t2-4m_details.html"
            if t2.exists():
                results.append(
                    WeblogResult(
                        obs_folder="",  # filled by caller
                        weblog_tgz="",  # filled by caller
                        pipeline_dir=str(pdir),
                        stage_dir=str(sd),
                        t2_details_html=str(t2),
                    )
                )

    return results

def _parse_html_table_with_rowspan(html_path: Path, header_predicate) -> pd.DataFrame:
    """
    Parse an HTML table using BeautifulSoup, expanding rowspan/colspan.
    header_predicate(headers_norm) -> bool selects the desired table.
    """
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    tables = soup.find_all("table")

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip()).lower()

    for table in tables:
        # header row: prefer thead, else first tr with th
        header_tr = None
        thead = table.find("thead")
        if thead:
            header_tr = thead.find("tr")
        if header_tr is None:
            header_tr = table.find("tr")
        if header_tr is None:
            continue

        ths = header_tr.find_all(["th", "td"])
        headers = [re.sub(r"\s+", " ", th.get_text(" ", strip=True)) for th in ths]
        headers_norm = [norm(h) for h in headers]

        if not header_predicate(headers_norm):
            continue
        # collect all rows AFTER the header row
        body_rows = []
        # if thead exists, use tbody rows; else all trs skipping first
        trs = table.find_all("tr")
        # locate header index within trs
        try:
            header_idx = trs.index(header_tr)
        except ValueError:
            header_idx = 0
        data_trs = trs[header_idx + 1 :]

        # rowspan tracker: list of dicts { "value": str, "remaining": int }
        spans: list[Optional[dict]] = [None] * len(headers)

        for tr in data_trs:
            tds = tr.find_all(["td", "th"])
            if not tds:
                continue

            row: list[Optional[str]] = [None] * len(headers)

            # first, pre-fill from active rowspans
            for j in range(len(headers)):
                if spans[j] is not None and spans[j]["remaining"] > 0:
                    row[j] = spans[j]["value"]
                    spans[j]["remaining"] -= 1
                    if spans[j]["remaining"] == 0:
                        spans[j] = None

            # then fill remaining columns left-to-right from actual cells
            col = 0
            for td in tds:
                # advance to next empty col
                while col < len(headers) and row[col] is not None:
                    col += 1
                if col >= len(headers):
                    break

                text = td.get_text(" ", strip=True)
                text = re.sub(r"\s+", " ", text).strip()
                rs = int(td.get("rowspan", 1) or 1)
                cs = int(td.get("colspan", 1) or 1)

                for k in range(cs):
                    if col + k >= len(headers):
                        break
                    row[col + k] = text

                    if rs > 1:
                        spans[col + k] = {"value": text, "remaining": rs - 1}

                col += cs

            body_rows.append(row)

        df = pd.DataFrame(body_rows, columns=headers)
        return df

    return pd.DataFrame()


def _is_number(s: str) -> bool:
    s = (s or "").strip()
    s = s.replace("\u2212", "-")  # unicode minus
    return bool(_NUM_RE.match(s))


def _parse_points_table_malformed(html_path: Path) -> pd.DataFrame:
    """
    Parse the per-frequency 'Data, error, fit, and residuals' table even if <tr> tags are malformed.
    Strategy:
      1) find the correct table by header text
      2) stream all <td> cells after header
      3) reconstruct rows:
         - if we see a cell with rowspan OR a non-numeric token -> treat as Source for the next N rows
         - then read 5 numeric cells per data row (freq, data, err, fit, resid)
    """
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip()).lower()

    target_table = None
    for table in soup.find_all("table"):
        # collect header-ish text
        header_text = " ".join(norm(th.get_text(" ", strip=True)) for th in table.find_all("th"))
        if ("frequency" in header_text and "ghz" in header_text
            and "fitted" in header_text
            and "residual" in header_text
            and "source" in header_text):
            target_table = table
            break

    if target_table is None:
        return pd.DataFrame()

    # Find where data begins: after the last header row in thead if present, else after first row containing "Frequency"
    start_node = None
    thead = target_table.find("thead")
    if thead:
        trs = thead.find_all("tr")
        start_node = trs[-1] if trs else None

    # Collect all td cells after header
    # We iterate over *all* td in document order inside the table, but skip those that are inside thead.
    tds = []
    for td in target_table.find_all("td"):
        if thead and thead in td.parents:
            continue
        txt = re.sub(r"\s+", " ", td.get_text(" ", strip=True)).strip()
        tds.append((td, txt))

    rows = []
    current_source = None

    i = 0
    while i < len(tds):
        td, txt = tds[i]

        # Detect a Source cell:
        # - has rowspan attribute (common for Source), OR
        # - is non-numeric and looks like a calibrator name (starts with J/B/3C etc.)
        rowspan = td.get("rowspan")
        if rowspan is not None or (txt and not _is_number(txt)):
            current_source = txt
            i += 1
            # After source cell, we expect 5 numeric cells (freq, data, err, fit, resid)
            if i + 4 >= len(tds):
                break
            vals = [tds[i + k][1] for k in range(5)]
            rows.append([current_source] + vals)
            i += 5
            continue

        # Otherwise, this should be a continuation row: 5 numeric cells
        if current_source is None:
            # We can't assign these values to any source; skip one and continue
            i += 1
            continue

        if i + 4 >= len(tds):
            break
        vals = [tds[i + k][1] for k in range(5)]
        rows.append([current_source] + vals)
        i += 5

    df = pd.DataFrame(
        rows,
        columns=[
            "Source",
            "Frequency [GHz]",
            "Data",
            "Error",
            "Fitted Data",
            "Residual: Data-Fitted Data",
        ],
    )

    # Numeric conversion
    for c in df.columns[1:]:
        df[c] = (
            df[c].astype(str)
                 .str.replace("\u2212", "-", regex=False)
                 .str.replace(",", "", regex=False)
        )
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Drop any weird non-parsed rows
    df = df.dropna(subset=["Frequency [GHz]", "Data"]).reset_index(drop=True)
    return df


def parse_fluxboot_tables(t2_html_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      spectral_df: Spectral Indices summary table
      points_df: per-frequency/SPW table
    """
    spectral_df = pd.DataFrame()
    points_df = pd.DataFrame()

    # ---- Try pandas first (fast path)
    points_df = _parse_points_table_malformed(t2_html_path)
    
    spectral_df = _parse_html_table_with_rowspan(
        t2_html_path,
        header_predicate=lambda hs: ("spectral index" in " ".join(hs))
                                    and ("band center" in " ".join(hs) and "ghz" in " ".join(hs))
                                    and ("source" in " ".join(hs))
                                    and ("band" in " ".join(hs)),
    )
    return spectral_df, points_df


def obs_id_from_path(weblog_tgz: Path) -> str:
    """
    Extract a human-readable observation folder name: 24A-411.XXXX or 25A-411.XXXX.
    """
    # observation folder is usually parent of products/
    if weblog_tgz.parent.name == "products":
        return weblog_tgz.parent.parent.name
    return weblog_tgz.parent.name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=str, help="Root directory containing observation folders (24A-411.*, 25A-411.*)")
    ap.add_argument("--outdir", type=str, default=".", help="Output directory")
    ap.add_argument("--keep-all-stages", action="store_true",
                    help="If multiple matching stages exist, keep them all (default: keep first per weblog)")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    spectral_rows: list[pd.DataFrame] = []
    points_rows: list[pd.DataFrame] = []
    index_rows: list[dict] = []

    # Iterate over *all* immediate subfolders in root
    for obs_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        obs_id = obs_dir.name
        if obs_id == "25A-157.sb47894310.eb48187719.60748.13153532408":
            continue  # Skip the one failed observation.
        products_dir = obs_dir / "products"
        weblog_tgz = products_dir / "weblog.tgz"

        # --- status: products missing
        if not products_dir.exists():
            index_rows.append({
                "obs_id": obs_id,
                "status": "products_missing",
                "weblog_tgz": "",
                "pipeline_dir": "",
                "stage_dir": "",
                "t2_details_html": "",
            })
            continue

        # --- status: weblog.tgz missing
        if not weblog_tgz.exists():
            index_rows.append({
                "obs_id": obs_id,
                "status": "weblog_missing",
                "weblog_tgz": "",
                "pipeline_dir": "",
                "stage_dir": "",
                "t2_details_html": "",
            })
            continue

        # --- extract and inspect weblog
        try:
            with tempfile.TemporaryDirectory(prefix=f"weblog_extract_{obs_id}_") as td:
                td_path = Path(td)
                safe_extract_tgz(weblog_tgz, td_path)

                found = locate_t2_details(td_path)

                # --- status: no pipeline / no t2 tables
                if not found:
                    index_rows.append({
                        "obs_id": obs_id,
                        "status": "no_fluxboot_tables",
                        "weblog_tgz": str(weblog_tgz),
                        "pipeline_dir": "",
                        "stage_dir": "",
                        "t2_details_html": "",
                    })
                    continue

                if not args.keep_all_stages:
                    found = [found[0]]

                for item in found:
                    spectral_df, points_df = parse_fluxboot_tables(Path(item.t2_details_html))
                    meta = {
                        "obs_id": obs_id,
                        "weblog_tgz": str(weblog_tgz),
                        "pipeline_dir": item.pipeline_dir,
                        "stage_dir": item.stage_dir,
                        "t2_details_html": item.t2_details_html,
                    }

                    if not spectral_df.empty:
                        sdf = spectral_df.copy()
                        for k, v in meta.items():
                            sdf.insert(0, k, v)
                        spectral_rows.append(sdf)

                    if not points_df.empty:
                        pdf = points_df.copy()
                        for k, v in meta.items():
                            pdf.insert(0, k, v)
                        points_rows.append(pdf)

                    index_rows.append({**meta, "status": "ok"})
                    
        except Exception as e:
            # --- status: extraction / parsing failure
            print(e)
            index_rows.append({
                "obs_id": obs_id,
                "status": f"error: {type(e).__name__}",
                "weblog_tgz": str(weblog_tgz),
                "pipeline_dir": "",
                "stage_dir": "",
                "t2_details_html": "",
            })

    # --- write outputs
    index_df = pd.DataFrame(index_rows)
    index_df.to_csv(outdir / "index.csv", index=False)

    if spectral_rows:
        pd.concat(spectral_rows, ignore_index=True).to_csv(
            outdir / "secondary_spectral_summary.csv", index=False
        )

    if points_rows:
        pd.concat(points_rows, ignore_index=True).to_csv(
            outdir / "secondary_per_spw_points.csv", index=False
        )

    print(f"Wrote status index: {outdir / 'index.csv'}")


if __name__ == "__main__":
    main()
