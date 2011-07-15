class OWLOutput:
    def __init__(self,header=['ME','MAE','RMSE','BS','BSS','PSS','HSS']):
        """
        OWLOutput()
        Purpose:  Initialize OWLOutput class
        Parameters:
        header:  list of verification statistics being included in the file
        """
        self.metaheader = ['Variable','ForecastDay','Station','StartDate','EndDate','ShiftPeriod','ShiftDay']
        self.header = [x for x in self.metaheader]
        self.header.extend(header)
        self.data = []

    def addEntry(self,*args):
        """
        addEntry() [public]
        Parameters:
        args: list of arguments that correspond to entries in header

        """
        if len(args) == len(self.header):
            self.data.append(args)
        else:
            print "Error:  entry not correct length"
    
    def toCSV(self,filename,delimiter=',',newline='\n'):
        """
        toCSV() [public]
        Parameters:
        filename:  name of csv file being written
        delimiter:  character that separates entries in row
        newline:  character that separates lines
        """
        outfile = open(filename,'w')
        outfile.write(delimiter.join(self.header) + newline)
        for entry in self.data:
            outfile.write(delimiter.join([str(x) for x in entry]) + newline)
        outfile.close()

    def fromCSV(self,filename,delimiter=',',newline='\n',overwrite=False):
        """
        fromCSV() [public]
        Parameters:
        filename:  name of csv file being read
        delimiter:  character that separates entries in row
        newline:  character that separates lines
        """
        infile = open(filename)
        fullfile = infile.read()
        infile.close()
        filelists = fullfile.split(newline)
        
        if self.header == filelists[0].split(delimiter):
            if overwrite:
                self.data = []
            for entry in filelists[1:]:
                if len(entry) > 1:
                    self.addEntry(*entry.split(delimiter))
        else:
            print filelists[0]

            

if __name__=="__main__":
    o = OWLOutput(header=['ME','MAE'])
    entry = ['TMPH','1A','KOUN','20090911','20100510','ALL','ALL',-2.0,3.4]
    o.addEntry(*entry)
    o.fromCSV('out_test.csv')
    o.toCSV('out_test.csv')
    print o.data
