from lattice_surgery.Patch import *


class DataBlock:
    '''
    Grid: for the higher level overview of each block.

    ------

    Attribute:

    ->qbits(list of str): A logical qubits list in this grid.
    '''

    def __init__(self, config):

        # Easy implementation in doi:10.1088/1367-2630/14/12/123011

        self.config = config
        # have some bug, when adding ancila, the size will change.
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
        origin_pos = patch2.axis[-1]
        self.move_by_path(op2, path)
        result.append(copy.deepcopy(self.config))

        # step3: total 5 cycle: 1 for new patch, 2 for 2 merge, 2 for 2 split.
        self.add_new_patch(name='A_CNOT', axis=[(patch1.axis[-1][0], patch1.axis[-1][1] + 1)], info='+')
        result.append(copy.deepcopy(self.config))
        info = self.merge(op1, 'A_CNOT')
        result.append(copy.deepcopy(self.config))
        self.split(op1, 'A_CNOT', info)
        result.append(copy.deepcopy(self.config))
        info = self.merge('A_CNOT', op2)
        result.append(copy.deepcopy(self.config))
        self.split('A_CNOT', op2, info)
        result.append(copy.deepcopy(self.config))
        self.measure_patch('A_CNOT')
        result.append(copy.deepcopy(self.config))

        # step4: 1 cycle
        path.reverse()
        path.pop(0)
        path.append(origin_pos)
        self.move_by_path(op2, path)
        result.append(copy.deepcopy(self.config))

        return result

    def sim_Phase(self, op1):

        # First: check if op1 is in upper row or in lower row(classical) and check op1 if op1 is in right rotation
        # Second: move the upper qubit in the same vertical position of op1
        # Third: initial \ket{0} and extend the border in order to perform Y-basis
        # Forth: initial ancila qubit between \ket{0} and op1
        # Fifth: Merge and measure
        # Sixth: measure \ket{0} register

        # case1: op1 is in the lower row
        result = []
        pat = self.config[op1]
        if pat.axis[-1][1] == 0:

            # step1: 1 cycle
            name = self.search_name_by_axis((pat.axis[-1][0], pat.axis[-1][1] + 2))
            origin_axis = self.config[name].axis[-1]
            self.move_by_path(name, [(self.config[name].axis[-1][0], self.config[name].axis[-1][1] + 1)])
            result.append(copy.deepcopy(self.config))

            # step2: 3 cycle
            if not self.config[op1].is_right_rotation():
                result.extend(self.rotation(op1))

            # step3: 1 cycle
            # prepare the Y-basis measurement
            self.add_new_patch(name='anci_1', axis=[origin_axis], info='0')
            self.config['anci_1'].axis.append((origin_axis[0] + 1, origin_axis[1]))
            self.config['anci_1'].get_border()
            sqr1 = Square(origin_axis)
            sqr2 = Square((origin_axis[0] + 1, origin_axis[1]))
            for edge in self.config['anci_1'].border:
                if equal(edge, sqr2.down):
                    self.config['anci_1'].border_map[edge] = self.config['anci_1'].border_map[sqr1.left]
                if equal(edge, sqr2.up) or equal(edge, sqr2.right):
                    self.config['anci_1'].border_map[edge] = self.config['anci_1'].border_map[sqr1.up]
            result.append(copy.deepcopy(self.config))

            # step4: 1 cycle
            # prepare the ancilary measure qubit
            self.add_new_patch(name='anci_2', axis=[(origin_axis[0], origin_axis[1] - 1)], info='0')
            self.config['anci_2'].axis.append((origin_axis[0] + 1, origin_axis[1] - 1))
            self.config['anci_2'].get_border()
            sqr1 = Square((origin_axis[0], origin_axis[1] - 1))
            sqr2 = Square((origin_axis[0] + 1, origin_axis[1] - 1))
            for edge in self.config['anci_2'].border:
                if equal(edge, sqr2.right):
                    self.config['anci_2'].border_map[edge] = self.config['anci_2'].border_map[sqr1.left]
                if equal(edge, sqr2.up) or equal(edge, sqr2.down):
                    self.config['anci_2'].border_map[edge] = self.config['anci_2'].border_map[sqr1.up]
            result.append(copy.deepcopy(self.config))

            # step5: 1 cycle
            info1 = self.merge(op1, 'anci_2')
            info2 = self.merge('anci_2', 'anci_1')
            result.append(copy.deepcopy(self.config))

            # step6: 1 cycle
            # actually is doing Pauli measurement in this stage
            self.split(op1, 'anci_2', info1)
            self.split('anci_2', 'anci_1', info2)
            self.measure_patch('anci_2')
            result.append(copy.deepcopy(self.config))

            # step7:
            self.measure_patch('anci_1')
            result.append(copy.deepcopy(self.config))

            # step8:
            self.move_by_path(name, [origin_axis])
            result.append(copy.deepcopy(self.config))
        return result

    def add_new_patch(self, name, axis, info='0'):

        self.config[name] = Patch(name=name, axis=axis, info=info)

    def measure_patch(self, name):

        del self.config[name]

    def merge(self, op1, op2) -> list:

        info_before_merge = [{}, {}]
        for edge1 in self.config[op1].border:
            for edge2 in self.config[op2].border:
                if equal(edge1, edge2):
                    border1 = self.config[op1].border_map[edge1]
                    border2 = self.config[op2].border_map[edge2]
                    self.config[op1].border_map[edge1] = 'M'
                    self.config[op2].border_map[edge2] = 'M'
                    info_before_merge[0][edge1] = border1
                    info_before_merge[1][edge2] = border2

        return info_before_merge

    def split(self, op1, op2, info_before_merge=None):

        for edge1 in self.config[op1].border:
            if self.config[op1].border_map[edge1] == 'M':
                for edge2 in self.config[op2].border:
                    if self.config[op2].border_map[edge2] == 'M' and equal(edge1, edge2):
                        if info_before_merge:
                            self.config[op1].border_map[edge1] = info_before_merge[0][edge1]
                            self.config[op2].border_map[edge2] = info_before_merge[1][edge2]
                        else:
                            # default: 1
                            self.config[op1].border_map[edge1] = 1
                            self.config[op2].border_map[edge2] = 1

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

    def new_rotation(self, name: str) -> list:

        pass

    def extend_one_position(self, name: str, axis: tuple):

        pat = self.config[name]
        i0, j0 = pat.axis[-1]
        i1, j1 = axis
        sqr1 = Square((i0, j0))
        # sqr2 = Square((i1, j1))
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

    def search_name_by_axis(self, axis):

        for name in self.config.keys():
            if self.config[name].axis[-1] == axis:
                return name

        return None

    def turn_around(self, name, edge, typ='outside', position='clockwise'):

        # judge if edge is in "name" Patch
        pat = self.config[name]
        ind = 0
        for i in range(len(pat.border)):
            if edge == pat.border[i]:
                ind = i
                break

        if typ == 'outside':
            p0 = edge[0]
            p1 = edge[1]

            turning_edge_typ = pat.border_map[edge]
            if position == 'clockwise':
                extending_edge = pat.border[ind + 1]
                sign = +1
            elif position == 'anticlockwise':
                extending_edge = pat.border[ind - 1]
                sign = -1
            else:
                extending_edge = None
                sign = None
            extending_edge_typ = pat.border_map[extending_edge]
            p2 = (p0[0] + sign * (p1[1] + p0[1]), p0[1] - sign * (p1[0] - p0[0]))
            p3 = (p1[0] + p2[0] - p0[0], p1[1] + p2[1] - p0[1])
            # For easy, we convert to int, but may cause future error!!!
            new_axis = (int(0.25*(p0[0] + p1[0] + p2[0] + p3[0]) - 0.5), int(0.25*(p0[1] + p1[1] + p2[1] + p3[1]) - 0.5))
            pat.axis.append(new_axis)
            pat.get_border()
            sqr = Square(new_axis)
            for e in pat.border:
                if edge_in_square(e, sqr):
                    if equal(e, (p0, p2)):
                        pat.border_map[e] = turning_edge_typ
                    else:
                        pat.border_map[e] = extending_edge_typ

        elif typ == 'inside':
            turning_edge_typ = pat.border_map[edge]
            for i in range(len(pat.axis)):
                axis = pat.axis[i]
                sqr = Square(axis)
                if edge_in_square(edge, sqr):
                    pat.axis.pop(i)
            pat.get_border()
            for e in pat.border:
                if e not in pat.border_map.keys():
                    pat.border_map[e] = turning_edge_typ

        else:
            return NotImplemented

    def move_corner(self, name, src, dst, position='anticlockwise'):

        pat = self.config[name]
        i = pat.border.index(src)
        j = pat.border.index(dst)
        n = len(pat.border)
        t = i

        if position == 'anticlockwise':
            sign = +1
        elif position == 'clockwise':
            sign = -1
        else:
            sign = None

        while t != j:
            t = (t + sign) % n
            pat.border_map[pat.border[t]] = pat.border_map[src]