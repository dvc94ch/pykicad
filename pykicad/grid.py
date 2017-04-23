from pykicad.boundarybox import *


class Grid(object):

    def __init__(self):
        self.grid = [[]]
        self.size = [0, 0]
        self.origin = [0, 0]


    def resize(self, index):
        # Minimum size in positive x y direction
        new_size = [
            max(self.size[0], index[0] + 1),
            max(self.size[1], index[1] + 1)
        ]

        # Compute new origin and increase size in negative x y direction
        new_origin = [self.origin[0], self.origin[1]]
        if index[0] < 0:
            new_origin[0] += abs(index[0])
            new_size[0] += abs(index[0])

        if index[1] < 0:
            new_origin[1] += abs(index[1])
            new_size[1] += abs(index[1])

        # Build new grid
        new_grid = []
        for col in range(new_size[0]):
            columns = []
            for row in range(new_size[1]):
                old_coordinates = [col - new_origin[0], row - new_origin[1]]
                columns.append(self.get(old_coordinates))
            new_grid.append(columns)
        self.origin = new_origin
        self.size = new_size
        self.grid = new_grid


    def place(self, at, module):
        # insertion is relative to origin
        index = [self.origin[0] + at[0], self.origin[1] + at[1]]


        if index[0] < 0 or index[1] < 0:
            # grid to small in negative x, y
            self.resize(index)
            # index needs to be recomputed
            self.place(at, module)
        elif self.size[0] <= index[0] or self.size[1] <= index[1]:
            # grid to small in positive x, y
            self.resize(index)
            # index needs to be recomputed
            self.place(at, module)
        else:
            self.grid[index[0]][index[1]] = module


    def get(self, at):
        index = [self.origin[0] + at[0], self.origin[1] + at[1]]
        return self.get_by_index(index)


    def get_by_index(self, index):
        if index[0] < 0 or index[1] < 0:
            return None
        elif self.size[0] <= index[0] or self.size[1] <= index[1]:
            return None

        return self.grid[index[0]][index[1]]


    def __str__(self):
        string = ''
        for col in reversed(self.grid):
            string += '|'
            for field in col:
                string += ' %5s |' % str(field)
            string += '\n'
        return string
