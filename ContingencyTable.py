
import numpy as np

"""
ContingencyTable
Purpose:    Base class for the contingency tables.  Handles things like getting and setting individual items in the table and converting tables to strings.
Started:    6-30-11 by Tim Supinie (tsupinie@ou.edu)
Completed:  [not yet]
Modified:   [not yet]
"""

class ContingencyTable(object):

    def fill(self, data):
        """
        fill() [public]
        Purpose:    Fill the contingency table with an array of data.
        Parameters: data [type=np.array]: The data to put in the contingency table
        Returns:    [nothing]
        """
        if data.shape != self.ct.shape:
            print "Error!"

        self.ct = data
        return

    def __getitem__(self, index):
        """
        __getitem__() [public]
        Purpose:    Returns an item or array of items from the table (called as <ContingencyTable object>[index]).
        Parameters: index [type=int,tuple]: The index in the table to return.  Can be an integer or a tuple of integers.
        Returns:    The value(s) from the table.
        """
        return self.ct[index]

    def __setitem__(self, index, value):
        """
        __setitem__() [public]
        Purpose:    Sets an item or array of items in the table (called as <ContingencyTable object>[index] = value).
        Parameters: index [type=int,tuple]: The index in the table to set.  Can be an integer or a tuple of integers.
                    value [type=int]: The value to set the index to.
        Returns:    [nothing]
        """
        self.ct[index] = value
        return 

    def __str__(self):
        """
        __str__() [public]
        Purpose:    Returns a string representation of the contingency table (called as str(<ContingencyTable object>) or print to the console with print <ContingencyTable object>).
        Parameters: [none]
        Returns:    A string representation of the contingency table.
        """
        string = ""
        for idx in range(self.ct.shape[0]):
            for jdy in range(self.ct.shape[1]):
                string += "%8.2f " % self.ct[idx, jdy]
            string += "\n"
        return string + "\n"

"""
ProbContingencyTable
Purpose:    Handles computing scores for probability contingency tables (2 x n).
Started:    6-30-11 by Tim Supinie (tsupinie@ou.edu)
Completed:  [not yet]
Modified:   [not yet]
"""

class ProbContingencyTable(ContingencyTable):
    def __init__(self, labels, size=None, data=None):
        """
        __init__()
        Purpose:    Constructor for the ProbContingencyTable class.  Either initializes it as a blank 2 x size table (fills it with zeros) or fills it with the data provided.
        Parameters: labels [type=np.array]:  Array of probability values.
                    size [type=int]: The size of the table to create.
                    data [type=np.array]: Data to fill the initial table with
        """
        self.labels = np.array(labels,dtype=float)
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
        """
        getReliability() [public]
        Purpose:    Compute and return the data for a reliability diagram.
        Parameters: [none]
        Returns:    Reliability diagram data as a numpy array.
        """
        return self.ct[1] / self.ct.sum(axis=0, dtype=float)
    
    def BrierScore(self,components=False):
        """
        BrierScore(components=False) [public]
        Purpose:  Compute the Brier Score and its components: reliability, resolution, and uncertainty
        Returns:  If components==False, returns Brier Score.  If components==True, returns a tuple of (BrierScore,reliability,resolution,uncertainty).
        """
        N = self.ct.sum(dtype=float)
        num_forecasts = self.ct.sum(axis=0,dtype=float)
        obs_freq = self.ct[1] / num_forecasts
        obs_freq[np.nonzero(np.isnan(obs_freq))] = 0
        climo = np.sum(self.ct[1]) / N
        reliability = 1/N * np.sum(num_forecasts * (self.labels- obs_freq) ** 2)
        resolution = 1/N * np.sum(num_forecasts * (obs_freq - climo) ** 2)
        uncertainty = climo * ( 1 - climo)
        BS = reliability - resolution + uncertainty
        if components:
            return BS,reliability,resolution,uncertainty
        else:
            return BS
    def BrierSkillScore(self):
        """
        BrierSkillScore() [public]
        Purpose:  Calculate the Brier Skill Score for probabilistic forecasts
        Parameters:  None
        Returns:  the Brier Skill Score as a float
        """
        BS,reliability,resolution,uncertainty = self.BrierScore(components=True)
        return (resolution - reliability) / uncertainty


"""
MultiContingencyTable
Purpose:    Handles computing scores for multiclass contingency tables (n x n).
Started:    6-30-11 by Tim Supinie (tsupinie@ou.edu)
Completed:  [not yet]
Modified:   [not yet]
"""

class MultiContingencyTable(ContingencyTable):
    def __init__(self, labels,size=None, data=None):
        """
        __init__()
        Purpose:    Constructor for the MultiContingencyTable class.  Either initializes it as a blank size x size table (fills it with zeros) or fills it with the data provided.  Observed categories are the columns and forecast categories are the rows.
        Parameters: labels [type=np.array]:  Labels for each item being forecasted and verified.
                    size [type=int]: The size of the table to create.
                    data [type=np.array]: Data to fill the initial table with
        """
        self.labels = labels
        if data is None:
            if size is None:
                print "Error!"

            self.ct = np.zeros((size, size))
        else:
            if data.shape[0] != data.shape[1]:
                print "Error!"

            self.ct = data
        return

    def HeidkeSkillScore(self):
        """
        HeidkeSkillScore() [public]
        Purpose:  Calculate the multiclass Heidke Skill Score
        Returns:  the Heidke Skill Score
        """
        N = self.ct.sum(dtype=float)
        NO = self.ct.sum(axis=0)
        NF = self.ct.sum(axis=1)
        n_diag = 0
        for i in xrange(self.ct.shape[0]):
            n_diag += self.ct[i,i]
        HSS = (1/N * n_diag - 1/N**2 * np.sum(NO * NF)) / ( 1 - 1/N**2 * np.sum(NF * NO))
        return HSS
    
    def PeirceSkillScore(self):
        """
        PeirceSkillScore() [public]
        Purpose:  Calculate the multiclass Peirce (a.k.a. Hanssen and Kuipers, true skill statistic)
        Returns:  The Peirce Skill Score
        """
        N = self.ct.sum(dtype=float)
        NO = self.ct.sum(axis=0)
        NF = self.ct.sum(axis=1)
        n_diag = 0
        for i in xrange(self.ct.shape[0]):
            n_diag += self.ct[i,i]
        PSS = (1/N * n_diag - 1/N**2 * np.sum(NO * NF)) / ( 1 - 1/N**2 * np.sum(NO**2))
        return PSS

if __name__ == "__main__":
    # Create a probability contingency table
    labels = np.arange(0,1.1,0.1)
    prob_ct = ProbContingencyTable(labels,size=11)
    # Fill table with data
    prob_ct.fill(np.array(range(11 * 2)).reshape((2, 11)))

    # Modify a single element of the table
    prob_ct[0, 0] += 1
    print prob_ct
    print prob_ct.getReliability()
    print prob_ct.BrierScore(components=True)
    print prob_ct.BrierSkillScore()
    # Create a multicategory contingency table (improper size: will fail)
    labels = np.array(['Yes','No','Maybe'],dtype='S6')
    mult_ct = MultiContingencyTable(labels,data=np.array([0]*9).reshape(3, 3))
    for i in xrange(3):
        mult_ct.ct[i,i] += 2
    print mult_ct.HeidkeSkillScore()
    print mult_ct.PeirceSkillScore()
