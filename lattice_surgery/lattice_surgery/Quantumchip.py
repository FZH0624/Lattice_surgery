from lattice_surgery.Grid import *
from lattice_surgery.Patch import *


class QuantumChip:

    def __init__(self, params):

        self.data_block = None
        self.time_series = None
        self.params = params
        self.initialization()

    def initialization(self):

        qbits = self.params.circuit.information.qubits
        config = dict()
        for qbit in qbits:
            config[qbit] = None

        self.data_block = Grid(config)
        self.data_block.initialization()

    def simulation(self):

        # simulation of each instruction (just implement the easiest case: no parallel)
        instructions = self.params.circuit.instructions
        self.time_series = []
        self.time_series.append(copy.deepcopy(self.data_block))

        for ins in instructions:

            # self.data_block.visualization()
            print(f'Now simulating the instruction:{ins}')

            result = self.data_block.simulation(ins)
            for next_config in result:
                self.time_series.append(Grid(next_config))

    def visual(self):

        for i in range(len(self.time_series)):
            self.time_series[i].visualization()
