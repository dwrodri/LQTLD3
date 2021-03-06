import numpy
import sys
import png

# TODO: figure out argparse

# CELL SPEC: [[0, 0, 'G', sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize]]
#              ^  ^   ^        ^            ^            ^            ^
#        address  |   |        |            |            |            |
#        generation   |        |            |            |            |
#                 color        |            |            |            |
#             east neighbor diff            |            |            |
#                         north neighbor diff            |            |
#                                       west neighbor diff            |
#                                                   south neighbor diff


def qlao(code, tx, ty, direction) -> int:
    """
    This is the circled plus operator from the paper. QLAO stands for quad location addition operator

    :param code: address of cell
    :param tx: constant mask for filtering x bits
    :param ty: constant mask for filtering y bits
    :param direction: direction vector in interleaved binary format
    :return: the calculated neighbor address
    """
    return (((code | ty) + (direction & tx)) & tx) | (((code | tx) + (direction & ty)) & ty)


class LinearQuadTree:

    def __init__(self, value_matrix: numpy.array, filename=None):
        """

        :param value_matrix: 2-D binary data to be compressed into a tree
        :param filename: optional filename for loading a quadtree from memory
        """
        self.vmatrix = value_matrix
        self.dims = self.vmatrix.shape
        # check matrix meets specs
        if self.dims[0] & (self.dims[0] - 1) != 0 or len(set(self.dims)) != 1:
            self.pad()
        self.r = int(numpy.math.log2(self.vmatrix.shape[0]))
        if filename is None:
            print('Generating new quadtree...')
            self.tree = []
            self.populate_tree()
        else:
            print('Loading quadtree from file')

    def pad(self) -> None:
        """
        Pads value matrix with zeros so that address calculations work smoothly.
        """
        new_dim = 2 ** (int(numpy.math.log2(max(self.dims))) + 1)
        adjustments = list(map(lambda x: new_dim - x, self.dims))
        self.vmatrix = numpy.pad(self.vmatrix,
                                 ((0, adjustments[0]), (0, adjustments[1])),
                                 'constant',
                                 constant_values=(1, 1))

    def write_tree_to_file(self) -> None:
        """
        Caches tree to raw text file so that it doesn't have to be rendered again
        """
        pass

    def populate_tree(self) -> None:
        """
        populate the linear quad tree with cells that track level differences.
        """
        self.tree = [[0, 0, 'G', sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize]]
        while list(filter(lambda x: x[2] == 'G', self.tree)):  # while includes GRAY areas do
            for i in range(len(self.tree)):
                if self.tree[i][2] == 'G':  # find first gray node
                    self.update_neighbors(self.tree[i])  # neighbors of first GRAY node incremented
                    break

            target_node = self.tree.pop(i)  # pop gray node off tree
            if target_node[1] < self.r:
                children = self.divide(target_node)

                for child in children:
                    self.update_neighbors(child)
                self.tree.extend(children)  # add new kids since they were out of the list

    def update_neighbors(self, cell: list) -> None:
        """
        Helper method that updates all neighbors of newly formed child cell.

        :param cell: child cell produced by `divide()` function call
        """
        directions = [int('01', 2), int('10', 2), int('01' * self.r, 2),
                      int('10' * self.r, 2)]  # east, north, west, south
        neighbor_codes = []
        directions = list(map(lambda x: x << (2 * (self.r - cell[1])), directions))
        for i in range(4):
            if cell[3 + i] == sys.maxsize:  # if neighbor is known wall, make no changes to any LD value
                neighbor_codes.append(sys.maxsize)
            else:
                neighbor_codes.append(qlao(cell[0], int('01' * self.r, 2), int('10' * self.r, 2),
                                           directions[i]))  # this is theorem 1 from paper
                neighbor = next((x for x in self.tree if x[0] == neighbor_codes[i]), None)
                if neighbor is not None and neighbor[1] == cell[1]:
                    neighbor[3 + ((2 + i) % 4)] += 1

    def divide(self, cell: list) -> list:
        """
        Helper function that splits a gray cell into four more gray cells.

        :param cell: cell that needs to be divided
        :return: list of children cells to be pushed onto the tree
        """
        for i in range(4):
            if cell[3 + i] != sys.maxsize:
                cell[3 + i] -= 1
        generations = [cell[1] + 1] * 4
        new_code_bits = list(map(lambda x: x << (2 * (self.r - generations[x])), range(4)))
        codes = list(map(lambda x: cell[0] | x, new_code_bits))
        colors = list(map(lambda x: self.assign_color(codes[x], generations[x]), range(4)))  # get color of cells
        east_levels = [0, cell[3], 0, cell[3]]  # east levels go to SE and NE corners
        north_levels = [0, 0, cell[4], cell[4]]  # north levels go NE and NW corners
        west_levels = [cell[5], 0, cell[5], 0]  # west levels go to SW and SW corners
        south_levels = [cell[6], cell[6], 0, 0]  # south levels go to SW and SE corners
        return list(map(lambda x: list(x),
                        zip(codes,
                            generations,
                            colors,
                            east_levels,
                            north_levels,
                            west_levels,
                            south_levels)))  # zip and convert kids to lists

    def assign_color(self, code: int, gen: int) -> str:
        """
        Fetches color of cell to assign color code upon creation.
        
        :param code: binary address of cell
        :param gen: generation of cell
        :return: 'W" = white, 'G' = gray, or 'B' = black 
        """
        cell_row, cell_col = self.code_to_pixel(code)
        cell_width = cell_height = len(self.vmatrix) >> gen
        score = numpy.sum(self.vmatrix[cell_row:cell_row+cell_height, cell_col:cell_col+cell_width])
        if score == 0:
            return 'B'
        elif score == cell_width*cell_height:
            return 'W'
        else:
            return 'G'

    def code_to_pixel(self, code: int) -> list:
        """

        :param code: binary add
        :return:
        """
        row_bits = int(bin(code)[2:].zfill(2 * self.r)[::2], 2)
        col_bits = int(bin(code)[2:].zfill(2 * self.r)[1::2], 2)
        return [row_bits, col_bits]

    # TODO: rewrite to remove the level_dif_index parameter, it's confusing
    def get_neighbor(self, cell: list, level_dif_index: int, direction: int) -> int:
        """
        Get neighbor code in given direction. This is straight from the Aizawa & Tanaka paper.
        See paper about shortcomings of this algorithm.

        :param cell: cell whose neighbor we want
        :param level_dif_index: index in cell of the level dif we want
        :param direction: direction vector to apply to the code
        :return: location code of neighbor
        """
        dd = cell[level_dif_index]  # this is the level differential
        if dd != sys.maxsize:  # if the direction requested is not facing wall
            n_q, l = cell[:2]  # n_q is the neighbor code, l is level
            shift = 2 * (self.r - l - dd)  # compensate for level differences
            tx = int('01' * self.r, 2)  # generate masks for QLAO
            ty = int('10' * self.r, 2)
            if dd < 0:  # if neighbor is higher up in tree
                return qlao((n_q >> shift << shift), tx, ty, (direction << shift))
            else:  # if neighbor is further down or at same level...
                return qlao(cell[0], tx, ty, direction << (2 * (self.r - l)))

    def generate_debug_png(self, filename: str):
        """
        debugger function that uses PyPNG to render an RGB image of the vmatrix

        :param filename: string used as filename for output_PNG
        """
        output_file = open(filename, 'wb')
        writer = png.Writer(2**self.r, 2**self.r)
        pixel_matrix = []
        for row in range(2**self.r):
            pixel_matrix.append([])
            for col in range(2**self.r):
                if self.vmatrix[row][col] == 0:
                    pixel_matrix[row].extend([0, 0, 0])
                elif self.vmatrix[row][col] == 1:
                    pixel_matrix[row].extend([255, 255, 255])
                else:
                    b = self.vmatrix[row][col] & 255 # apparently this is slaughtering performance
                    g = (self.vmatrix[row][col] >> 8) & 255
                    r = (self.vmatrix[row][col] >> 16) & 255
                    pixel_matrix[row].extend([r, g, b])
        writer.write(output_file, pixel_matrix)

    def color_cell(self, cell_index, color) -> None:
        """
        Draws a bounding box around the inside of the cell in the tree.
        Currently only used as a helper function for *draw_all_usable_cells()*

        :param cell_index: index in self.tree of the cell
        :param color: color of the boundary line
        """
        cell = self.tree[cell_index]
        cell_row, cell_col = self.code_to_pixel(cell[0])  # get corner of cell
        for i in range(len(self.vmatrix) >> cell[1]):
            for j in range(len(self.vmatrix[0]) >> cell[1]):
                if i == 0 or j == 0 or i == (len(self.vmatrix) >> cell[1]) - 1 or j == (
                        len(self.vmatrix[0]) >> cell[1]) - 1:
                    self.vmatrix[cell_row + i][cell_col + j] = color

    def draw_all_usable_cells(self):
        """
        edits the occupancy_matrix to draw in the edges of the cells
        """
        for i in range(len(self.tree)):
            if self.tree[i][2] != 'B' and self.tree[i][1] < (self.r - 1):
                self.color_cell(i, int('0xe74cff', 16))




