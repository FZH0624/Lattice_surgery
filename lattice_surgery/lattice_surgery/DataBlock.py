from lattice_surgery.Grid import Grid
import math
from lattice_surgery.Patch import Patch


class DataBlock(Grid):

    def __init__(self, config, params):

        super().__init__(config, params)
        self.size = (2 * math.ceil(len(self.params.circuit.information.qubits) / 2), 4)
        self.avail_list = []

    def initialization(self):

        n = len(self.config.keys())

        # available qbit list in the grid
        for j in range(2):
            for i in range(math.ceil(n / 2)):
                self.avail_list.append((2 * i, 2 * j))

        for qbit in self.config.keys():
            axis = [self.avail_list.pop(0)]
            pat = Patch(qbit, axis)
            self.config[qbit] = pat
