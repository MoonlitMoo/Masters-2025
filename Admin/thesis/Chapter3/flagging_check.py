#!/usr/bin/env python3
"""
Collect final flagging statistics using flagdata(mode='summary').

Output CSV columns:
  cluster, config, epoch, spw, freq_GHz, flagged_frac, retained_frac, exposure_s, ms_path
"""

import re
import csv
import json
from pathlib import Path
from typing import Dict, Tuple

from casatasks import flagdata
from casatools import msmetadata, ms

MS_RE = re.compile(r"^(cconfig2|cconfig|dconfig1|dconfig2)-p(\d+)\.ms$")


def find_last_selfcal_ms(full_image_dir: Path) -> Dict[str, Path]:
    best = {}
    for p in full_image_dir.iterdir():
        if not p.is_dir():
            continue
        m = MS_RE.match(p.name)
        if not m:
            continue
        base, px = m.group(1), int(m.group(2))
        if base not in best or px > best[base][0]:
            best[base] = (px, p)
    return {k: v[1] for k, v in best.items()}


def base_to_config_epoch(base: str) -> Tuple[str, str]:
    if base.startswith("cconfig"):
        return "C", "2" if base == "cconfig2" else "1"
    if base.startswith("dconfig"):
        return "D", base[-1]
    return "?", "?"


def main():
    imaging_root = Path("../../../Image-Processing")
    out_csv = Path("final_flagging_summary.csv")

    rows = []
    header = [
        "cluster", "config", "epoch", "freq_Hz",
        "flagged_frac", "retained_frac",
        "exposure_s", "ms_path"
    ]

    for cluster_dir in sorted(imaging_root.iterdir()):
        full_image = cluster_dir / "full_image"
        if not full_image.exists():
            print(f"Did not find full_image for {cluster_dir}")
            continue

        cluster = cluster_dir.name
        ms_map = find_last_selfcal_ms(full_image)
        
        if not ms_map:
            print(f"Did not find self calibration for {cluster_dir}")
            continue
        
        for base, ms_path in ms_map.items():
            config, epoch = base_to_config_epoch(base)
            vis = str(ms_path)

            # Flagging summary
            summary = flagdata(
                vis=vis,
                mode="summary",
                spwchan=True,
                field="",
                scan=""
            )

            msmd.open(vis)
            nspw = msmd.nspw()
            avg_spw_freq = [msmd.chanfreqs(i).mean() for i in range(nspw)]
            exposure_s = msmd.effexposuretime()['value']
            msmd.close()

            for spw in range(nspw):
                if f'{spw}' in summary['spw']:
                    stats = summary['spw'][f'{spw}']
                    total = stats["total"]
                    flagged = stats["flagged"]
                    f_frac = flagged / total
                else:
                    f_frac = 1

                rows.append([
                    cluster,
                    config,
                    epoch,
                    avg_spw_freq[spw],
                    f_frac,
                    1 - f_frac,
                    f"{exposure_s:.1f}",
                    vis
                ])

    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_csv}")


main()
