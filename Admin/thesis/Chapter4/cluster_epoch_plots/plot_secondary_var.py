import re
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import chi2
import matplotlib.pyplot as plt

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 12 * f_scale

def extract_mjd(obs_id: str):
    if not isinstance(obs_id, str):
        return np.nan

    m = re.search(r"\.(\d{5}\.\d+)$", obs_id)
    return float(m.group(1)) if m else np.nan

def fit_scalar_full_spectrum(g, mjd_a, mjd_b,
                            freq_col="Frequency [GHz]",
                            data_col="Data",
                            err_col="Error"):
    a = g[g["mjd"] == mjd_a][[freq_col, data_col, err_col]].copy()
    b = g[g["mjd"] == mjd_b][[freq_col, data_col, err_col]].copy()

    # align on frequency (inner join)
    m = a.merge(b, on=freq_col, suffixes=("_a", "_b"), how="inner").dropna()

    Sa = m[f"{data_col}_a"].to_numpy(float)
    Sb = m[f"{data_col}_b"].to_numpy(float)
    ea = m[f"{err_col}_a"].to_numpy(float)
    eb = m[f"{err_col}_b"].to_numpy(float)

    n = len(Sa)
    if n < 3:
        return None  # too few points to assess linear scaling

    def chi2_of_C(C):
        denom = ea**2 + (C**2) * eb**2
        return np.sum((Sa - C*Sb)**2 / denom)

    # bracket: allow negative if you want, but flux should be positive ⇒ restrict to >0
    res = minimize_scalar(chi2_of_C, bounds=(0, 5), method="bounded")
    C = float(res.x)
    chi2_val = float(chi2_of_C(C))
    dof = n - 1
    red_chi2 = chi2_val / dof
    p_val = 1 - chi2.cdf(chi2_val, dof)

    # 1-sigma uncertainty via Δχ² = 1 for 1 parameter
    # Find C where chi2 = chi2_min + 1 on either side.
    target = chi2_val + 1.0

    def find_side(lo, hi):
        # simple bisection on chi2(C)-target assuming monotonic away from min locally
        for _ in range(60):
            mid = 0.5*(lo+hi)
            if (chi2_of_C(mid) - target) * (chi2_of_C(lo) - target) <= 0:
                hi = mid
            else:
                lo = mid
        return 0.5*(lo+hi)

    # search windows around C
    left = max(1e-6, C/10)
    right = C*10

    # expand until we bracket target
    lo = left
    while lo > 1e-6 and chi2_of_C(lo) < target:
        lo *= 0.5
    hi = C
    C_lo = find_side(lo, hi) if chi2_of_C(lo) > target else np.nan

    lo = C
    hi = right
    while hi < 1e6 and chi2_of_C(hi) < target:
        hi *= 2
    C_hi = find_side(lo, hi) if chi2_of_C(hi) > target else np.nan

    C_err = 0.5*((C - C_lo) + (C_hi - C)) if np.isfinite(C_lo) and np.isfinite(C_hi) else np.nan

    return {
        "C": C,
        "C_err": C_err,
        "chi2": chi2_val,
        "dof": dof,
        "red_chi2": red_chi2,
        "p_value": p_val,
        "n_freq": n,
    }

df = pd.read_csv("../fluxboot_secondary_fits/secondary_per_spw_points.csv")

df["mjd"] = df["obs_id"].apply(extract_mjd)
df["year"] = [2024 if "24A" in i else 2025 for i in df["obs_id"]]
rows = []

for (src, year), g in df.groupby(["Source", "year"]):
    mjds = sorted(g["mjd"].dropna().unique())
    if len(mjds) != 2:
        continue

    out = fit_scalar_full_spectrum(g, mjds[0], mjds[1])
    if out is None:
        continue

    rows.append({
        "Source": src,
        "year": int(year),
        "mjd1": int(mjds[0]),
        "mjd2": int(mjds[1]),
        **out
    })

res_df = pd.DataFrame(rows)
res_df["C_percent"] = (res_df["C"] - 1.0) * 100.0
res_df["C_percent_err"] = res_df["C_err"] * 100.0
res_df["good_fit"] = res_df["p_value"] > 0.05
res_df["color"] = ["r" if i == 24 else "g" for i in res_df["year"]]

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# res_df columns assumed:
# Source, year, C_percent, C_percent_err, good_fit (bool)

# Stable ordering on x-axis
sources = list(pd.unique(res_df["Source"]))
xpos = {s: i for i, s in enumerate(sources)}
x = res_df["Source"].map(xpos).to_numpy()

years = np.sort(res_df["year"].unique())
cmap = plt.get_cmap("tab10") if len(years) <= 10 else plt.get_cmap("tab20")
year_to_color = {y: cmap(i % cmap.N) for i, y in enumerate(years)}

fig, ax = plt.subplots(figsize=(8, 4))

markers = {True: "o", False: "s"}  # good fit circle, bad fit square

for good_flag in [True, False]:
    sub = res_df[res_df["good_fit"] == good_flag]
    for y, gy in sub.groupby("year"):
        ax.errorbar(
            gy["Source"].map(xpos),
            gy["C_percent"],
            yerr=gy["C_percent_err"],
            fmt=markers[good_flag],
            linestyle="none",
            color=year_to_color[y],
            capsize=2,
            markersize=8,
        )

ax.axhline(0, ls="--", lw=1)
ax.set_xlabel("Source")
ax.set_ylabel("Scale factor C (%)")
ax.set_xticks(range(len(sources)))
ax.set_xticklabels(sources, rotation=45, ha="right")
ax.grid()

# Legends: year = colour, fit quality = shape
year_handles = [
    mlines.Line2D([], [], color=year_to_color[y], marker="o", linestyle="none", label=str(y))
    for y in years
]
shape_handles = [
    mlines.Line2D([], [], color="black", marker="o", linestyle="none", label="Good"),
    mlines.Line2D([], [], color="black", marker="s", linestyle="none", label="Poor"),
]

leg1 = ax.legend(handles=year_handles, title="Year", loc="upper left", bbox_to_anchor=(1.02, 1))
ax.add_artist(leg1)
ax.legend(handles=shape_handles, title="Fit", loc="lower left", bbox_to_anchor=(1.02, 0))

ax.axhline(5, ls='--', lw=1, c='k', alpha=0.8)
ax.axhline(-5, ls='--', lw=1, c='k', alpha=0.8)

plt.tight_layout()
plt.savefig("secondary_variation.pdf", dpi=300, bbox_inches="tight")

print(
    f"Weighted mean |ΔC| (%) (good fits) = "
    f"{np.average(res_df.loc[res_df['good_fit'], 'C_percent'].abs(), weights=1.0 / res_df.loc[res_df['good_fit'], 'C_percent_err']**2):.2f}"
)

