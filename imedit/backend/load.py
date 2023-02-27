
from PIL import Image
import numpy as np

# load image into a 2D numpy array for faster performance
def loadtonumpy(filepath):
    image = Image.open(filepath)
    array = np.array(image)
    return array


# save an image to a filepath from a 2D numpy array (uint8)
def savefromnumpy(array, filepath):
    image = Image.fromarray(array)
    image.save(filepath)
