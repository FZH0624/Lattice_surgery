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
        chip.visual_all()

        ########## TEST AREA ############
        #print(chip.data_block.config['Q1'].border_map)
        #visual(chip.configuration)
        #chip.data_block.turn_around('Q1',  ((1, 0), (1, 1)))
        ##chip.data_block.move_corner('Q1', ((0, 1), (0, 0)), ((2, 1), (1, 1)))
        #visual(chip.configuration)
        #chip.visual_all()
