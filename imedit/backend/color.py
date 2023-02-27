
import numpy as np
from numba import jit
from PIL import Image

# numba makes first convert slow but all others faster

@jit(nopython=True)
def convertpixeltograyscale(array, x, y):
	pixelval = np.sum(array[y, x, 0:3])/3
	# print(np.array([pixelval, pixelval, pixelval, array[y, x, 3]]))
	return np.array([pixelval, pixelval, pixelval, 255])

@jit(nopython=True)
def adjustcolor(array, x, y, coloradjustment):
	return np.add(array[y, x], coloradjustment)

def getthumbnail(imgarray):
	thumb = Image.fromarray(imgarray)
	thumb.thumbnail((64, thumb.height * (64/thumb.width)),Image.Resampling.LANCZOS)
	thumbarray = np.array(thumb)
	return thumbarray


@jit(nopython=True)
def converttograyscale(array):
	grayscalearray = np.zeros((array.shape[0], array.shape[1], 4))

    # loop over each pixel in the original image
    # and store the calculated pixel in the new array
	for y in range(len(array)):
		for x in range(len(array[0])):
			grayscalearray[y, x] = convertpixeltograyscale(array, x, y)

	grayscalearray = grayscalearray.astype('uint8')

	return grayscalearray

@jit(nopython=True)
def shiftcolor(array, coloradjustment):
	shiftcolorarray = np.zeros(array.shape)

    # loop over each pixel in the original image
    # and store the calculated pixel in the new array
	for y in range(len(array)):
		for x in range(len(array[0])):
			shiftcolorarray[y, x] = adjustcolor(array, x, y, coloradjustment)

	shiftcolorarray = shiftcolorarray.astype('uint8')

	return shiftcolorarray
