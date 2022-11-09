import copy

from lattice_surgery.DataBlock import *
from lattice_surgery.Patch import *
from lattice_surgery.DistillBlock import *


def visual(configuration: [DataBlock, DistillBlock]):

    if configuration[0] and configuration[1]:

        # Partition the whole chip into two block.

        data_block = configuration[0]
        distill_block = configuration[1]
        figure, _ = plt.subplots()

        # draw data block grid

        plt.plot((0, data_block.size[0]), (0, 0), color='red')
        plt.plot((data_block.size[0], data_block.size[0]), (0, data_block.size[1]), color='red')
        plt.plot((data_block.size[0], 0), (data_block.size[1], data_block.size[1]), color='red')
        plt.plot((0, 0), (data_block.size[1], 0), color='red')

        # draw distill block grid

        plt.plot((data_block.size[0], data_block.size[0] + distill_block.size[0]), (0, 0), color='red')
        plt.plot((data_block.size[0] + distill_block.size[0], data_block.size[0] + distill_block.size[0]),
                 (0, distill_block.size[1]), color='red')
        plt.plot((data_block.size[0] + distill_block.size[0], data_block.size[0]),
                 (distill_block.size[1], distill_block.size[1]), color='red')
        plt.plot((data_block.size[0], data_block.size[0]), (distill_block.size[1], data_block.size[0]), color='red')

        # This function is to show the topology looks like in the specific time
        size = (data_block.size[0] + distill_block.size[0], max(data_block.size[1], distill_block.size[1]))
        plt.xlim([-0.4, size[0] + 0.4])
        plt.ylim([-0.4, size[1] + 0.4])
        ax = plt.gca()

        # visual the data block:
        for name in data_block.config.keys():

            patch = data_block.config[name]
            for item in patch.figure_params():
                ax.add_patch(item)

            for edge in patch.border:

                if not patch.border_map[edge]:
                    mark = '--'
                    color = 'black'
                else:
                    if patch.border_map[edge] == 1:
                        mark = '-'
                        color = 'black'
                    else:
                        mark = '-'
                        color = 'blue'
                plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], mark, color=color)

        # visual the distillation block:
        for name in distill_block.config.keys():

            patch = distill_block.config[name]
            for item in patch.figure_params():
                ax.add_patch(item)

            for edge in patch.border:

                if not patch.border_map[edge]:
                    mark = '--'
                    color = 'black'
                else:
                    if patch.border_map[edge] == 1:
                        mark = '-'
                        color = 'black'
                    else:
                        mark = '-'
                        color = 'blue'
                plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], mark, color=color)

        ax.set_aspect('equal', adjustable='box')
        plt.grid('True')
        plt.show()

    else:
        print('Configuration Error!')


class QuantumChip:

    def __init__(self, params):

        self.data_block = None
        self.distill_block = None
        self.time_series = None
        self.params = params
        self.initialization()
        self.configuration = [self.data_block, self.distill_block]

    def initialization(self):

        qbits = self.params.circuit.information.qubits
        data_config = dict()
        distill_config = dict()
        for qbit in qbits:
            data_config[qbit] = None

        # initial distill block qubits dict for easy protocol
        for i in range(5):
            distill_config[f'{i + 1}'] = None

        self.data_block = DataBlock(data_config, self.params)
        self.data_block.initialization()
        self.distill_block = DistillBlock(distill_config, self.params)
        self.distill_block.initialization()

    def prepare_magic_state(self):

        return self.distill_block.prepare()

    def simulation(self):

        instructions = self.params.circuit.instructions
        self.time_series = []
        self.time_series.append([copy.deepcopy(self.data_block), copy.deepcopy(self.distill_block)])
        try:
            num_T = self.params.circuit.information.operations['T']
        except KeyError:
            num_T = 0
        ts_distill_config = []
        ts_data_config = []

        if num_T:
            i_ins = -1
            for i_T in range(num_T):
                ts_distill_config.extend(self.prepare_magic_state())
                pre_time = len(ts_distill_config)
                while i_ins < len(instructions):
                    i_ins = i_ins + 1
                    ins = instructions[i_ins]
                    if ins[0] != 'T':
                        # clifford operation
                        ts_data_config.extend(self.sim_one_ins(ins))
                    else:
                        meet_T_time = len(ts_data_config)
                        if meet_T_time < pre_time:
                            for i in range(pre_time - meet_T_time):
                                ts_data_config.append(copy.deepcopy(self.data_block.config))

                        else:
                            for i in range(meet_T_time - pre_time):
                                ts_distill_config.append(copy.deepcopy(self.distill_block.config))

                        res = self.sim_one_ins(ins)
                        ts_data_config.extend(res)
                        for i in range(len(res)):
                            ts_distill_config.append(copy.deepcopy(self.distill_block.config))
                        break

            for i in range(len(ts_data_config)):
                self.time_series.append([DataBlock(ts_data_config[i], self.params),
                                         DistillBlock(ts_distill_config[i], self.params)])

    #def simulation(self):
#
    #    # sim#ulation of each instruction (just implement the easiest case: no parallel)
    #    instructions = self.params.circuit.instructions
    #    self.time_series = []
    #    self.time_series.append([copy.deepcopy(self.data_block), copy.deepcopy(self.distill_block)])
    ##
    #    for ins in instructions:
#
    #        print(f'Now simulating the instruction:{ins}')
#
    #        data_res = self.sim_one_ins(ins)
    #        for next_config in data_res:
    #            self.time_series.append([DataBlock(next_config, self.params),
    #                                     DistillBlock(self.distill_block.config, self.params)])

    def sim_one_ins(self, ins):

        result = []
        gate_typ = ins[0]
        op1 = ins[1]
        try:
            op2 = ins[2]
        except IndexError:
            op2 = ''

        if gate_typ == 'H':
            result = self.data_block.sim_H(op1)

        elif gate_typ == 'CZ':

            # bad implementation...
            result = self.data_block.sim_H(op2)
            result.extend(self.data_block.sim_CNOT(op1, op2))
            result.extend(self.data_block.sim_H(op2))

        elif gate_typ == 'CNOT':
            result = self.data_block.sim_CNOT(op1, op2)

        elif gate_typ == 'S':
            result = self.data_block.sim_Phase(op1)

        elif gate_typ == 'T':
            result = self.sim_T(op1)

        elif gate_typ == 'M':
            result = self.data_block.sim_M(op1)

        else:
            print('not implement')

        return result

    def sim_T(self, op1):

        # in the easy case: this function is to simulate T-gate
        pat = self.data_block.config[op1]
        result = []

        # step1: judge if the rotation is right for Z_{\pi/8} gate
        if not pat.is_right_rotation(reverse=True):
            result.extend(self.data_block.rotation(op1))

        # step2: doing Z-Z measurement
        i0, j0 = pat.axis[-1]
        i1, j1 = (self.distill_block.out_axis[0], self.distill_block.out_axis[1])

        self.data_block.add_new_patch(name='anci', axis=[(i0, j0 + 1)])
        self.data_block.extend_one_position(name='anci', axis=(i1 - 1, j1))
        result.append(copy.deepcopy(self.data_block.config))

            # merge
        self.merge_between_two_block('anci', '5')
        self.data_block.merge('anci', op1)
        result.append(copy.deepcopy(self.data_block.config))
        return result

    def merge_between_two_block(self, op1, op2) -> list:
        # special case compared to definition in DataBlock,
        # op1 is from data_block, op2 is from distill_block.
        # Consider this function as interact with these two blocks
        info_before_merge = [{}, {}]
        for edge1 in self.data_block.config[op1].border:
            for edge2 in self.distill_block.config[op2].border:
                if equal(edge1, edge2):
                    border1 = self.data_block.config[op1].border_map[edge1]
                    border2 = self.distill_block.config[op2].border_map[edge2]
                    self.data_block.config[op1].border_map[edge1] = 'M'
                    self.distill_block.config[op2].border_map[edge2] = 'M'
                    info_before_merge[0][edge1] = border1
                    info_before_merge[1][edge2] = border2
        return info_before_merge

    def split_between_two_block(self, op1, op2, info_before_merge=None):

        for edge1 in self.data_block.config[op1].border:
            if self.data_block.config[op1].border_map[edge1] == 'M':
                for edge2 in self.distill_block.config[op2].border:
                    if self.distill_block.config[op2].border_map[edge2] == 'M' and equal(edge1, edge2):
                        if info_before_merge:
                            self.data_block.config[op1].border_map[edge1] = info_before_merge[0][edge1]
                            self.distill_block.config[op2].border_map[edge2] = info_before_merge[1][edge2]
                        else:
                            # default: 1
                            self.data_block.config[op1].border_map[edge1] = 1
                            self.distill_block.config[op2].border_map[edge2] = 1

    def visual_all(self):

        for config in self.time_series:
            visual(config)

