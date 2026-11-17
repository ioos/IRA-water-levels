#!/usr/bin/python3
#=========================#
# Configuration section.  #
#=========================#
dataDir = #redacted      # Where data files will be stored. 
pil = "PWMRR8CAR"
officeName = "CARIBOU ME"
wmoId = "SRUS51 KCAR"

# The amount of time to request data, in seconds.  
requestLength = 14400 #Look at the last 4 hours for new data

#-------------------#
# Obs Station info. #
#-------------------#
#datumConversionFactor is the factor to convert from NAVD88 (in feet) to MLLW (in feet). In most cases, this is attained using the NOAA online vdatum conversion tool
siteInfo =     {'HPNM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_GMRI_Pier_Portland_ME.json?time%2Cmllw_meters&time%3E={}&time%3C={}",
                     'siteName' : "GMRI Pier Portland, ME", 'siteId' : "HPNM1", 'tz':'g', 'datumConversionFactor':0},
                'BTBM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Boothbay_Harbor_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "DMR Boothbay, ME", 'siteId' : "BTBM1", 'tz':'g', 'datumConversionFactor':5.48},
                'STGM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Port_Clyde_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Port Clyde St. George, ME", 'siteId' : "STGM1", 'tz':'g', 'datumConversionFactor':5.709},
                'MCSM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Machias_radar.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Machias, ME", 'siteId' : "MCSM1", 'tz':'g', 'datumConversionFactor':6.929},
                'FRPM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Fore_River_Portland_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Fore River, Portland, ME", 'siteId' : "FRPM1", 'tz':'g', 'datumConversionFactor':5.258},
                'CGUM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Chebague_Island_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Chebeague Island, ME", 'siteId' : "CGUM1", 'tz':'g', 'datumConversionFactor':5.023},:w
                'BAHM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Bath_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Kennebec River, Bath, ME", 'siteId' : "BAHM1", 'tz':'g', 'datumConversionFactor':3.32},
                'SCRM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/Hohonu_tide_Scarborough_ME.json?time%2Cnavd88_feet&time%3E={}&time%3C={}",
                     'siteName' : "Scarborough River, Pine Point, ME", 'siteId' : "SCRM1", 'tz':'g', 'datumConversionFactor':4.921},
                'HPMN3' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/ONSET_hamptonbay_hourly_water_level.json?time%2CMLLW_feet&time%3E={}&time%3C={}",
                     'siteName' : "Hampton, NH", 'siteId' : "HPMN3", 'tz':'g', 'datumConversionFactor':0},
                # 'BLFM1' : {'webUrl' : "https://data.neracoos.org/erddap/tabledap/NWS_Hydromet_GYX.json?site_id%2Ctime%2Cnavd_88_meters&site_id=%22BELFAST%22&time%3E={}&time%3C={}",
                     # 'siteName' : "Belfast, ME", 'siteId' : "BLFM1", 'tz':'g', 'datumConversionFactor':5.827},
}                    
#=============================#
# End Configuration section.  #
#=============================#