from png import Reader
from quadtrees import trees
import numpy
import itertools

def test_png_file(filename:str) -> None:
    reader = Reader(filename)
    pngdata = reader.read() #extract file
    matrix = numpy.array([[y/255 for y in x] for x in list(pngdata[2])])[:, ::3]  # load into numpy array
    lqtld = trees.LinearQuadTree(value_matrix=matrix)
    lqtld.draw_all_usable_cells()
    lqtld.generate_debug_png('../debug.png')

def test_np_array() -> None:
    pass

if __name__ == '__main__':
    test_png_file('../test_pngs/mini2.png')