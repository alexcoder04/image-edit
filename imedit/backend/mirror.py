
import numpy as np
from numba import jit # just-in-time-compilation, used to improve performance

# mirrors an image vertically
@jit(nopython=True)
def mirror_vertical(image: np.array) -> np.array:
    # create new array to hold the new image
    new_image = np.zeros((image.shape[0], image.shape[1], 4))
    # iterate over all pixels
    for x in range(len(image[0])):
        for y in range(len(image)):
            # save the pixel data on the corresponding position in the new image (mirrored)
            new_image[y, len(image[0]) - 1 - x] = image[y, x]
    # return in correct data type for PIL to work with
    return new_image.astype("uint8")

# mirrors an image horizontally
# works the same as mirror_vertical
@jit(nopython=True)
def mirror_horizontal(image: np.array) -> np.array:
    new_image = np.zeros((image.shape[0], image.shape[1], 4))
    for x in range(len(image[0])):
        for y in range(len(image)):
            new_image[len(image) - 1 - y, x] = image[y, x]
    return new_image.astype("uint8")
