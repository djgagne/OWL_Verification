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
    
    def getDataValues(self,startDate,endDate,variable,dataFilter=True):
        """ getDataValues(startDate,endDate,variable)
            Purpose:  Retrieve values over a particular time range.
            Parameters:
                startDate:  date string for start of period of interest
                endDate:  date string for end of period of interest
                variable:  variable to be extracted.
        """
        if dataFilter:
            dateIdxs = np.nonzero((self.data['time'] >= startDate) & (self.data['time'] <= endDate) & (self.data[variable] > -990))
        else:
            dateIdxs = np.nonzero((self.data['time'] >= startDate) & (self.data['time'] <= endDate))
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
            temps = self.getDataValues(startDates[idx],endDates[idx],'tmpf')
            if len(temps) > 0:
                highTemps.append(np.max(temps))
            else:
                highTemps.append(-998)
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
            temps = self.getDataValues(startDates[idx],endDates[idx],'tmpf')
            if len(temps) > 0:
                lowTemps.append(np.min(temps))
            else:
                lowTemps.append(-998)
        return np.array(lowTemps,dtype=float)

    def getPrecip(self, startDates, endDates):
        """ getPrecip(startDates,endDates)
            Purpose:  Retrieve precipitation between the given start and end dates.
            Parameters:
                startDates [type=list,tuple,np.array]:  Array of starting date strings (format is 'YYYYMMDD_HH:MM') for each forecast period.
                endDates [type=list,tuple,np.array]:  Array of starting date strings (format is 'YYYYMMDD_HH:MM', same as in startDates) for each forecast period.
            Returns:
                A boolean array of precipitation occurrence corresponding to the periods in startDates and endDates.
        """
        precip = []
        for idx in xrange(len(startDates)):
            precip1hr = self.getDataValues(startDates[idx], endDates[idx], 'p01m')
#           if self.site == "ADM" and startDates[idx][-5:] == "10:00" and endDates[idx][-5:] == "18:00":
#               print startDates[idx], endDates[idx], precip1hr
            if len(precip1hr) > 0:
                precip.append(precip1hr.sum())
            else:
                precip.append(-998)
        return np.array(precip, dtype=float)

def main():
    for site in ['adm','clk','end','eyw','guy','prx','law','lts','mlc','okc','oun','prx','tul','wwr']:
        print site
        startDate = '20090930'
        endDate = '20110601'
        d = ASOS(site,startDate,endDate)
        print d.data[0]
        print d.getDataValues('20100510_02:00','20100510_23:00','p01m')
        print d.getHighTemps(['20100510_02:00'],['20100510_23:00'])
if __name__=="__main__":
    main()
