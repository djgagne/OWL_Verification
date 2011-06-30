
import numpy as np

class ContingencyTable(object):

    def fill(self, data):
        if data.shape != self.ct.shape:
            print "Error!"

        self.ct = data
        return

    def __getitem__(self, key):
        return self.ct[key]

    def __setitem__(self, key, value):
        self.ct[key] = value
        return 

    def __str__(self, grid=None):
        string = ""
        for idx in range(self.ct.shape[0]):
            for jdy in range(self.ct.shape[1]):
                string += "%8.2f " % self.ct[idx, jdy]
            string += "\n"
        return string + "\n"

class ProbContingencyTable(ContingencyTable):
    def __init__(self, size=None, data=None):
        if data is None:
            if size is None:
                print "Error!"

            self.ct = np.zeros((2, size))
        else:
            if data.shape[0] != 2:
                print "Error!"

            self.ct = data
        return

    def getReliability(self):
        return self.ct[1] / self.ct.sum(axis=0, dtype=float)

class MultiContingencyTable(ContingencyTable):
    def __init__(self, size=None, data=None):
        if data is None:
            if size is None:
                print "Error!"

            self.ct = np.zeros((size, size))
        else:
            if data.shape[0] != data.shape[1]:
                print "Error!"

            self.ct = data
        return

if __name__ == "__main__":
    # Create a probability contingency table
    prob_ct = ProbContingencyTable(size=11)

    # Fill table with data
    prob_ct.fill(np.array(range(11 * 2)).reshape((2, 11)))

    # Modify a single element of the table
    prob_ct[0, 0] += 1

    print prob_ct
    print prob_ct.getReliability()

    # Create a multicategory contingency table (improper size: will fail)
    mult_ct = MultiContingencyTable(data=np.array(range(3 * 3)).reshape(4, 3))
