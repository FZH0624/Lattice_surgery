from pre_processing import *
from tools import *
from lattice_surgery.Quantumchip import *


def read_qcis(file_path):
    with open(file_path) as f:
        f_lines = f.readlines()

    qcis_inst = []
    for line in f_lines:
        ins = []
        temp = ''
        for letter in line:
            if letter.isspace():
                ins.append(temp)
                temp = ''
            else:
                temp = temp + letter
        qcis_inst.append(ins)

    return qcis_inst


class Solution:

    def __init__(self, file_path):

        self.qcis_inst = read_qcis(file_path)
        self.init()

    def init(self):

        cir = Circuit(self.qcis_inst)
        params = Params('surface', cir, LowLevelOpts(d=5))
        chip = QuantumChip(params)
        chip.simulation()
        chip.visual()
        #chip.data_block.visualization()
        #chip.data_block.move_by_path('Q2', path)
        #chip.data_block.visualization()