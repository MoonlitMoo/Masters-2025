import numpy as np

img_name = "minihalo_r=1.5_ssb=0.image.tt0"
MINIHALO_MASK = "../minihalo.mask"
OUTPUT_DIR = "flux_images"

ia.open(MINIHALO_MASK)
mpix=ia.getchunk().astype(bool)
ia.done()

os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_flux(image: str, out_file: str = None):
    # Load the image
    ia.open(img_name)
    pix = ia.getchunk()
    ia.close()

    # Get sigma and flux
    res = imstat(img_name)
    sigma = res["sigma"]

    # Apply masks to minihalo
    pix[~mpix] = 0.
    pix[pix < 3 * sigma] = 0.

    # Save minihalo flux image
    if out_file is not None:
        output_image = f'{OUTPUT_DIR}/{out_file}'
        if os.path.exists(output_image):
            os.system(f'rm -r {output_image}')
        os.system(f'cp -r {image} {output_image}')
        # Save minihalo flux
        ia.open(output_image)
        ia.putchunk(pix)
        ia.close()

    tot = np.sum(pix)

    return tot, sigma

t, s = get_flux(img_name, img_name)
print(f"Image std: {s}")
print(f"Minihalo flux: {t} Jy")
