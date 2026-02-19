#!/usr/bin/env python
# coding: utf-8

# In[29]:


import requests, shutil
import json
import csv
from collections import defaultdict
from datetime import datetime, timedelta
import os

# Global constants
AUTHKEY = ""

HEADERS = {
    "accept": "application/json",
    "Authorization": AUTHKEY
}

QUERY_DELTA_MINUTES = 30
DATA_DELTA = 1

OUTFILE = 'SHEF_ENCODED_FDEP.txt'
CONFIGFILE = './config/config.json'

BASE_URL = "https://dashboard.hohonu.io/api/v1"

PROJECT_ENDPOINT = "/stations/{}/waterlevel"

START_DATE = '2024-09-17 10:00:00'
END_DATE = '2024-09-17 10:59:59'

clean_start_date = START_DATE.replace(' ', '_').replace(':', '')
clean_end_date = END_DATE.replace(' ', '_').replace(':', '')


# In[30]:


def write_shef(data, cData, startTime):
    dataOut = ""
    noData = ""

    if (QUERY_DELTA_MINUTES == 15):
        if(startTime.minute in [0,30]):
            fullCount = 3
        else:
            fullCount = 2
    else:
        fullCount = 5

    for site in data:
        print(site)
        dataString = ""
        # If site has not data, continue to next station
        if (len(site['data']['waterlevel']) == 0):
            print("No data for site: " + site['meta']['location'])
            continue

        initTime = startTime

        # Create empty dictionary of missing data times to match data to
        dataDict = {}
        for i in range(0, 30):
            dataDict[(startTime + timedelta(minutes=i)).strftime('%Y-%m-%dT%H:%M:00')] = 'M'
        for level in site['data']['waterlevel']:
            if(cData[site['meta']['station_id']]['correction']):
                print('Applying Correction')
                dataDict[level['t'][0:16]+':00'] = str(round(float(level['o']) + cData[site['meta']['station_id']]['delta'], 2))
            else:
                print('No Correcton applied')
                dataDict[level['t'][0:16]+':00'] = float(level['o'])

        if(cData[site['meta']['station_id']]['datum'] == "MHHW"):
            gageCode = "HC"
        elif (cData[site['meta']['station_id']]['correction']):
            gageCode = "HC"
        else:
            gageCode = "HG"
        dataArray = []
        for i in range(0,30):
            dataArray.append(dataDict[(startTime + timedelta(minutes=i)).strftime('%Y-%m-%dT%H:%M:00')])

        #print(dataDict)
        #print(dataArray)

        lineCount = 0
        batch_size = 7
        for i in range(0,len(dataArray),batch_size):
            batch = dataArray[i:i + batch_size]
            for s in range(0,len(batch)):
                if (lineCount > 0 and s == 0):
                    dataString += ("\n.E" + str(lineCount) + " /" + str(batch[s]))
                else:
                    dataString += ("/" + str(batch[s]))
            lineCount += 1
        

#        if(len(site['data']['waterlevel']) == fullCount):
#            print("Complete Data Found")
#            dataString = [("/" + str(reading['o'])) for reading in site['data']['waterlevel']]
#            initTime = datetime.strptime(site['data']['waterlevel'][0]['t'], '%Y-%m-%dT%H:%M:%SZ')
#        else:
#            print("Possible Missing Data")
#            initTime = datetime.strptime(site['data']['waterlevel'][0]['t'], '%Y-%m-%dT%H:%M:%SZ')
#            dataString = [("/" + str(reading['o'])) for reading in site['data']['waterlevel']]
#            for i in range(fullCount-len(site['data']['waterlevel'])):
#                dataString.append("/M")


        if (site['meta']['station_id'] in cData) and (site['meta']['station_id'] != cData[site['meta']['station_id']]["NWSLI"]):
            dataOut += (".E %s %s Z DH%s/%sIRP/DIN01%s : %s\n" % (cData[site['meta']['station_id']]["NWSLI"], initTime.strftime("%Y%m%d"),initTime.strftime("%H%M"),gageCode,''.join(dataString),site['meta']['location']))
        else:
            noData += (".E %s %s Z DH%s/%sIRP/DIN01%s : %s\n" % (cData[site['meta']['station_id']]["NWSLI"], initTime.strftime("%Y%m%d"),initTime.strftime("%H%M"),gageCode,''.join(dataString),site['meta']['location']))
    print(dataOut)
    print(noData)
    return dataOut
    
def round_to_previous_quarter_hour(dt):
    minutes_past_hour = dt.minute
    minutes_to_subtract = minutes_past_hour % QUERY_DELTA_MINUTES
    rounded_dt = dt.replace(
        minute=minutes_past_hour - minutes_to_subtract,
        second=0,
        microsecond=0
    )
    return rounded_dt


# In[31]:


if __name__ == "__main__":
    now = datetime.utcnow()
    #START_DATE = '2024-09-17 10:00:00'
    #END_DATE = '2024-09-17 10:59:59'
    # SET START AND END TIME FOR DATA REQUEST
    endTime = round_to_previous_quarter_hour(now)
    startTime = endTime - timedelta(minutes=QUERY_DELTA_MINUTES)
    endTime = endTime - timedelta(seconds=1)
    END_DATE = endTime.strftime('%Y-%m-%d %H:%M:%S')
    START_DATE = startTime.strftime('%Y-%m-%d %H:%M:00')
    #clean_start_date = START_DATE.replace(' ', '_').replace(':', '')
    #clean_end_date = END_DATE.replace(' ', '_').replace(':', '')


    params = {
        'from' : START_DATE,
        'to'   : END_DATE,
        'units': 'english',
        'datum': 'MHHW',
        'qc_level': 2,
        'predictions': 'false'
    }

    dataArray = []

    with open(CONFIGFILE) as cFile:
        cData = json.load(cFile)
        #print(cData)
    for site in cData.keys():
        params['datum'] = cData[site]['datum']
        print(site + ": " + START_DATE + " TO " + END_DATE)
        theUrl = f"{BASE_URL}{PROJECT_ENDPOINT.format(site)}"
        print(theUrl)
        response = requests.get(theUrl, headers=HEADERS, params=params)
        #print(response.json())
        if("error" not in response.json()):
            dataArray.append(response.json())
        else:
            print(response.json())

    shefData = write_shef(dataArray, cData, startTime)

    shef_filename = "SUAMIARR8TAE.dat"
    full_filename = os.path.join(os.getcwd(), "output", shef_filename)
    shef_fullfilename = os.path.join(os.getcwd(), "output",shef_filename)
    destination = "/data/Incoming"
    oFile = open(full_filename, "w")
    oFile.write("SRUS82 KTAE %s\n" % (now.strftime('%d%H%M'))) # 201430
    oFile.write("RR8TAE\n\n")
    oFile.write(":SHEF ENCODED HOHONU WATER LEVEL NETWORK DATA\n")
    oFile.write(":WATER LEVELS REFERENCED TO MHHW IN FEET (HC)\n")
    oFile.write(":DATA PROVIDED BY HOHONU WATER LEVEL NETWORK\n")
    oFile.write(shefData)
    oFile.close()

    # Copy final RR8 File to /data/Incoming for ingest into AWIPS
    shutil.copy(full_filename, os.path.join(destination, shef_filename))
