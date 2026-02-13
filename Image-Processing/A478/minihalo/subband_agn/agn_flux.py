import pandas as pd
import matplotlib.pyplot as plt

images = ["images/image_spw0-7", "images/image_spw8-15", "images/image_spw16-23", "images/image_spw24-31"]
labels = ["Minihalo AGN"]
regions = ["circle[[4h13m25.29s, 10d27m54.6s], 5arcsec]"]
log_dir = "fit_logs"


def _read_log_value(l: str):
    """Return (flux, error) in mJy from a log line supporting Jy, mJy, and uJy."""
    pattern = r".*:\s*([\d.]+)\s*\+/-\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    # pattern = r".*\[flux\]:\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    match = re.match(pattern, l)
    if not match:
        print(f"Unknown flux scale in {l.strip()}")
        return np.nan, np.nan

    value, error, unit = match.groups()
    value, error = float(value), float(error)
    # value, unit = match.groups()
    # Convert to mJy
    if unit == "Jy":
        scale = 1000.0
    elif unit == "mJy":
        scale = 1.0
    elif unit == "uJy":
        scale = 1.0 / 1000.0
    else:
        scale = np.nan
    return value * scale, error * scale


def _get_flux_from_log(log):
    with open(log, "r") as f:
        for l in f.readlines():
            if "Integrated:" in l:
            # if "flux density" in l:
                return _read_log_value(l)
            # elif "Integrated:" in l:
            #     return read_log_value(l)
    return np.nan, np.nan


# Fit the fluxes
log_files = []
for image in images:
    image_name = f"{image}.image.tt0"
    image_logs = []
    for region, label in zip(regions, labels):
        log_name = f"{log_dir}/{os.path.basename(image)}_{label}.log"
        image_logs.append(log_name)
        print()
        imfit(image_name, region=region, logfile=log_name, append=False)
    log_files.append(image_logs)

# Grab the log data
data = []
for d, all_l in zip(images, log_files):
    for p, l in zip(labels, all_l):
        flux, error = _get_flux_from_log(l)
        data.append({
            "Dataset": d.split("_")[-1],
            "Position": p,
            "Flux (mJy)": flux,
            "Error (mJy)": error
        })

df = pd.DataFrame(data)
df.sort_values(by=['Dataset', 'Position'], inplace=True)
print(df.to_string(index=False))