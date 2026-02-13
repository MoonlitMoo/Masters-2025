datasets = ['cconfig', 'dconfig1', 'dconfig2']
labels = ["Minihalo AGN", "S3", "S4"]
regions = ["circle[[16h32m46.94s, 5d34m32.5s], 2arcsec]",
           "circle[[16h32m41.15s, 5d34m16.87s], 3arcsec]",
           "circle[[16h32m45.88s, 5d31m57.99s], 2.5arcsec]"]
check_point_flux([datasets[0]], regions, labels, clean_params={
    "sidelobethreshold": 2.5, "scales": [0, 2, 4], "smallscalebias":0.5})
