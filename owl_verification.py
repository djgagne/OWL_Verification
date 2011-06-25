from OWLShift import OWLShift
from ASOS import ASOS
from datetime import datetime,timedelta
import os
import re
import cPickle as pickle
import argparse

days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
times = ['Mor','Aft','Eve']
def main():
    parser = argparse.ArgumentParser(description='Load and match forecasts and observed data.')
    parser.add_argument('--start',default='20090901',help='Start verification date in the format YYYYMMDD')
    parser.add_argument('--end',default='20110509',help='End verification date in the format YYYYMMDD')
    parser.add_argument('--update',action='store_true',help='Load data from pickle files and add any new data from files.')
    parser.add_argument('--compare',action='store_true',help='Load data from pickle files and calculate comparison statistics.')
    parser.add_argument('--owlpickle',default='owl_shift_forecasts.pkl',help='Specify name of OWL forecast file.')
    parser.add_argument('--asospickle',default='asos_sites.pkl',help='Specify name of ASOS sites file')
    args = parser.parse_args()
    if args.update:
        shifts = pickle.load(open(args.owlpickle))
        asos_sites = pickle.load(open(args.asospickle))
    else:
        asos_sites = None
        shifts = {}
        for day in days:
            for time in times:
                shifts[day + '_' + time] = OWLShift(day,time)
    shifts = collectForecasts(shifts,args.start,args.end)
    asos_sites = collectASOS(args.start,args.end,asos_sites)
    pickle.dump(shifts,open(args.owlpickle,'w'))
    pickle.dump(asos_sites,open(args.asospickle,'w'))
def collectForecasts(shifts,startDate,endDate,forecastDir='fcst/'):
    """collectForecasts
        Purpose:  Loop through series of dates and load forecasts into appropriate OWL shifts
        Parameters:
            shifts - dictionary of OWLShift class objects
            startDate,endDate - starting and ending dates of verification period in YYYYMMDD form
    """
    forecastFiles = os.listdir(forecastDir)
    forecastFiles.sort()
    currDateTime = datetime(year=int(startDate[0:4]),month=int(startDate[4:6]),day=int(startDate[6:]))
    endDateTime = datetime(year=int(endDate[0:4]),month=int(endDate[4:6]),day=int(endDate[6:]))
    while (endDateTime - currDateTime).days >= 0:
        weekday = currDateTime.strftime('%a')
        currDate = currDateTime.strftime('%Y%m%d')
        print currDate
        for time in times:
            if currDate + time + '.fcst' in forecastFiles:
                loadOWLForecast(currDate,time,shifts[weekday + '_' + time])
        currDateTime = currDateTime + timedelta(days=1)
    return shifts

def loadOWLForecast(date,shift,owlshift,forecastDir='fcst/'):
    """loadOWLForecast
        Parameters: date - YYYYMMDD string representing date
                    shift - Mor,Aft,Eve
                    owlshift - OWLShift class passed from shifts that is to be modified
        Returns:  owl forecast in array form."""
    filename = date + shift + '.fcst'
    owlFile = open(forecastDir + filename)
    periods = ['day1A','day1B','day2','day3','day4']
    periodDates = setPeriodDates(date,shift)
    perIdx = -1
    for line in owlFile:
        if line[:8].isdigit():
            date = line[:8]
            perIdx += 1
            
        if 'TMPH' in line:
            header = splitLine(line[:-1])
        if re.match('K[A-Z]{3}',line):
            forecast = [periodDates[perIdx][0].strftime('%Y%m%d_%H:%M'),periodDates[perIdx][1].strftime('%Y%m%d_%H:%M')]
            forecast.extend(splitLine(line))
            owlshift.addForecast(forecast,periods[perIdx])
def collectASOS(startDate,endDate,sites=None,asos_dir='verif_data/'):
    """ collectASOS(sites,startDate,endDAte,asos_dir)
        Purpose:  Collect data from IEM ASOS data files.
        Parameters:
                startDate:  YYYYMMDD string representing first date included in file
                endDate:  YYYYMMDD string representing last date included in file
                sites: dictionary that has site acronyms as keys and ASOS objects as values
                       If None, then sites is initialized and all dates are added
                asos_dir:  directory containing IEM ASOS files
        Returns:  sites dictionary with ASOS data
    """
    if sites==None:
        asos_files = os.listdir(asos_dir)
        asos_files.sort()
        sites = {}
        for asos_file in asos_files:
            site = asos_file.split('_')[0]
            sites[site] = ASOS(site,startDate,endDate)
    else:
        for site,asos in sites.iteritems():
            asos.update(startDate,endDate)
    return sites
def splitLine(line,width=5):
    """Purpose:  Split line of fixed width data into list"""
    lineList = []
    for i in xrange(width,len(line[:-1])+width,width):
        lineList.append(line[i-width:i].strip())
    return lineList

def setPeriodDates(date,shift):
    """setPeriodDates
        Purpose:  Make a list of the appropriate verification datetimes for each forecast period"""
    startDateTime = datetime(year=int(date[0:4]),month=int(date[4:6]),day=int(date[6:]),hour=0,minute=0)
    if shift == 'Mor':
        periodDates = [(startDateTime + timedelta(hours=10),startDateTime + timedelta(hours=18)),
                        (startDateTime + timedelta(hours=18),startDateTime + timedelta(days=1,hours=6)),
                        (startDateTime + timedelta(days=1),startDateTime + timedelta(days=2)),
                        (startDateTime + timedelta(days=2),startDateTime + timedelta(days=3)),
                        (startDateTime + timedelta(days=3),startDateTime + timedelta(days=4))]
    elif shift == 'Aft':
        periodDates = [(startDateTime + timedelta(hours=18),startDateTime + timedelta(days=1,hours=6)),
                        (startDateTime + timedelta(days=1,hours=6),startDateTime + timedelta(days=2)),
                        (startDateTime + timedelta(days=2),startDateTime + timedelta(days=3)),
                        (startDateTime + timedelta(days=3),startDateTime + timedelta(days=4)),
                        (startDateTime + timedelta(days=4),startDateTime + timedelta(days=5))]
    elif shift == 'Eve':
        periodDates = [(startDateTime + timedelta(days=1,hours=0),startDateTime + timedelta(hours=18)),
                        (startDateTime + timedelta(days=1,hours=18),startDateTime + timedelta(days=2,hours=6)),
                        (startDateTime + timedelta(days=2),startDateTime + timedelta(days=3)),
                        (startDateTime + timedelta(days=3),startDateTime + timedelta(days=4)),
                        (startDateTime + timedelta(days=4),startDateTime + timedelta(days=5))]
    else:
        periodDates = []
    return periodDates
if __name__=="__main__":
    main()
