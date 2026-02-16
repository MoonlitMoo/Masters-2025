import os

# Get image pixels and RMS
ia.open("minihalo.image.tt0")
pix = ia.getchunk()
ia.close()
res = imstat(f"minihalo.residual.tt0")
sigma = res["sigma"][0]

# Get mask and flux
agn_region = ["circle[[21h29m39.97s, 0d05m21.05s], 5arcsec]"]
# _, mask, _ = contour_sum(pix, 3 * sigma, pick='seed', seed=(1150, 1150))
# Estimate mask from G19
os.system("cp -r minihalo.mask significance.mask")
ia.open("significance.mask")
shape, coords = ia.shape(), ia.coordsys().torecord()
mask_text = "ellipse[[21h29m39.5s, +0d05m24.8s], [14.5arcsec, 29.5arcsec], 0deg]"
s2_text = "circle[[21h29m39.1s, +0d05m9.8s], 5arcsec]"
mask_reg = rg.fromtext(mask_text, shape=shape, csys=coords)
excl_reg = rg.fromtext(s2_text, shape=shape, csys=coords)
mask_reg = rg.difference(mask_reg, excl_reg)  # Remove s2 from mask
ia.set(0.0, region=rg.complement(mask_reg))
ia.set(1.0, region=mask_reg)
mask = np.squeeze(np.array(ia.getchunk(), dtype=bool))
ia.putchunk(mask.astype(int))
ia.close()

f, e, s = get_minihalo_flux_density("minihalo", output_image="minihalo_masked", mask=mask, agn_region=agn_region,verbose=True)
