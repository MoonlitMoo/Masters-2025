import numpy as np
from scipy import ndimage as ndi


def contour_sum(data, level, *, seed=None, pick='largest',
                     connectivity=1, fill_holes=True, valid_mask=None):
    """
    Sum pixels/voxels inside thresholded connected regions.
    Created via ChatGPT.

    Parameters
    ----------
    data : ndarray
        From ia.getchunk() or a numpy array. Can be (ny, nx) or (nz, ny, nx),
        or with extra singleton axes (they'll be squeezed).
    level : float
        Threshold.
    seed : tuple | None
        Index inside the desired region. (y,x) for 2D or (z,y,x) for 3D when pick='seed'.
    pick : {'largest', 'seed', 'all'}
        Selection strategy for components.
    connectivity : {1, 2} for 2D, {1, 2, 3} for 3D
        Neighborhood definition; higher = more connected.
    fill_holes : bool
        Fill internal holes in the binary mask.
    valid_mask : ndarray[bool] | None
        Optional mask (same shape as data before squeeze or broadcastable).

    Returns
    -------
    total : float
        Sum of data inside the selected region(s).
    mask_sel : ndarray[bool]
        Boolean mask (same shape as squeezed data) of selected pixels/voxels.
    info : dict
        {'ndim': 2 or 3, 'n_components': int, 'component_size': int or array, 'level': float}
    """
    a = np.asarray(data)
    a = np.squeeze(a)  # drop Stokes=1, Freq=1 if present
    if valid_mask is None:
        valid_mask = np.isfinite(a)
    else:
        valid_mask = np.squeeze(valid_mask) & np.isfinite(a)

    if a.ndim not in (2, 3):
        raise ValueError(f"Expected 2D or 3D after squeeze, got shape {a.shape} (ndim={a.ndim}).")

    # Threshold
    thr = (a >= level) & valid_mask

    # Optional hole fill
    if fill_holes:
        thr = ndi.binary_fill_holes(thr)

    # Build structure matching array rank
    structure = ndi.generate_binary_structure(a.ndim, connectivity)

    # Label connected components
    labels, nlab = ndi.label(thr, structure=structure)

    # No labels means we return empty
    if nlab == 0:
        z = np.zeros_like(thr, bool)
        return 0.0, z, {'ndim': int(a.ndim), 'n_components': 0, 'component_size': 0, 'level': float(level)}

    # Select components
    if pick == 'all':
        mask_sel = thr
        comp_sizes = np.bincount(labels.ravel())[1:]  # exclude background
    elif pick == 'largest':
        counts = np.bincount(labels.ravel())
        counts[0] = 0  # Ignore background
        lab_id = counts.argmax()
        mask_sel = (labels == lab_id)
        comp_sizes = int(mask_sel.sum())
    elif pick == 'seed':
        if seed is None:
            raise ValueError("pick='seed' requires a seed index: (y,x)")
        lab_id = labels[seed]
        if lab_id == 0:
            z = np.zeros_like(thr, bool)
            return 0.0, z, {'ndim': int(a.ndim), 'n_components': int(nlab), 'component_size': 0, 'level': float(level)}
        mask_sel = (labels == lab_id)
        comp_sizes = int(mask_sel.sum())
    else:
        raise ValueError("pick must be 'largest', 'seed', or 'all'.")

    total = float(a[mask_sel].sum())
    return total, mask_sel, {'ndim': int(a.ndim), 'n_components': int(nlab), 'component_size': comp_sizes, 'level': float(level)}




def get_minihalo_flux_density(image: str, output_image: str, mask: None, cleanup=False):
    """ Gets the minihalo flux density from an image.

    Parameters
    ----------
    image : str
        The image to use (without .image.tt0 suffix)
    output_image : str
        The path to use for the masked image (without .image.tt0 suffix).
    mask : ndarray, default = None
        An optional mask to use instead of calculating the contour.
    cleanup : bool, default=False
        Whether to remove the masked image at the end.

    Returns
    -------
    flux : float
        The flux density of the minihalo
    sigma : float
        The sigma used for the thresholding of the minihalo
    """
    image_file = f"{image}.image.tt0"
    residual_file = f"{image}.residual.tt0"
    output_file = f"{output_image}.image.tt0"

    # Load the image
    ia.open(image_file)
    pix = ia.getchunk()
    ia.close()

    # Get sigma and flux
    res = imstat(residual_file)
    sigma = res["sigma"][0]

    # Get minihalo flux
    if mask is None:
        _, mask, _ = contour_sum(pix, 3*sigma, pick='largest')

    # Save minihalo flux image
    if os.path.exists(output_file):
        os.system(f'rm -r {output_file}')
    os.system(f'cp -r {image_file} {output_file}')

    # Save minihalo flux
    pix[~mask] = 0.
    ia.open(output_file)
    ia.putchunk(pix)
    ia.close()

    # Get the flux density
    res = imstat(output_file)

    if cleanup:
        os.system(f'rm -r {output_file}')

    return res["flux"][0], sigma
