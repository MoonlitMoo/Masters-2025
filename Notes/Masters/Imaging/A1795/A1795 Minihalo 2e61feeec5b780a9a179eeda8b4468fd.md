# A1795 Minihalo

# Check point fluxes

- Minihalo AGN
- S1: West point
- S2: SE head tail

```jsx
datasets = ["cconfig-p4", "dconfig1-p4", "dconfig2-p4"]
labels = ["Minihalo AGN 1", "S1", "S2"]
regions = ["circle[[13h48m52.50s, 26d35m34.18s], 5arcsec]",
           "circle[[13h48m45.45s, 26d35m24.61s], 5arcsec]",
           "circle[[13h48m59.07s, 26d33m36.00s], 5arcsec]"]

check_point_flux(datasets, regions, labels)
```

![flux_comparison.png](A1795%20Minihalo/flux_comparison.png)