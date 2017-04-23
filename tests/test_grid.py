import unittest
from pytest import *
from pykicad.grid import *

class GridTests(unittest.TestCase):

    def setUp(self):
        self.grid = Grid()
        self.insertions = []

    def insert(self, at, value):
        self.grid.place(at, value)
        self.insertions.append((at, value))

        print(self.grid)

        for at, value in self.insertions:
            assert self.grid.get(at) == value


    def test_place(self):
        # origin
        self.insert([0, 0], 0)
        # +x
        self.insert([0, 1], 1)
        self.insert([0, 2], 2)
        self.insert([0, 3], 3)
        # -x
        self.insert([0, -1], -1)
        self.insert([0, -2], -2)
        self.insert([0, -3], -3)
        # +y
        self.insert([1, 0], 10)
        self.insert([2, 0], 20)
        self.insert([3, 0], 30)
        # -y
        self.insert([-1, 0], -10)
        self.insert([-2, 0], -20)
        self.insert([-3, 0], -30)
        # +x +y
        self.insert([2, 2], 99)
        # -x -y
        self.insert([-2, -2], -99)
        # +x -y
        self.insert([2, -2], 100)
        # -x +y
        self.insert([-2, 2], -100)

        self.grid.place([0, 0], 5)
        assert self.grid.get([0, 0]) == 5
        self.grid.place([4, 4], 5)
        assert self.grid.get([4, 4]) == 5
        print(self.grid)
