import os

# Get image pixels and RMS
ia.open("minihalo.image.tt0")
pix = ia.getchunk()
ia.close()
res = imstat(f"minihalo.residual.tt0")
sigma = res["sigma"][0]

# Get mask and flux
agn_reg = ["circle[[11h55m15.1s, 23d24m01.9s], 20arcsec]",
    "circle[[11h55m18.6s, 23d24m22.6s], 20arcsec]"]
_, mask, _ = contour_sum(pix, 3 * sigma, pick='seed', seed=(1150, 1150))
f, e, s = get_minihalo_flux_density("minihalo", output_image="minihalo_masked", mask=mask, agn_region=agn_reg, verbose=True)

# Save mask
os.system("cp -r minihalo.mask significance.mask")
ia.open("significance.mask")
ia.putchunk(mask.astype(int))
ia.close()
