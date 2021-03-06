import numpy as np
import sys,traceback
class OWLShift:
    
    # Static public list of all the possible forecast periods for an OWL shift
    _forecast_days = ['1A', '1B', '2', '3', '4']

    def __init__(self,day,period):
        """OWL Shift class
            Purpose:  Stores forecast information about a particular OWL shift.
        """
        self.day = day
        self.period = period
        self.day1A = []
        self.day1B = []
        self.day2 = []
        self.day3 = []
        self.day4 = []
        self.perDtype = [('SDATE','S15'),('EDATE','S15'),('SITE','S4'),('TMPH',float),('TIMH','S3'),('TMPL',float),('TIML','S3'),('WDRI','S2'),('WDRF','S2'),('WSHI',float),('WSLO',float),('WGST',float),('SKYC','S3'),('PPRB',float),('PTYP','S2'),('PINT','S3')]

    
    def addForecast(self,fcst,period):
        """Purpose:  Add a forecast to a specified period.
            Parameters:
                fcst - list of forecast parameters taken from a forecast file
                period - day1A,day1B,day2,day3,day4 - name of day forecast goes in""" 
        for i in xrange(len(fcst)):
            if fcst[i] == '':
                fcst[i] = '-999'
        try:
            inForecast = np.array(tuple(fcst),dtype=self.perDtype)
            if getattr(self,period) == []:
                setattr(self,period,inForecast)
            else:
                setattr(self,period,np.hstack((getattr(self,period),inForecast)))
        except:
            print self.day,self.period,period
            print fcst
            print getattr(self,period)
            print traceback.print_exc()
    
    def getForecasts(self,forecastDay,startDate,endDate,variable,site,filter=True):
        """getForecasts
            Purpose:  retrieve a list of forecast values for a particular variable
            Parameters:
                forecastDay - 1A,1B,2,3,4
                startDate,endDate - datetime object or 'YYYYMMDD' string that specifies the starting and ending dates
                variable - variable to be extracted as an array of values.
                site - site where variable is being extracted.
                filter - if True, remove dates with missing values for the selected variable.
            Returns:
                A tuple of arrays with the first array containing the start verifying dates/times, the second array containing the end verifying dates/times, and the third array containing the variable values.
        """

        forecasts = getattr(self, 'day' + forecastDay)        

        if filter == False:
            siteIdxs = np.nonzero((forecasts['SDATE'] >= startDate) & (forecasts['EDATE'] <= endDate) & (forecasts['SITE']==site))
        else:
            siteIdxs = np.nonzero((forecasts['SDATE'] >= startDate) & (forecasts['EDATE'] <= endDate) &
                (forecasts['SITE']   == site) &
                (forecasts[variable] >  -900) &
                ((forecasts['TMPH'] > -900) | (forecasts['TMPL'] > -900)))

        return (forecasts['SDATE'][siteIdxs], forecasts['EDATE'][siteIdxs], forecasts[variable][siteIdxs])

if __name__ == "__main__":
    import cPickle as pickle
    forecasts = pickle.load(open('owl_shift_forecasts.pkl'))
    all_temps = forecasts['Thu_Aft'].getForecasts('2','20090910','20110510','TMPH','KOUN',filter=False)
    temps = forecasts['Thu_Aft'].getForecasts('2','20100910','20110410','TMPH','KOUN',filter=True)
    print all_temps
    print temps
