import numpy as np
from datetime import datetime
class ASOS:
    def __init__(self,site,startDate,endDate,path='verif_data/'):
        """Initialize ASOS class.  Opens file and loads data from file"""
        self.site = site.upper()
        self.filename=path + self.site + '_asos.txt'
        self.startDateTime = datetime.strptime(startDate,'%Y%m%d')
        self.endDateTime = datetime.strptime(endDate,'%Y%m%d')

        data = []
        datafile = open(self.filename)
        for line in datafile:
            if line[0] != '#':
                if 'station' in line:
                    self.header = [x.strip() for x in line[:-1].split(',')]
                else:
                    dataline = line[:-2].split(',')
                    for i,val in enumerate(dataline[:-1]):
                        if val=='M':
                            dataline[i] = -999
                    dataline[1] = dataline[1].replace(' ','_')
                    dataline[1] = dataline[1].replace('-','')
                    currDateTime = datetime.strptime(dataline[1][:14],'%Y%m%d_%H:%M')
                    if currDateTime >= self.startDateTime and currDateTime <= self.endDateTime:
                        data.append(tuple(dataline))
        datafile.close()
        self.datatype = []
        for item in self.header:
            if item == 'station':
                self.datatype.append((item,'S3'))
            elif 'valid' in item:
                self.datatype.append(('time','S14'))
            elif 'skyc' in item:
                self.datatype.append((item,'S3'))
            elif item=='metar':
                self.datatype.append((item,'S99'))
            else:
                self.datatype.append((item,float))
        self.data = np.array(data,dtype=self.datatype)
    
    def getDataValues(self,startDate,endDate,variable):
        """ getDataValues(startDate,endDate,variable)
            Purpose:  Retrieve values over a particular time range.
            Parameters:
                startDate:  date string for start of period of interest
                endDate:  date string for end of period of interest
                variable:  variable to be extracted.
        """
        dateIdxs = np.nonzero(np.logical_and(self.data['time'] >= startDate,self.data['time'] <= endDate))
        return self.data[variable][dateIdxs]

    def getHighTemps(self,startDates,endDates):
        """ getHighTemps(startDates,endDates)
            Purpose:  Retrieve high temperatures for given starting and ending dates
            Parameters:
                startDates:  array of starting date strings for each forecast period 
                endDates:  array of ending date strings for each forecast period
            Returns:
                Array of high temperatures corresponding to the periods in startDates and endDates 
            """
        highTemps = []
        for idx in xrange(len(startDates)):
            temps = self.getDataValues(self,startDates[idx],endDates[idx],'tmpf')
            highTemps.append(np.max(temps))
        return np.array(highTemps,dtype=float)

    def getLowTemps(self,startDates,endDates):
        """ getLowTemps(startDates,endDates)
            Purpose:  Retrieve low temperatures for given start and end dates
            Parameters:
                startDates:  array of starting date strings for each forecast period
                endDates:  array of starting date strings for each forecast period
            Returns:
                Array of low temperatures corresponding to the periods in startDates and endDates
        """
        lowTemps = []
        for idx in xrange(len(startDates)):
            temps = self.getDataValues(self,startDates[idx],endDates[idx],'tmpf')
            lowTemps.append(np.min(temps[np.nonzero(temps > -990)]))
        return np.array(lowTemps,dtype=float)
def main():
    for site in ['adm','clk','end','eyw','guy','prx','law','lts','mlc','okc','oun','prx','tul','wwr']:
        print site
        startDate = '20090930'
        endDate = '20110601'
        d = ASOS(site,startDate,endDate)
        print d.data[0]
        print d.getDataValues('20100510_02:00','20100510_23:00','p01m')

if __name__=="__main__":
    main()
