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
# f, e, s = get_minihalo_flux_density("minihalo", output_image="minihalo_masked", mask=mask, agn_region=agn_region,verbose=True)

# Lobe mask and flux
se_mask_text = "circle[[3h38m43.3s, +9d57m51.7s], 17.5arcsec]"
nw_mask_text = "circle[[3h38m37.9s, +9d58m31.3s], 17.5arcsec]"

mask_text = nw_mask_text
os.system("cp -r minihalo.mask significance.mask")
ia.open("significance.mask")
shape, coords = ia.shape(), ia.coordsys().torecord()
mask_reg = rg.fromtext(mask_text, shape=shape, csys=coords)
ia.set(0.0, region=rg.complement(mask_reg))
ia.set(1.0, region=mask_reg)
mask = np.squeeze(np.array(ia.getchunk(), dtype=bool))
ia.putchunk(mask.astype(int))
ia.close()

null_region = [mask_text.replace("17.5", "0.5")]

f, e, s = get_minihalo_flux_density("minihalo", output_image="minihalo_masked", mask=mask, agn_region=null_region,verbose=True)

# Save mask
os.system("cp -r minihalo.mask significance.mask")
ia.open("significance.mask")
ia.putchunk(mask.astype(int))
ia.close()
