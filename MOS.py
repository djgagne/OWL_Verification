import numpy as np
from datetime import datetime,timedelta
class MOS:
    def __init__(self,sites,startDate,endDate,mosHour,type='mex',path='mos/gfsmex/'):
        """
        MOS()
        Purpose:  Initialize MOS object that will store forecasts for specified sites over a specified period
        Parameters:  sites (iterable) - list of MOS sites
                    startDate 'YYYYMMDD' - date string for first date of MOS forecasts
                    endDate 'YYYYMMDD' - date string for last date of MOS forecasts
                    type [string] - MOS type used, such as gfsmex,gfsmav
        """
        self.sites = ['K' + s if len(s) == 3 else s for s in sites]
        self.startDateTime = datetime.strptime(startDate,'%Y%m%d')
        self.endDateTime = datetime.strptime(endDate,'%Y%m%d')
        self.mosHour = str(mosHour).zfill(2)
        self.type = type
        self.filepath = path
        self.forecasts = []
        currDateTime = datetime.strptime(startDate,'%Y%m%d')
        currfile = open(path + type + currDateTime.strftime('%Y%m') + '.t' + self.mosHour + 'z','r')
        mosData = currfile.readlines()
        currfile.close()
        l = 0
        while currDateTime <= self.endDateTime:
            if l < len(mosData):
                if 'MOS GUIDANCE' in mosData[l]:
                    header = mosData[l].split()
                    if header[0] in self.sites:
                        print header
                        fDateTime = datetime.strptime(header[4],'%m/%d/%Y')
                        if currDateTime < fDateTime:
                            currDateTime = fDateTime 
                        self.parseSingleForecast(mosData,l)
                    l += 12 
                else:
                    l += 1
            
            else:
                l = 0
                currDateTime = currDateTime + timedelta(days=1)
                currfile = open(path + type + currDateTime.strftime('%Y%m') + '.t' + self.mosHour + 'z','r')
                mosData = currfile.readlines()
                currfile.close()

    def parseSingleForecast(self,mosData,l):
        """
        parseSingleForecast()
        Purpose:  read lines containing MOS forecast information and break the information down into 
            individual forecasts for each lead time in the file.
        """
        mosWidths = dict(mex=65)
        header = mosData[l].split()
        singleForecast = {}
        singleForecast['site'] = header[0]
        singleForecast['model'] = header[1]
        singleForecast['date'] = datetime.strptime(header[4],'%m/%d/%Y')
        singleForecast['hour'] = header[5]
        l += 1
        while len(mosData[l].split()) > 1:
            cleanLine = mosData[l][:mosWidths[self.type]].replace('|',' ')
            dataList = cleanLine.split()
            singleForecast[dataList[0]] = dataList[1:]
            l+= 1
        for k,v in singleForecast.iteritems():
            print k,v
            
        
        

if __name__ == "__main__":
    sites = ['OKC','OUN','TUL','GUY','WWR','LAW','LTS','END','ADM','PRX','MLC','EYW','CLK']
    mos = MOS(sites,'20090901','20091031',0)
      
                
            