import copy

from lattice_surgery.DataBlock import *
from lattice_surgery.Patch import *
from lattice_surgery.DistillBlock import *


def visual(configuration: [DataBlock, DistillBlock]):

    if configuration[0] and configuration[1]:
        # This function is to show the topology looks like in the specific time
        data_block = configuration[0]
        distill_block = configuration[1]
        size = (data_block.size[0] + distill_block.size[0], max(data_block.size[1], distill_block.size[1]))
        figure, _ = plt.subplots()
        plt.xlim([-0.4, size[0]])
        plt.ylim([-0.4, size[1]])
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
        disitill_out = (distill_block.output[0] + data_block.size[0], distill_block.output[1])
        ax.add_patch(patches.Rectangle(disitill_out, 1, 1, edgecolor='red', facecolor='purple', linewidth=2))

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
        config = dict()
        for qbit in qbits:
            config[qbit] = None

        self.data_block = DataBlock(config)
        self.data_block.initialization()
        self.distill_block = DistillBlock()

    def simulation(self):

        # simulation of each instruction (just implement the easiest case: no parallel)
        instructions = self.params.circuit.instructions
        self.time_series = []
        self.time_series.append([copy.deepcopy(self.data_block), copy.deepcopy(self.distill_block)])

        for ins in instructions:

            # self.data_block.visualization()
            print(f'Now simulating the instruction:{ins}')

            data_res = self.sim_one_ins(ins)
            for next_config in data_res:
                self.time_series.append([DataBlock(next_config), DistillBlock()])

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
            print('T')

        else:
            print('not implement')

        return result

    def visual_all(self):

        for config in self.time_series:
            visual(config)

