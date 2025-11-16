datasets = ["cconfig", "dconfig1", "dconfig2"]
labels = ["Minihalo AGN", "Head-Tail", "TL", "M"]
regions = ["circle[[4h13m25.29s, 10d27m54.6s], 5arcsec]",
           "circle[[4h13m38.37s, 10d28m08.54s], 2.5arcsec]",
           "circle[[4h13m35.25s, 10d29m21.23s], 2.5arcsec]",
           "circle[[4h13m31.88s, 10d28m38.90s], 2.5arcsec]"]

check_point_flux(datasets, regions, labels)
