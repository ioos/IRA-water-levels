#!/usr/bin/python3

#Script to take ERDDAP tide gauge data, shef encode it, and send it to a staging area 
#to be ingested into AWIPS.
#Maintainer: Matt Strauser, ITO WFO Caribou, ME (Matt.Strauser@noaa.gov)

#Version 1.1, Updated 5/30/2025
#Updated to make the end time request optional for situations where the max time is not accurate
#Users should still set this to True most of the time.

import urllib
import base64
from urllib.request import urlopen, Request
import urllib.request
from urllib.error import URLError
import sys
import os
import string
import time
import json
sys.path.insert(0,'/home/ldad/TideGauges/etc/')
import getTideGaugeData_Config as cfg

#=========================#
# Configuration section.  #
#=========================#
dataDir = cfg.dataDir     # Where data files will be stored. 
pil = cfg.pil
officeName = cfg.officeName
wmoId = cfg.wmoId

# The amount of time to request data, in seconds. 
# Used around line 170 
requestLength = cfg.requestLength 

#-------------------#
# Obs Station info. #
#-------------------#
siteInfo = cfg.siteInfo

#=============================#
# End Configuration section.  #
#=============================#

#============================================================#
#                         getLastTimes()                     # 
# Load the dictionary saved in the file usgsRaven.lasttimes. #
# This dictionary contains the unix time of the last         #
# data sent out for each site ID.  This way we know if we    #
# have down loaded some new data.                            #
#============================================================#
def getLastTime(lastTimeFile):
   
   #-------------------------------------------------#
   # Load the lasttimes dict structure from the file #
   #-------------------------------------------------#
   lastFile=dataDir+lastTimeFile
   print("Last time file: {}".format(lastFile) )
   
   lastTime={}
   try:
      lastTime = eval(open(lastFile).read())
   except:
      print("Could not load last times file.")
       
   return lastTime
   

#============================================================#
#                         makeLastTimes()                    # 
# Create a new .lasttimes file. This file conatains          #
# a dictionary which holds the unixtime of the last          #
# data sent out for each site ID. This way we know if we     #
# have down loaded some new data.                            #
#============================================================#
def makeLastTime(lastTimes, lastTimeFile):
      
   lastFile=dataDir+lastTimeFile
   print("UPDATING Last time file: {}".format(lastFile) )
   try:
      ofile=open(lastFile,'w')
   except IOError (erno,ermsg):
      print("Could not open file: {} -> Error: {}".format(lastFile,ermsg) )
      sys.exit(1)


   ofile.write('{\n')
   numK=len(lastTimes)
   cc=0
   for k,v in lastTimes.items():
      if cc == numK-1:
         char=""
      else:
         char=","
	 	 
      ofile.write("'%s':'%s'%s\n"%(k,v,char))
      cc=cc+1
      
   ofile.write('}\n')
   ofile.close()
   
   return

#============================================================#
#                      startShefFile(mf)                     # 
# opens file Puts the header info into the shef file 'mf'    #
#============================================================#
def startShefFile(mf):      
            
   timenow = time.strftime("%d%H%M", time.gmtime(time.time()))	    
   headerTime2=time.strftime("%I%M %P %Z %a %b %d %Y", time.localtime(time.time()))
   headerTime2 = headerTime2.upper()
 
   if headerTime2[0:1] == "0":
      headerTime2 = headerTime2[1:]
    
   mf.writelines("ZCZC {} ALL\n".format(pil) )
   mf.writelines("{} {} \n".format(wmoId,timenow) )
   mf.writelines(" \n")
   mf.writelines("HYDROMETEOROLOGICAL DATA REPORT\n")
   mf.writelines("NATIONAL WEATHER SERVICE {}\n".format(officeName))
   mf.writelines("{}\n".format(headerTime2))
   mf.writelines(" \n")

   return 

def main():
     
   #----------------------#
   # Set up the timezone. #
   #----------------------#  
   os.environ['TZ']='EST5EDT'  
   time.tzset()
   
   #------------------------------------------------#   
   # Creat the shef file name and open the file for #      
   # output.  If we can't open the file, notify the #
   # user and exit the program.                     #
   #------------------------------------------------#
   shefFname="{}SUA{}.dat.{}".format(dataDir, pil, time.strftime("%d%H%M", time.gmtime(time.time())))   
   shefFnameShort="SUA{}.dat.{}".format(pil, time.strftime("%d%H%M", time.gmtime(time.time())))   
   try:
      sf=open(shefFname,'w')

   except IOError (erno,ermsg):
      print("Could not open file: {} -> Error: {}".format(shefFname,ermsg) )
      sys.exit(1)
   
   print("Shef datta will be saved in: {}".format(shefFname ) )
          
   #------------------------#     
   # some variables we need #
   #------------------------#
   shefFileCreated = False
   shefCreated = False   
   firstOb = True   
      
   for st in siteInfo:
      firstSiteOb = True
      
      ltf = "{}Tide.lasttime".format(siteInfo[st]['siteId'])
      lastTime = getLastTime(ltf)

      if siteInfo[st]['siteId'] in lastTime:      
         thisLastTime = lastTime[siteInfo[st]['siteId']]      
      else:
         thisLastTime = "0"

      print("{} Latstime: {}".format(siteInfo[st]['siteId'],thisLastTime) )
          
      #---------------------------------#
      # Download the data from the web. #
      #---------------------------------#
      #----------------------------------------------#      
      # Make the web url needed to download the data #
      #----------------------------------------------      
      try:
         print("Starting request: {}".format(time.strftime("%I:%M:%S %P %Z %a %b %d %Y", time.localtime(time.time()))))
         requestStartTime =  time.strftime("%Y-%m-%d+%H%%3A%M", time.gmtime(time.time ()- requestLength))
         if siteInfo[st]['EndTimeRequest'] == True:
             requestEndTime =  time.strftime("%Y-%m-%d+%H%%3A%M", time.gmtime(time.time()))
   
         #----------------------------------------------#      
         # Make the web url needed to download the data #
         #----------------------------------------------      
             webUrl = siteInfo[st]['webUrl'].format(requestStartTime, requestEndTime)
         else:
             webUrl = siteInfo[st]['webUrl'].format(requestStartTime)
         print("URL: {}".format(webUrl) )

         header = {"Content-Type":"application/json"}         
         with urllib.request.urlopen( webUrl ) as webpage:
            content = json.loads(webpage.read().decode())
         
         gageDataDates, gageDataValues = [],[]
         WaterLevelUnits = content['table']['columnUnits'][1]

        #convert to feet if the units are in meters
         if WaterLevelUnits == 'm':
            unitConversionFactor = 3.28084
         else:
            unitConversionFactor = 1
            
        #establish column number of time and data:
         if len(content['table']['columnNames']) > 2:
             for j in range(len(content['table']['columnNames'])):
                 if content['table']['columnNames'][j] == "time":
                     timeIndex = j
                     dataIndex = j+1
         else:
             timeIndex = 0
             dataIndex = 1
        
         for i in range(len(content['table']['rows'])):
            if content['table']['rows'][i][1] is not None:
                gageDataDates.append(content['table']['rows'][i][timeIndex])
                gageDataValues.append(round((content['table']['rows'][i][dataIndex]*unitConversionFactor)+siteInfo[st]['datumConversionFactor'],3))
         print("Request complete: {}".format(time.strftime("%I:%M:%S %P %Z %a %b %d %Y", time.localtime(time.time()))))
         print("Request contains {} observations".format(len(gageDataValues)))

      except urllib.error.HTTPError as e:
         print("Error retriving tide data: ", e)    
         continue
        
         
      if len(gageDataValues) <= 0 :
         continue
         
      #--------------------------------------#   
      # Loop through the data and look for   #
      # the most current water level obs.    #
      # If we find data newer than the last  #
      # run through, then create a shef file #
      # and include the news water level obs.#
      # This file will be sent to AWIPS via  #
      # LDAD.                                #
      #--------------------------------------#
      startData=False
      newLastTime=thisLastTime

      for idx, gageDataDate in enumerate(gageDataDates, start=0):
         print("{} {} {}".format(idx, gageDataDate, gageDataValues[idx]))

         if gageDataValues[idx] != None and gageDataValues[idx] != "null":

             #-------------------------------#         
             # get the timestamp of this ob. #
             #-------------------------------#
             obdate = gageDataDate.replace("Z","").replace("-","").split("T")[0]
             obtime = gageDataDate.replace("Z","").replace('-','').replace(':','').split("T")[1][:-2]
             obdatetime = "{}{}".format(obdate, obtime)
             print(obdatetime, obdate, obtime)
                              
             #-------------------------------------------# 
             # if a newer ob, then lets start writing to #
             # a shef file.                              #
             #-------------------------------------------# 
             print(obdatetime,thisLastTime)
             if int(obdatetime) > int(thisLastTime):
                lastTime[siteInfo[st]['siteId']]=obdatetime         
             
                #---------------------------------------#         
                # get the water level                   #
                #---------------------------------------#
                print(gageDataValues[idx])
                level = float(gageDataValues[idx])
                            
                print("date: {} time: {} -> level: {}".format(obdate, obtime, level) )

                #-------------------------------------------#	    
                # If this is the first new data point, then #
                # we need to start a new shef file.         #
                #-------------------------------------------#
                if firstOb==True:
                   firstOb=False
                   if shefFileCreated == False:
                      startShefFile(sf)     
                      shefFileCreated=True
             
                shefCreated=True
          
                if sf and firstOb==False and level:
                   if firstSiteOb == True: 
                      sf.write(":%s\n"%siteInfo[st]['siteName'])
                      firstSiteOb = False
                    
                   outLine=".E %s %s" %(siteInfo[st]['siteId'],obdate)
                   outLine+=" Z DH{}/HMIRZ/DIN+0/{:.2f}".format(obtime,level)
                   sf.write(outLine+"\n")
                   print("{}\n".format(outLine))   

      makeLastTime(lastTime, ltf)	 

      print("\n")
   
   #------------------------------------------#	    
   # Close out the shef product and the file. #
   #------------------------------------------#	    
   if shefCreated==True: 
      sf.write(":\nNNNN\n")
      sf.close()
         
   #----------------------------------------------#      
   # If we found new data, the copy the shef file #   
   # to LDAD directory to prepare for ingest.     #
   #----------------------------------------------#

#Redacted
      	 
   #------#
   # DONE #
   #------#
   print("\n")
   print("***** All Done *****\n\n\n" )
 
 
if __name__ == "__main__":       
   main()
