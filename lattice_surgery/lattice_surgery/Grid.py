from lattice_surgery.Patch import *


class Grid:
    '''
    Grid: for the higher level overview of each block.

    ------

    Parameters:

    ->qbits(list of str): A logical qubits list in this grid.
    '''

    def __init__(self, config):

        # Easy implementation in doi:10.1088/1367-2630/14/12/123011

        self.config = config
        self.size = (2 * math.ceil(len(self.config.keys()) / 2), 4)
        self.avail_list = []
        # self.initialization()

    def initialization(self):

        n = len(self.config.keys())
        # self.size = (2 * math.ceil(n/2), 4)

        # available qbit list in the grid
        for j in range(2):
            for i in range(math.ceil(n / 2)):
                self.avail_list.append((2 * i, 2 * j))

        for qbit in self.config.keys():
            axis = [self.avail_list.pop(0)]
            pat = Patch(qbit, axis)
            self.config[qbit] = pat

    def simulation(self, ins):

        gate_typ = ins[0]
        op1 = ins[1]
        if len(ins) > 2:
            op2 = ins[2]

        if gate_typ == 'H':
            result = self.sim_H(op1)

        elif gate_typ == 'CZ':
            print('CZ')

        elif gate_typ == 'CNOT':
            result = self.sim_CNOT(op1, op2)

        elif gate_typ == 'S':
            print('S')

        elif gate_typ == 'T':
            print('T')

        else:
            print('not')

        return result

    def sim_H(self, op):

        self.config[op].switch_border()

        return [copy.deepcopy(self.config)]

    def sim_CNOT(self, op1, op2):

        # First: check if op1 and op2 are in right rotation.
        #        if not run rotation....
        # Second: move op2 to op1's up right one and initial the ancila qubit
        # Third: Merge op1 and ancila
        # Forth: Split op1 and ancila
        # Fifth: Merge op2 and ancila
        # Sixth: Measure the ancila
        # Seventh: Move back to the op2 original place

        patch1 = self.config[op1]
        patch2 = self.config[op2]
        result = []

        # step1: 3 cycle
        if not patch1.is_right_rotation():
            r1 = self.rotation(op1)
            result.extend(r1)

        if not patch2.is_right_rotation():
            r2 = self.rotation(op2)
            result.extend(r2)

        # step2: 1 cycle
        path = self.get_CNOT_path(op1, op2)
        self.move_by_path(op2, path)
        result.append(copy.deepcopy(self.config))

        return result

    def rotation(self, name: str) -> list:

        pat = self.config[name]
        i, j = pat.axis[0]
        sqr1 = Square((i, j))
        result = []

        if len(pat.axis) == 1:
            pat.axis.append((i, j + 1))
            pat.get_border()
            sqr2 = Square((i, j + 1))

            a = pat.border_map[sqr1.down]

            # step1
            for edge in pat.border:

                if equal(edge, sqr2.left) or equal(edge, sqr2.up):
                    pat.border_map[edge] = pat.border_map[sqr1.left]

                if equal(edge, sqr2.right):
                    pat.border_map[edge] = pat.border_map[sqr1.down]

            result.append(copy.deepcopy(self.config))

            # step2
            for edge in pat.border:

                if equal(edge, sqr1.left) or equal(edge, sqr2.left):
                    pat.border_map[edge] = pat.border_map[sqr1.down]

            result.append(copy.deepcopy(self.config))

            # step3
            pat.axis.pop()
            pat.get_border()
            pat.border_map[sqr1.up] = 1 - a
            pat.border_map[sqr1.down] = 1 - a
            pat.border_map[sqr1.left] = a
            pat.border_map[sqr1.right] = a

            result.append(copy.deepcopy(self.config))
            return result

    def extend_one_position(self, name: str, axis: tuple):

        pat = self.config[name]
        i0, j0 = pat.axis[-1]
        i1, j1 = axis
        sqr1 = Square((i0, j0))
        sqr2 = Square((i1, j1))
        try:
            h = pat.border_map[sqr1.left]
        except KeyError:
            h = pat.border_map[sqr1.right]
        try:
            v = pat.border_map[sqr1.up]
        except KeyError:
            v = pat.border_map[sqr1.down]

        # case1: vertical move
        if j0 != j1 and i0 == i1:

            if j1 >= j0:
                interval = +1
            else:
                interval = -1

            for j in range(j0, j1, interval):
                pat.axis.append((i0, j + interval))
                sqr = Square((i0, j + interval))
                pat.get_border()

                for edge in pat.border:
                    if edge_in_square(edge, sqr):
                        if equal(edge, sqr.left) or equal(edge, sqr.right):
                            pat.border_map[edge] = h
                        else:
                            pat.border_map[edge] = v

        elif i0 != i1 and j0 == j1:

            if i1 >= i0:
                interval = +1
            else:
                interval = -1

            for i in range(i0, i1, interval):
                pat.axis.append((i + interval, j0))
                sqr = Square((i + interval, j0))
                pat.get_border()

                for edge in pat.border:
                    if edge_in_square(edge, sqr):
                        if equal(edge, sqr.left) or equal(edge, sqr.right):
                            pat.border_map[edge] = h
                        else:
                            pat.border_map[edge] = v

    def move_by_path(self, name: str, path):

        # path example: [(i1, j1), (i2, j2), ... , (in, jn)]
        # means that the patch moving from (i0, j0) -> (i1, j1) -> (i2, j2) -> ...  -> (in, jn)
        # constrain: the two nodes in the path must have one position in common, either i1 = i2 or j1 = j2.

        for node in path:
            self.extend_one_position(name, node)

        # unextend by measure
        pat = self.config[name]
        pat.axis = [path[-1]]
        sqr = Square(pat.axis[-1])
        pat.get_border()

        try:
            h = pat.border_map[sqr.left]
        except KeyError:
            h = pat.border_map[sqr.right]
        try:
            v = pat.border_map[sqr.up]
        except KeyError:
            v = pat.border_map[sqr.down]

        for edge in pat.border:
            if equal(edge, sqr.left) or equal(edge, sqr.right):
                pat.border_map[edge] = h
            else:
                pat.border_map[edge] = v

    def get_CNOT_path(self, op1, op2) -> list:

        # op1: ctrl qbit, op2: targ qbit
        patch1 = self.config[op1]
        patch2 = self.config[op2]

        i1, j1 = patch1.axis[-1]
        i2, j2 = patch2.axis[-1]

        # The move will be op2 to op1's up right place
        # There are three cases in our CNOT move standard
        # The first case: op1 and op2 are in the same row.
        if j1 == j2:
            # first up and move to right position
            return [(i2, j2 + 1), (i1 + 1, j1 + 1)]

        else:
            # The second case: op1 is in the upper row, op2 is in the lower row
            if j2 < j1:
                # this is because there is a qbit in (i2, j1)
                return [(i2 + 1, j2), (i2 + 1, j1 + 1), (i1 + 1, j1 + 1)]
            else:
                return [(i2, j2 - 1), (i1 + 1, j1 + 1)]

    def visualization(self):

        delta = 0.1
        figure, _ = plt.subplots()
        plt.xlim([-0.4, self.size[0]])
        plt.ylim([-0.4, self.size[1]])
        ax = plt.gca()

        for name in self.config.keys():

            patch = self.config[name]
            for item in patch.figure_params():
                ax.add_patch(item)

            for edge in patch.border:

                if patch.border_map[edge]:
                    mark = '-'
                else:
                    mark = '--'
                plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], mark, color='black')

        ax.set_aspect('equal', adjustable='box')
        plt.grid('True')
        plt.show()
