
# essential image manipulation functions

def getdimensions(array):
    return len(array[0]), len(array)


def croparray(array, xleft, xright, ytop, ybot):
    newarray = array.copy()
    return newarray[xleft:xright, ytop:ybot], newarray
