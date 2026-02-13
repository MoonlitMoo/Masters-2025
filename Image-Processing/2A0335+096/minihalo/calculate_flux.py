import os

# Get image pixels and RMS
ia.open("minihalo.image.tt0")
pix = ia.getchunk()
ia.close()
res = imstat(f"minihalo.residual.tt0")
sigma = res["sigma"][0]

# Get mask and flux
agn_region = ["circle[[3h38m41.4s, 9d58m17.5s], 4arcsec]",
    "circle[[3h38m40.6s, 9d58m11.6s], 4arcsec]",
    "circle[[3h38m39.9s, 9d58m07.3s], 4arcsec]",
    "circle[[3h38m40.3s, 9d58m17.9s], 4arcsec]"
]
_, mask, _ = contour_sum(pix, 3 * sigma, pick='seed', seed=(1150, 1150))
f, e, s = get_minihalo_flux_density("minihalo", output_image="minihalo_masked", mask=mask, agn_region=agn_region,verbose=True)

# Save mask
os.system("cp -r minihalo.mask significance.mask")
ia.open("significance.mask")
ia.putchunk(mask.astype(int))
ia.close()
