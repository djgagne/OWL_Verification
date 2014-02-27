#!/bin/csh
foreach station (OUN PRX ADM LTS WWR CLK GUY MLC END LAW OKC TUL EYW)
if ($station == "PRX") then
    set state="TX"
else if ($station == "EYW") then
    set state="FL"
else
    set state = "OK"
endif
set year="2012"
set month1="1"
set month2="7"
set day1="1"
set day2="1"

wget "http://mesonet.agron.iastate.edu/cgi-bin//request/getData.py?ls_baseLayers=Google+Streets&${state}_ASOS+Network=${state}_ASOS+Network&station=${station}&data=all&year1=${year}&year2=${year}&month1=${month1}&month2=${month2}&day1=${day1}&day2=${day2}&tz=local&format=comma&latlon=yes" -O verif_data/${station}_asos_${year}.txt 
end
