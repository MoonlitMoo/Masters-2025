#!/usr/bin/env python3
"""
Build CASA regions (centre, tail, full) on an image grid and export boolean
numpy masks for reuse.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np

def _build_regions(shape, coords):
    # Region text (exactly as provided)
    centre_region_txt = "ellipse[[17:20:09.4, +026.37.30], [30.0arcsec, 34.8arcsec], 127deg]"
    tail_region_txt = (
        "poly[[17:20:10.50000, +026.38.02.0000], [17:20:11.40000, +026.38.07.5000], "
        "[17:20:14.20000, +026.37.34.0000], [17:20:14.20000, +026.37.00.0000], "
        "[17:20:13.00000, +026.36.33.0000], [17:20:11.20000, +026.36.23.0000], "
        "[17:20:09.70000, +026.36.30.0000], [17:20:09.30000, +026.36.35.0000], "
        "[17:20:09.70000, +026.36.56.0000]]"
    )

    centre_region = rg.fromtext(centre_region_txt, shape=shape, csys=coords)
    tail_region = rg.fromtext(tail_region_txt, shape=shape, csys=coords)

    # Remove centre from tail
    tail_minus_centre = rg.difference(tail_region, centre_region)

    # Union of centre + tail
    full_region = rg.makeunion(regions={"c": centre_region, "t": tail_minus_centre})

    return centre_region, tail_minus_centre, full_region, centre_region_txt, tail_region_txt


def _region_to_bool_mask(mask_image_path: str, sel_region) -> np.ndarray:
    """
    Given a CASA mask image directory (copied from some .mask), write 0/1 into it
    and return the resulting mask as a squeezed boolean ndarray.
    """
    ia.open(mask_image_path)
    try:
        # Default everything to 0, then region to 1
        ia.set(0.0, region=rg.complement(sel_region))
        ia.set(1.0, region=sel_region)

        arr = np.array(ia.getchunk(), dtype=bool)
        return np.squeeze(arr)
    finally:
        ia.close()

outdir = "rxj1720_masks"
image_tt0 = "../../../../Image-Processing/RXJ1720+2638/minihalo/model_minihalo/minihalo.image.tt0"
src_mask = "../../../../Image-Processing/RXJ1720+2638/minihalo/model_minihalo/minihalo.mask"

if not os.path.exists(image_tt0):
    raise FileNotFoundError(f"Image not found: {image_tt0}")
if not os.path.exists(src_mask):
    raise FileNotFoundError(f"Source mask directory not found: {src_mask}")
os.makedirs(outdir, exist_ok=True)
# Read shape + coordsys record from the reference image
ia.open(image_tt0)
try:
    shape = ia.shape()
    coords = ia.coordsys().torecord()
finally:
    ia.close()

centre_region, tail_region, full_region, centre_txt, tail_txt = _build_regions(shape, coords)

# Create three independent working mask copies so they don't overwrite each other
centre_mask_dir = f"{outdir}/centre.mask"
tail_mask_dir = f"{outdir}/tail.mask"
full_mask_dir = f"{outdir}/full.mask"

for d in (centre_mask_dir, tail_mask_dir, full_mask_dir):
    if os.path.isdir(d):
        os.system(f"rm -r {d}")
    os.system(f"cp -r {src_mask} {d}")

# Build boolean masks
centre_mask = _region_to_bool_mask(centre_mask_dir, centre_region)
tail_mask = _region_to_bool_mask(tail_mask_dir, tail_region)
full_mask = _region_to_bool_mask(full_mask_dir, full_region)

# Save numpy arrays
np.save(f"{outdir}/centre_mask.npy", centre_mask)
np.save(f"{outdir}/tail_mask.npy", tail_mask)
np.save(f"{outdir}/full_mask.npy", full_mask)