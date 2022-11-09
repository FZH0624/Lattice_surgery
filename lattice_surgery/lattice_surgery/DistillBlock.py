import copy

from lattice_surgery.Grid import Grid
from lattice_surgery.Patch import *
import math


class DistillBlock(Grid):

    def __init__(self, config, params):
        super().__init__(config, params)
        # Easy implementation is fixed. But can be modified by replacing the magic state distillation protocol
        self.size = (5, 3)
        data_block_size = (2 * math.ceil(len(self.params.circuit.information.qubits) / 2), 4)
        self.bias = data_block_size[0]
        self.out_axis = (data_block_size[0] + 0, 1)
        self.state = False

    def initialization(self):

        # fixed protocol:
        self.config['1'] = Patch(name='1', axis=[(self.bias + 2, 2)], info='+', reverse=True)
        self.config['2'] = Patch(name='2', axis=[(self.bias + 2, 0)], info='+', reverse=True)
        self.config['3'] = Patch(name='3', axis=[(self.bias + 1, 2)], info='+', reverse=True)
        self.config['4'] = Patch(name='4', axis=[(self.bias + 1, 0)], info='+', reverse=True)
        self.config['5'] = Patch(name='5', axis=[(self.bias + 0, 1)], info='+')

    def prepare(self):

        # step1: state injection to prepare 5 initial patch
        result = self.state_injection(['1', '2', '3', '4'])

        # step2: perform multi-Z-rotation (idea from arXiv:1808.02892v3 Sec3.1)
        # 1:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['3', '4', '5']))
        # 2:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['2', '4', '5']))
        # 3:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['2', '3', '5']))
        # 4:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['2', '3', '4']))
        # 5:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '4', '5']))
        # 6:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '3', '5']))
        # 7:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '3', '4']))
        # 8:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '2', '5']))
        # 9:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '2', '4']))
        # 10:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '2', '3']))
        # 11:
        result.extend(self.pre_anci())
        result.extend(self.multi_non_clifford_Z_rotation(['1', '2', '3', '4', '5']))

        # step 3: X-measurement of 1, 2, 3, 4
        self.measure_patch('1')
        self.measure_patch('2')
        self.measure_patch('3')
        self.measure_patch('4')
        result.append(copy.deepcopy(self.config))

        return result

    def multi_non_clifford_Z_rotation(self, name_list, anci_m='m', anci_0='0', anci='anci'):

        # This function defines a way to implement multi-qubits Z rotations of pi/8
        # input params:
        #  -anci_m: name of previous round distill output
        #  -anci_0: name of initial 0 state prepared for Y-basis measurement
        #  -anci  : name of ancillary qubits to perform multi qubits Z-measurement.
        result = []
        info_list = []
        if isinstance(name_list, list):
            for name in name_list:
                info_list.append(self.merge(anci, name))
        else:
            info_list.append(self.merge(anci, name_list))
        info1 = self.merge(anci_m, anci)
        info2 = self.merge(anci_m, anci_0)

        result.append(copy.deepcopy(self.config))

        if isinstance(name_list, list):
            for i in range(len(name_list)):
                self.split(anci, name_list[i], info_list[i])
        else:
            self.split(anci, name_list, info_list[0])
        self.split(anci_m, anci, info1)
        self.split(anci_m, anci_0, info2)
        self.measure_patch(anci)
        self.measure_patch(anci_m)
        self.measure_patch(anci_0)

        result.append(copy.deepcopy(self.config))
        return result

    def state_injection(self, name_list, info='t'):

        if isinstance(name_list, list):
            for name in name_list:
                self.config[name].info = info
        else:
            # may be a string
            self.config[name_list].info = info

        return [copy.deepcopy(self.config)]

    def pre_anci(self):

        self.add_new_patch(name='m', axis=[(self.bias + 3, 2)])
        self.state_injection(name_list='m')
        self.add_new_patch(name='0', axis=[(self.bias + 4, 2)])
        self.add_new_patch(name='anci', axis=[(self.bias + 1, 1)])
        self.extend_one_position('m', (self.bias + 3, 1))
        sqr = Square((self.bias + 4, 2))
        self.turn_around('0', edge=sqr.down)
        self.extend_one_position('anci', (self.bias + 2, 1))

        return [copy.deepcopy(self.config)]
