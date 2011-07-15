from OWLShift import OWLShift
from ASOS import ASOS
from ContingencyTable import ProbContingencyTable,ContinuousContingencyTable
from OWLOutput import OWLOutput
from datetime import datetime,timedelta
import os
import re
import cPickle as pickle
import argparse
import numpy as np

days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
times = ['Mor','Aft','Eve']

# Dictionary mapping verifying points to forecast points
verif_to_fcst = {'GUY':'KGUY', 'WWR':'KWWR', 'CLK':'KCSM', 'LTS':'KLTS', 'LAW':'KLAW', 'END':'KEND', 'OKC':'KOKC', 'OUN':'KOUN', 'ADM':'KADM', 'TUL':'KTUL', 'MLC':'KMLC', 'PRX':'KHHW', 'EYW':'KEYW' }

# Dictionary mapping forecast points to verifying points
fcst_to_verif = {'KGUY':'GUY', 'KWWR':'WWR', 'KCSM':'CLK', 'KLTS':'LTS', 'KLAW':'LAW', 'KEND':'END', 'KOKC':'OKC', 'KOUN':'OUN', 'KADM':'ADM', 'KTUL':'TUL', 'KMLC':'MLC', 'KHHW':'PRX', 'KEYW':'EYW' }

def main():
    parser = argparse.ArgumentParser(description='Load and match forecasts and observed data.')
    parser.add_argument('--start',default='20090910',help='Start verification date in the format YYYYMMDD')
    parser.add_argument('--end',default='20110509',help='End verification date in the format YYYYMMDD')
    parser.add_argument('--update',action='store_true',help='Load data from pickle files and add any new data from files.')
    parser.add_argument('--frompickle',action='store_true', help='Load data from a pickle file.')
    parser.add_argument('--owlpickle',default='owl_shift_forecasts.pkl',help='Specify name of OWL forecast file.')
    parser.add_argument('--asospickle',default='asos_sites.pkl',help='Specify name of ASOS sites file')
    parser.add_argument('--precip',action='store_true', help='Run precip verification')
    parser.add_argument('--temps',action='store_true', help='Run temperature verification')
    parser.add_argument('--out',help='Output file for verification data.')
    args = parser.parse_args()
    if args.update or args.frompickle:
        shifts = pickle.load(open(args.owlpickle))
        asos_sites = pickle.load(open(args.asospickle))
    else:
        asos_sites = None
        shifts = {}
        for day in days:
            for time in times:
                shifts[day + '_' + time] = OWLShift(day,time)

    if not args.frompickle:
        shifts = collectForecasts(shifts,args.start,args.end)
        asos_sites = collectASOS(args.start,args.end,asos_sites)
        pickle.dump(shifts,open(args.owlpickle,'w'))
        pickle.dump(asos_sites,open(args.asospickle,'w'))

    morning_shifts = {}
    afternoon_shifts = {}
    evening_shifts = {}

    for shift_time, fcsts in shifts.iteritems():
        if shift_time[-3:] == "Mor":
            morning_shifts[shift_time] = fcsts
        if shift_time[-3:] == "Aft":
            afternoon_shifts[shift_time] = fcsts
        if shift_time[-3:] == "Eve":
            evening_shifts[shift_time] = fcsts
    if args.precip:
        scores = verifyPrecip(shifts, asos_sites, args.start, args.end)
        morning_scores = verifyPrecip(morning_shifts, asos_sites, args.start, args.end)
        afternoon_scores = verifyPrecip(afternoon_shifts, asos_sites, args.start, args.end)
        evening_scores = verifyPrecip(evening_shifts, asos_sites, args.start, args.end)

        print "Overall Verification Scores"
        station_list = asos_sites.keys()
        for period in OWLShift._forecast_days:
            print "BSS's for period %s:" % period
            print "All stations: %f" % scores[period]['all']
            for station in station_list:
                print "%s: %2.2f %2.2f %2.2f %2.2f" % (verif_to_fcst[station], scores[period][station], morning_scores[period][station], afternoon_scores[period][station], evening_scores[period][station])
                print
    
    if args.temps:
        temp_out = OWLOutput(header=['ME','MAE','RMSE'])
        station_list = asos_sites.keys()
        station_list.sort()
        me,mae,rmse = verifyTemps(shifts, asos_sites,args.start,args.end)
        for period in OWLShift._forecast_days:
            print 'Day ' + period
            for station in station_list:
                print '%s: H:  %2.2f  L:  %2.2f' % (verif_to_fcst[station], rmse[period][station]['H'],rmse[period][station]['L'])
                for t in ['H','L']:
                    entry = ['TMP' + t,period,station,args.start,args.end,'ALL','ALL',me[period][station][t],mae[period][station][t],rmse[period][station][t]]
                    temp_out.addEntry(*entry)
        temp_out.toCSV(args.out)
    return

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
#       print currDate
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
    return

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

def verifyTemps(forecasts,observations,start_date,end_date):
    """
    verifyTemps()
    Purpose:  Control function for temperature verification
    Parameters:  forecasts [type=dictionary]
                    Dictionary mapping shift days (e.g. 'Tue_Aft' for Tuesday Afternoon) to their OWLShift objects.

    """
    me = {}
    mae = {}
    rmse = {}
    all_obs = observations.keys()
    all_obs.sort()
    for period in OWLShift._forecast_days:
        rmse[period] = {}
        mae[period] = {}
        me[period] = {}
        for station in all_obs:
            H_ct = tempContingencyTable(forecasts, observations, start_date, end_date, temp="H",stations=station, period=period)
            L_ct = tempContingencyTable(forecasts, observations, start_date, end_date, temp="L",stations=station, period=period)
            print station, period
            rmse[period][station] = dict(H=H_ct.RootMeanSquareError(),L=L_ct.RootMeanSquareError()) 
            mae[period][station] = dict(H=H_ct.MeanAbsoluteError(),L=L_ct.MeanAbsoluteError())
            me[period][station] = dict(H=H_ct.MeanError(),L=L_ct.MeanError())
    return me,mae,rmse

def verifyPrecip(forecasts, observations, start_date, end_date):
    """
    verifyPrecip()
    Purpose:    Main precipitation verification function
    Parameters: forecasts [type=dictionary]
                    Dictionary mapping shift days (e.g. 'Tue_Aft' for Tuesday Afternoon) to their OWLShift objects.
                observations [type=dictionary]
                    Dictionary mapping observation points (e.g. 'OUN' for Norman) to their ASOS objects.
                start_date [type=string]
                    String containing the date of the start of the verification period (format is 'YYYYMMDD_HH:MM').
                end_date [type=string]
                    String containing the date of the end of the verification period (format is 'YYYYMMDD_HH:MM', same as in start_date).
    Returns:    [nothing ... yet]
    """
    brier_skill_scores = {}

    for period in OWLShift._forecast_days:
        brier_skill_scores[period] = {}

        print "Period %s" % period
        for station in observations.keys():
            print "Day %s forecasts for station %s:" % (period, verif_to_fcst[station])
            ct = precipContingencyTable(forecasts, observations, start_date, end_date, stations=station, period=period)
            BSS = ct.BrierSkillScore()
            print "Contingency Table:"
            print ct
            print "Brier Skill Score: ", BSS
            print

            brier_skill_scores[period][station] = BSS

        ct = precipContingencyTable(forecasts, observations, start_date, end_date, period=period)
        bs,reliability,resolution,uncertainty = ct.BrierScore(components=True)
        BSS = ct.BrierSkillScore()

        print "Contingency Table:"
        print ct
        print "Brier Score: ", bs
        print "Reliability, Resolution, Uncertainty: ", reliability, resolution, uncertainty
        print "Brier Skill Score: ", BSS
        print

        brier_skill_scores[period]['all'] = BSS

    return brier_skill_scores

def dump(grid):
    """
    dump()
    Purpose:    Dump a grid of any number of dimensions to the console.  May want to modify it to dump to a file.
    Parameters: grid [type=np.array]
                    The grid to dump
    Returns:    [nothing]
    """
    if len(grid.shape) == 1:
        string = ""
        for val in grid:
            string += "%8.2f " % val
        print string
    else:
        for idx in range(grid.shape[0]):
            dump(grid[idx])
        print
    return

def precipContingencyTable(forecasts, observations, start_date, end_date, stations=None, shift=None, period=None):
    """
    precipContingencyTable()
    Purpose:    Produce a 2x11 contingency table containing all the precipitation probability forecasts for the period.
    Parameters: forecasts [type=dictionary]
                    Dictionary mapping shift days (e.g. 'Tue_Aft' for Tuesday Afternoon) to their OWLShift objects.
                observations [type=dictionary]
                    Dictionary mapping observation points (e.g. 'OUN' for Norman) to their ASOS objects.
                start_date [type=string]
                    String containing the date of the start of the verification period (format is 'YYYYMMDD_HH:MM').
                end_date [type=string]
                    String containing the date of the end of the verification period (format is 'YYYYMMDD_HH:MM', same as in start_date).
                stations [type=list,tuple,string]
                    A station or list of stations to include in the contingency table.  Optional, defaults to KOUN if not given.
                shift [type=string]
                    The shift to verify (e.g. 'Tue_Aft' for Tuesday Afternoon).  Not implemented yet.
                period [type=string]
                    The period to verify (one of '1A', '1B', '2', '3', or '4').  Optional, defaults to '1A' if not given.
    Returns:    The completed contingency table as a ProbContingencyTable object.
    """
    labels = np.arange(0,1.1,.1)
    contingency_table = ProbContingencyTable(labels,size=11)
    total_forecasts = 0

    if period is None:
        period = OWLShift._forecast_days[0]

    if stations is None:
        stations = observations.keys()
    elif type(stations) not in [ list, tuple ]:
        stations = [ stations ]

    for shift_name, shift_data in forecasts.iteritems():
        for stn in stations:
            pprb = shift_data.getForecasts(period, start_date, end_date, "PPRB", verif_to_fcst[stn])

            shift_start_times, shift_end_times = pprb[:2]

            precip_obs = observations[stn].getPrecip(shift_start_times, shift_end_times)

#           if shift_name[-3:] == "Mor" and stn == "ADM":
#               print "Shift starts:", shift_start_times
#               print "Shift ends:", shift_end_times
#               print "Obs:", precip_obs

            for idx in range(len(precip_obs)):
                contingency_table[precip_obs[idx], pprb[2][idx] / 10] += 1
                total_forecasts += 1

    return contingency_table

def splitLine(line,width=5):
    """Purpose:  Split line of fixed width data into list"""
    lineList = []
    for i in xrange(width,len(line[:-1])+width,width):
        lineList.append(line[i-width:i].strip())
    return lineList

def tempContingencyTable(forecasts, observations, start_date, end_date, temp="H", stations=None, shift=None, period=None):
    """
    precipContingencyTable()
    Purpose:    Produce a continuous contingency table containing all the temperature forecasts for the period.
    Parameters: forecasts [type=dictionary]
                    Dictionary mapping shift days (e.g. 'Tue_Aft' for Tuesday Afternoon) to their OWLShift objects.
                observations [type=dictionary]
                    Dictionary mapping observation points (e.g. 'OUN' for Norman) to their ASOS objects.
                start_date [type=string]
                    String containing the date of the start of the verification period (format is 'YYYYMMDD_HH:MM').
                end_date [type=string]
                    String containing the date of the end of the verification period (format is 'YYYYMMDD_HH:MM', same as in start_date).
                temp [type=string]
                    String telling whether the high or low temperature is being evaluated.  "H" for high and "L" for low.
                stations [type=list,tuple,string]
                    A station or list of stations to include in the contingency table.  Optional, defaults to KOUN if not given.
                shift [type=string]
                    The shift to verify (e.g. 'Tue_Aft' for Tuesday Afternoon).  Not implemented yet.
                period [type=string]
                    The period to verify (one of '1A', '1B', '2', '3', or '4').  Optional, defaults to '1A' if not given.
    Returns:    The completed contingency table as a ContinuousContingencyTable object.
    """
    temp_ct = ContinuousContingencyTable(np.array([]),np.array([]))
    if period is None:
        period = OWLShift._forecast_days[0]

    if stations is None:
        stations = observations.keys()
    elif type(stations) not in [ list, tuple ]:
        stations = [ stations ]

    for shift_name, shift_data in forecasts.iteritems():
        for stn in stations:
            if temp.upper()=="H":
                temp_fcasts = shift_data.getForecasts(period, start_date, end_date, "TMPH", verif_to_fcst[stn])
            else:
                temp_fcasts = shift_data.getForecasts(period, start_date, end_date, "TMPL", verif_to_fcst[stn])
            
            shift_start_times, shift_end_times = temp_fcasts[:2]
            if temp.upper()=="H":
                temp_obs = observations[stn].getHighTemps(shift_start_times,shift_end_times)
            else:
                temp_obs = observations[stn].getLowTemps(shift_start_times,shift_end_times)
            temp_ct.addPairs(temp_fcasts[2],temp_obs)
    return temp_ct

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
        periodDates = [(startDateTime + timedelta(days=1,hours=0),startDateTime + timedelta(days=1,hours=18)),
                        (startDateTime + timedelta(days=1,hours=18),startDateTime + timedelta(days=2,hours=6)),
                        (startDateTime + timedelta(days=2),startDateTime + timedelta(days=3)),
                        (startDateTime + timedelta(days=3),startDateTime + timedelta(days=4)),
                        (startDateTime + timedelta(days=4),startDateTime + timedelta(days=5))]
    else:
        periodDates = []
    return periodDates

if __name__=="__main__":
    main()
