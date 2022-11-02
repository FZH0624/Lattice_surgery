from collections import namedtuple
from datetime import timedelta
import math
import numbers
import copy
from matplotlib import pyplot as plt, patches


class Square:
    '''
    Square class: define some proper corresponding with the topology of Patches.
    '''

    def __init__(self, axis):
        self.axis = axis
        i, j = axis
        self.left = ((i, j + 1), (i, j))
        self.right = ((i + 1, j), (i + 1, j + 1))
        self.up = ((i + 1, j + 1), (i, j + 1))
        self.down = ((i, j), (i + 1, j))
        self.edges = [self.down, self.right, self.up, self.left]


def equal(e1, e2):
    # judge if e1 and e2 is equal edge.
    p1 = e1[0]
    p2 = e1[1]

    return p1 in e2 and p2 in e2


def edge_in_square(e, sqr: Square):
    return equal(e, sqr.right) or equal(e, sqr.left) or equal(e, sqr.up) or equal(e, sqr.down)


class Patch:
    '''

    Patch: information in each cell.

    ------

    Attribute:

    ->name(str): Qbit name of this patch.
    eg: p1.name = 'Q1'

    ->axis(list): which area are this patch occuiped in the grid.
    eg: axis = [(0, 0)] means this patch is in the left bottom of the grid.
        axis = [(0, 0), (0, 1), (1, 0)] will declare an "L" shaped patch.

    ->border(list): Contains the border(edge connecting two points) of this patch. Before and after the simulation of instructions,
    this will be set to len 1.
    eg: p1 = Patch([(0, 0),(0, 1)])
        p1.border =
                 [((0, 0), (1, 0)),
                  ((1, 0), (1, 1)),
                  ((0, 1), (0, 0)),
                  ((1, 1), (1, 2)),
                  ((1, 2), (0, 2)),
                  ((0, 2), (0, 1))]

    ->border_map(dict): Contains the type of each border of this patch. 0 for 'Z' type, 1 for 'X' type.
    eg: p1.border_map =
                        {((0, 0), (1, 0)): 1,
                         ((1, 0), (1, 1)): 0,
                         ((0, 1), (0, 0)): 0,
                         ((1, 1), (1, 2)): 0,
                         ((1, 2), (0, 2)): 1,
                         ((0, 2), (0, 1)): 0}

    ------

    Method:


    '''

    def __init__(self, name, axis):

        self.axis = axis
        self.name = name
        self.info = None
        self.border = []
        self.border_map = {}
        self.init()

    def add_edge(self, e):

        p1 = e[0]
        p2 = e[1]
        flag = None

        for i in range(len(self.border)):

            if p1 in self.border[i] and p2 in self.border[i]:
                flag = i

        if not flag:
            self.border.append((p1, p2))
        else:
            self.border.pop(flag)

    def get_border(self):

        self.border = []

        for axis in self.axis:
            sqr = Square(axis)

            self.add_edge(sqr.left)
            self.add_edge(sqr.right)
            self.add_edge(sqr.up)
            self.add_edge(sqr.down)

        del_list = []

        for edge in self.border_map.keys():
            if edge not in self.border:
                del_list.append(edge)

        for edge in del_list:
            del self.border_map[edge]

    def init(self, info='0'):

        # default: every patch initialized by one axis
        self.info = info
        self.get_border()
        sqr = Square(self.axis[-1])
        self.border_map[sqr.up] = 1
        self.border_map[sqr.left] = 0
        self.border_map[sqr.down] = 1
        self.border_map[sqr.right] = 0

    def switch_border(self):

        for edge in self.border_map.keys():
            self.border_map[edge] = 1 - self.border_map[edge]

    def is_right_rotation(self):

        sqr = Square(self.axis[-1])
        u, d, l, r = False, False, False, False

        if len(self.axis) == 1:
            for edge in self.border:
                if equal(edge, sqr.up):
                    u = self.border_map[edge] == 1
                elif equal(edge, sqr.down):
                    d = self.border_map[edge] == 1
                elif equal(edge, sqr.left):
                    l = self.border_map[edge] == 0
                elif equal(edge, sqr.right):
                    r = self.border_map[edge] == 0
                else:
                    return NotImplemented

        return u and d and l and r

    def figure_params(self):

        area = []
        for item in self.axis:
            area.append(patches.Rectangle(item, 1, 1, edgecolor='orange', facecolor='yellow', linewidth=2))

        return area
