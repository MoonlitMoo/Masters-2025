# Z3146 Minihalo

# Check point flux

- S4: NE (this isn’t the MH AGN, its separate stuff to the east)
- S3: SW (this isn’t the MH AGN, its separate stuff to the east)
- S6: SW double lobe
- Minihalo AGN (S1): W close point with diffuse stuff
- S2: W Further without diffuse stuff.

```jsx
datasets = ["cconfig-p4", "dconfig1-p4", "dconfig2-p4"]
labels = ["S1", "S2", "S3", "S4", "S6"]
regions = ["circle[[10h23m39.60s, 4d11m10.75s], 5arcsec]",
           "circle[[10h23m38.68s, 4d11m04.63s], 5arcsec]",
           "circle[[10h23m44.75s, 4d10m35.89s], 3arcsec]",
           "circle[[10h23m45.34s, 4d10m44.16s], 3arcsec]",
           "circle[[10h23m37.16s, 4d09m05.83s], 4arcsec]"
           ]

check_point_flux(datasets, regions, labels)
```

![flux_comparison.png](Z3146%20Minihalo/flux_comparison.png)