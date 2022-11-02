from collections import namedtuple


Inform = namedtuple('Inform', 'operations, qubits', defaults=({}, []))
Qcircuit = namedtuple('Qcircuit', 'circuit, timeslice', defaults=({}, []))


class Circuit:

    def __init__(self, instructions):
        self.instructions = instructions
        self.qcircuit = Qcircuit({}, [])
        self.information = Inform({}, [])
        self.__get_inform()
        self.__circuit_analysis()

    def __get_inform(self):
        for ins in self.instructions:
            n = len(ins)
            for i in range(n):

                # This first element in qcis is gate operation
                if i == 0:
                    if ins[i] not in self.information.operations.keys():
                        self.information.operations[ins[i]] = 1
                    else:
                        self.information.operations[ins[i]] = self.information.operations[ins[i]] + 1
                # Count the qbits we declared in the qcis
                else:
                    if ins[i] not in self.information.qubits:
                        self.information.qubits.append(ins[i])

    def __circuit_analysis(self):

        # This function is to get the circuit overview by the qcis file.
        qcis_inst = self.instructions
        cir = self.qcircuit.circuit
        time_slice = self.qcircuit.timeslice

        # Declare a timeslice list longer than the true case
        time_slice_long = [[] for i in range(len(qcis_inst))]

        for ins in qcis_inst:

            length = len(ins)
            for ind in range(length):
                if ind == 0:  # The gate operation
                    gate = ins[ind]

                else:  # For each qbit we maintain a stack to capture the operation according to the time
                    if ins[ind] not in cir.keys():
                        cir[ins[ind]] = [(None, 0)]

                    # m store the information about which timeslice this instruction in.
                    if length == 2:
                        prev = ins[ind]
                        m = cir[prev][-1][1]
                        cir[prev].append((gate, m + 1))

                    if length == 3:
                        if ind == 1:
                            prev = ins[ind]
                            continue
                        if ind == 2:
                            succ = ins[ind]

                        m = max(cir[prev][-1][1], cir[succ][-1][1])
                        cir[prev].append((gate, m + 1))
                        cir[succ].append((gate, m + 1))

            time_slice_long[m].append(ins)

        for i in time_slice_long:
            if i:
                time_slice.append(i)