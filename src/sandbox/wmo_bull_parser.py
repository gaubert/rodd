'''
Created on Mar 30, 2012

@author: guillaume.aubert@eumetsat.int
'''

# T1 Table
T1_TABLE = {
             "A" : "Analyses",
             "B" : "Addressed message",
             "C" : "Climatic data",
             "D" : "Grid point information (GRID)",
             "E" : "Satellite imagery",
             "F" : "Forecasts",
             "G" : "Grid point information (GRID)",
             "H" : "Grid point information (GRIB)",
             "I" : "Observational data (Binary coded) - BUFR",
             "J" : "Forecast information (Binary coded) - BUFR",
             "K" : "CREX",
             "N" : "Notices", 
             "O" : "Oceanographic information (GRIB)",
             "P" : "Pictorial information (Binary coded)",
             "Q" : "Pictorial information (Binary coded)",
             "S" : "Surface data",
             "T" : "Satellite data",
             "U" : "Upper-air data",
             "V" : "National data",
             "W" : "Warnings",
             "X" : "GRID regional use",
             "Y" : "GRIB regional use",
           }


# B1 table when T1=A
A_B1_TABLE = {
               "C" : { "data_type" : "Cyclone", "code_form" : "[TEXT]"},
               "G" : { "data_type" : "Hydrological/marine", "code_form" : "[TEXT]"},
               "H" : { "data_type" : "Thickness", "code_form" : "[TEXT]"},
               "I" : { "data_type" : "Ice", "code_form" : "FM44 (ICEAN)"},
               "O" : { "data_type" : "Ozone layer", "code_form" : "[TEXT]"},
               "R" : { "data_type" : "Radar", "code_form" : "[TEXT]"},
               "S" : { "data_type" : "Surface", "code_form" : "FM45 (IAC)/FM 46 (IAC FLEET)"},
               "U" : { "data_type" : "Upper air", "code_form" : "FM45 (IAC)"},
               "W" : { "data_type" : "Weather summary", "code_form" : "[TEXT]"},
               "X" : { "data_type" : "Miscellaneous", "code_form" : "[TEXT]"},
             }

# B1 table when T1=C
C_B1_TABLE = {
               "A" : { "data_type" : "Climatic anomalies", "code_form" : "[TEXT]"},
               "E" : { "data_type" : "Monthly means (upper air)", "code_form" : "FM76 (CLIMAT TEMP SHIP)"},
               "H" : { "data_type" : "Monthly means (surface)", "code_form" : "FM72 (CLIMAT SHIP)"},
               "O" : { "data_type" : "Monthly means (ocean areas)", "code_form" : "FM73 (NACLI, CLINP, SPCLI, CLISA, INCLI)"},
               "S" : { "data_type" : "Monthly means (surface)", "code_form" : "FM71 (CLIMAT)"},
               "U" : { "data_type" : "Monthly means (upper air)", "code_form" : "FM75 (CLIMAT TEMP)"},
             }

# B1 table when T1=F
F_B1_TABLE = {
               "A" : { "data_type" : "Aviation area/GAMET/advisories", "code_form" : "FM53 (ARFOR)/[TEXT]"},
               "B" : { "data_type" : "Upper winds and temperatures", "code_form" : "FM50 (WINTEM)"},
               "C" : { "data_type" : "Aerodrome (VT < 12 hours)", "code_form" : "FM51 (TAF)"},
               "D" : { "data_type" : "Radiological trajectory dose", "code_form" : "FM57 (RADOF)"},
               "E" : { "data_type" : "Extended", "code_form" : "[TEXT]"},
               "F" : { "data_type" : "Shipping", "code_form" : "FM 46 (IAC FLEET)"},
               "G" : { "data_type" : "Hydrological", "code_form" : "FM 68 (HYFOR)"},
               "H" : { "data_type" : "Upper-air thickness", "code_form" : "[TEXT]"},
               "I" : { "data_type" : "Iceberg", "code_form" : "[TEXT]"},
               "J" : { "data_type" : "Radio warning service (including IUWDS data)", "code_form" : "[TEXT]"},
               "K" : { "data_type" : "Tropical cyclone advisories", "code_form" : "[TEXT]"},
               "L" : { "data_type" : "Local/area", "code_form" : "[TEXT]"},
               "M" : { "data_type" : "Temperatures extremes", "code_form" : "[TEXT]"},
               "O" : { "data_type" : "Guidance", "code_form" : "[TEXT]"},
               "P" : { "data_type" : "Public", "code_form" : "[TEXT]"},
               "Q" : { "data_type" : "Other shipping", "code_form" : "[TEXT]"},
               "R" : { "data_type" : "Aviation route", "code_form" : "FM 54 (ROFOR)"},
               "S" : { "data_type" : "Surface", "code_form" : "FM 45 (IAC)FM 46 (IAC FLEET)"},
               "T" : { "data_type" : "Aerodrome (VT >= 12 hours)", "code_form" : "FM 51 (TAF)"},
               "U" : { "data_type" : "Upper air", "code_form" : "FM 45 (IAC)"},
               "V" : { "data_type" : "Volcanic ash advisories", "code_form" : "[TEXT]"},
               "W" : { "data_type" : "Winter sports", "code_form" : "[TEXT]"},
               "X" : { "data_type" : "Miscellanous", "code_form" : "[TEXT]"},
               "Z" : { "data_type" : "Shippping area", "code_form" : "FM 61 (MAFOR)"},
             }

N_B1_TABLE = {
               "G" : { "data_type" : "Hydrological", "code_form" : "[TEXT]"},
               "H" : { "data_type" : "Marine", "code_form" : "[TEXT]"},
               "N" : { "data_type" : "Nuclear emergency response", "code_form" : "[TEXT]"},
               "O" : { "data_type" : "METNO/WIFMA", "code_form" : "[TEXT]"},
               "P" : { "data_type" : "Product generation delay", "code_form" : "[TEXT]"},
               "T" : { "data_type" : "TEST MSG [System related]", "code_form" : "[TEXT]"},
               "W" : { "data_type" : "Warning related and/or cancellation", "code_form" : "[TEXT]"},
             }


S_B1_TABLE = {
               "A" : { "data_type" : "Aviation routine reports", "code_form" : "FM15 (METAR)"},
               "B" : { "data_type" : "Radar reports (Part A)", "code_form" : "FM20 (RADOB)"},
               "C" : { "data_type" : "Radar reports (Part B)", "code_form" : "FM20 (RADOB)"},
               "D" : { "data_type" : "Radar reports (Part A & B)", "code_form" : "FM20 (RADOB)"},
               "E" : { "data_type" : "Seismic data", "code_form" : "See Vol I attachement I (SEISMIC)"},
               "F" : { "data_type" : "Atmospherics reports", "code_form" : "FM81 (SFAZI)/FM82 (SFLOC)/FM83 (SFAZU)"},
               "G" : { "data_type" : "Radiological reports", "code_form" : "FM22 (RADREP)"},
               "I" : { "data_type" : "Intermediate synoptic houre", "code_form" : "FM12 (SYNOP)/FM13 (SHIP)"},
               "L" : { "data_type" : "-", "code_form" : "-"},
               "M" : { "data_type" : "Main synoptic hour", "code_form" : "FM12 (SYNOP)/FM13 (SHIP)"},
               "N" : { "data_type" : "Non standard synoptic hour", "code_form" : "FM12 (SYNOP)/FM13 (SHIP)"},
               "O" : { "data_type" : "Oceanographic data", "code_form" : "FM63 (BATHY)/FM64 (TESAC)/FM62 (TRACKOB)"},
               "P" : { "data_type" : "Special aviation weather reports", "code_form" : "FM16 (SPECI)"},
               "R" : { "data_type" : "Hydrological (river) reports", "code_form" : "FM67 (HYDRA)"},
               "S" : { "data_type" : "Drifting buoy reports", "code_form" : "FM18 (DRIFTER)"},
               "T" : { "data_type" : "Sea ice", "code_form" : "[TEXT]"},
               
               "U" : { "data_type" : "Snow depth", "code_form" : "[TEXT]"},
               "V" : { "data_type" : "Drifting buoy reports", "code_form" : "[TEXT]"},
               "W" : { "data_type" : "Wave information", "code_form" : "FM65 (WAVEOB)"},
               "X" : { "data_type" : "Miscellaneous", "code_form" : "[TEXT]"},
               "Y" : { "data_type" : "Seismic waveform data", "code_form" : "(any format)"},
               "Z" : { "data_type" : "Sea-level data and deep-ocean tsunami data", "code_form" : "(any alphanumeric format)"}, 
             }


T_B1_TABLE = {
               "B" : { "data_type" : "Satellite orbit parameters", "code_form" : "[TEXT]"},
               "C" : { "data_type" : "Satellite cloud interpretations", "code_form" : "FM85 (SAREP)"},
               "H" : { "data_type" : "Satellite remote upper-air soundings", "code_form" : "FM86 (SATEM)"},
               "R" : { "data_type" : "Clear radiance observations", "code_form" : "FM87 (SARAD)"},
               "T" : { "data_type" : "Sea surface temperatures", "code_form" : "FM88 (SATOB)"},
               "W" : { "data_type" : "Winds and cloud temperatures", "code_form" : "FM88 (SATOB)"},
               "X" : { "data_type" : "Miscellaneous", "code_form" : "[TEXT]"},
             }

# U Upper-air data
U_B1_TABLE = {
               "A" : { "data_type" : "Aircraft reports", "code_form" : "FM41 (CODAR), ICAO (AIREP)"},
               "D" : { "data_type" : "Aircraft reports", "code_form" : "FM42 (AMDAR)"},
               "E" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part D)", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               "F" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part C and D) [National and bilateral option]", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               "G" : { "data_type" : "Upper wind (Part B)", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/ FM34 (TEMP MOBIL)"},
               "H" : { "data_type" : "Upper wind (Part C)", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/ FM34 (TEMP MOBIL)"},
               "I" : { "data_type" : "Upper wind (Part A and B)", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/ FM34 (TEMP MOBIL)"},
               "K" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part B)", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               "L" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part C)", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               "M" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part A and B) [National and bilateral option]", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               "N" : { "data_type" : "Rocketsonde reports", "code_form" : "FM39 (ROCOB)/FM40 (ROCOB SHIP)"},
               "P" : { "data_type" : "Upper wind (Part A)", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/FM34 (PILOT MOBIL)"},
               "Q" : { "data_type" : "Upper wind (Part D)", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/FM34 (PILOT MOBIL)"},
               "R" : { "data_type" : "Aircraft report", "code_form" : "[NATIONAL*] (RECCO)"},
               "S" : { "data_type" : "Upper-level pressure, temperature, humidity and wind (Part A)", "code_form" : "FM35 (TEMP)/FM36 (TEMP SHIP)/ FM38 (TEMP MOBIL)"},
               
               "T" : { "data_type" : "Aircraft report", "code_form" : "FM41 (CODAR)"},
               "X" : { "data_type" : "Miscellaneous", "code_form" : "[TEXT]"},
               "Y" : { "data_type" : "Upper wind (Part C and D) [National and bilateral option]", "code_form" : "FM32 (PILOT)/FM33 (PILOT SHIP)/ FM34 (TEMP MOBIL)"},
               "Z" : { "data_type" : "Upper-level pressure, temperature, humidity and wind from a sonde released by carrier balloon or aircraft (Parts A, B, C, D)", "code_form" : "FM37 (TEMP DROP)"},
             }

# W warnings
W_B1_TABLE = {
               "A" : { "data_type" : "AIRMET", "code_form" : "[TEXT]"},
               "C" : { "data_type" : "Tropical cyclone (SIGMET)", "code_form" : "[TEXT]"},
               "E" : { "data_type" : "Tsunami", "code_form" : "[TEXT]"},
               "F" : { "data_type" : "Tornado", "code_form" : "[TEXT]"},
               "G" : { "data_type" : "Hydrological/river flood", "code_form" : "[TEXT]"},
               "H" : { "data_type" : "Marine/coastal flood", "code_form" : "[TEXT]"},
               "O" : { "data_type" : "Other", "code_form" : "[TEXT]"},
               "S" : { "data_type" : "SIGMET", "code_form" : "[TEXT]"},
               "T" : { "data_type" : "Tropical cyclone (Typhoon/hurricane)", "code_form" : "[TEXT]"},
               "U" : { "data_type" : "Severe thunderstorm", "code_form" : "[TEXT]"},
               "V" : { "data_type" : "Volcanic ash clouds (SIGMET)", "code_form" : "[TEXT]"},
               "W" : { "data_type" : "Warnings and weather summary", "code_form" : "[TEXT]"},
              }


B2_TABLE = {
             "A" : { "data_type" : "Radar data"},
             "B" : { "data_type" : "Cloud"},
             "C" : { "data_type" : "Vorticity"},
             "D" : { "data_type" : "Thickness (relative topography)"},
             "E" : { "data_type" : "Precipitation"},
             "F" : { "data_type" : "-"},
             "G" : { "data_type" : "Divergence"},
             "H" : { "data_type" : "Height"},
             "I" : { "data_type" : "-"},
             "J" : { "data_type" : "Wave height + combinations"},
             "K" : { "data_type" : "Swell height + combinations"},
             "L" : { "data_type" : "-"},
             "M" : { "data_type" : "For national use"},
             "N" : { "data_type" : "Radiation"},
             "O" : { "data_type" : "Vertical velocity"},
             "P" : { "data_type" : "Pressure"},
             "Q" : { "data_type" : "Wet bulb potential temperature"},
             "R" : { "data_type" : "Relative humidity"},
             "S" : { "data_type" : "-"},
             "T" : { "data_type" : "Temperature"},
             "U" : { "data_type" : "Eastward wind component"},
             "V" : { "data_type" : "Northward wind component"},
             "W" : { "data_type" : "Wind"},
             "X" : { "data_type" : "-"},
             "Y" : { "data_type" : "-"},
             "Z" : { "data_type" : "Not assigned"},     
           }

B3_TABLE = {
             "N" : { "data_type" : "Satellite data"},
             "O" : { "data_type" : "Oceanographic/limnographic (water property)"},
             "P" : { "data_type" : "Pictorial"},
             "S" : { "data_type" : "Surface/sea level"},
             "T" : { "data_type" : "Text (plain language information"},
             "U" : { "data_type" : "Upper-air data"},
             "X" : { "data_type" : "Other data types"},
           }

B4_TABLE = {
             "D" : { "data_type" : "Depth"},
             "E" : { "data_type" : "Ice concentration"},
             "F" : { "data_type" : "Ice thickness"},
             "G" : { "data_type" : "Ice drift"},
             "H" : { "data_type" : "Ice growth"},
             "I" : { "data_type" : "Ice convergence/divergence"},
             "Q" : { "data_type" : "Temperature anomaly"},
             "R" : { "data_type" : "Depth anomaly"},
             "S" : { "data_type" : "Salinity"},
             "T" : { "data_type" : "Temperature"},
             "U" : { "data_type" : "Current component"},
             "V" : { "data_type" : "Current component"},
             "W" : { "data_type" : "Temperature warming"},
             "X" : { "data_type" : "Mixed data"},
           }

B5_TABLE = {
             "C" : { "data_type" : "Cloud top temperature"},
             "F" : { "data_type" : "Fog"},
             "I" : { "data_type" : "Infrared"},
             "S" : { "data_type" : "Surface temperature"},
             "V" : { "data_type" : "Visible"},
             "W" : { "data_type" : "Water vapour"},
             "Y" : { "data_type" : "User specified"},
             "Z" : { "data_type" : "Unspecified"},
           }


B6_TABLE = {
             "A" : { "data_type" : "Radar data"},
             "B" : { "data_type" : "Cloud"},
             "C" : { "data_type" : "Clear air turbulence"},
             "D" : { "data_type" : "Thickness (relative topography)"},
             "E" : { "data_type" : "Precipitation"},
             "F" : { "data_type" : "Aerological diagrams (Ash cloud)"},
             "G" : { "data_type" : "Significant weather"},
             "H" : { "data_type" : "Height"},
             "I" : { "data_type" : "Ice flow"},
             "J" : { "data_type" : "Wave height + combinations"},
             "K" : { "data_type" : "Swell height + combinations"},
             "L" : { "data_type" : "Plain language"},
             "M" : { "data_type" : "For national use"},
             "N" : { "data_type" : "Radiation"},
             "O" : { "data_type" : "Vertical velocity"},
             "P" : { "data_type" : "Pressure"},
             "Q" : { "data_type" : "Wet bulb potential temperature"},
             "R" : { "data_type" : "Relative humidity"},
             "S" : { "data_type" : "Snow cover"},
             "T" : { "data_type" : "Temperature"},
             "U" : { "data_type" : "Eastward wind component"},
             "V" : { "data_type" : "Northward wind component"},
             "W" : { "data_type" : "Wind"},
             "X" : { "data_type" : "Lifted index"},
             "Y" : { "data_type" : "Observational plotted chart"},
             "Z" : { "data_type" : "Not assigned"},
             
           }

T1_to_T2_MAPPING = {
                 #   T1  : T2
                     "A" : A_B1_TABLE,
                     "C" : C_B1_TABLE,
                     "F" : F_B1_TABLE,
                     "N" : N_B1_TABLE,
                     "S" : S_B1_TABLE,
                     "T" : T_B1_TABLE,
                     "U" : U_B1_TABLE,
                     "W" : W_B1_TABLE,
                     "D" : B2_TABLE,
                     "G" : B2_TABLE,
                     "H" : B2_TABLE,
                     "X" : B2_TABLE,
                     "Y" : B2_TABLE,
                     "I" : B3_TABLE,
                     "J" : B3_TABLE,
                     "O" : B4_TABLE,
                     "E" : B5_TABLE,
                     "P" : B6_TABLE,
                     "Q" : B6_TABLE
                   }

C1_TABLE  = {
              "AA" : "Antartic",
              "AB" : "Albania",
              "AG" : "Argentina"
            }


C6_TABLE = {
            # T1T2A1 -> 
             "INA" : { "data_type" : "Satellite data (AMSUA)", "TAC": None, "subcategory" : "003/003"},
             "INB" : { "data_type" : "Satellite data (AMSUB)", "TAC": None, "subcategory" : "003/004"}, 
             "INH" : { "data_type" : "Satellite data (HIRS)" , "TAC": None, "subcategory" : "003/005"}, 
             "INM" : { "data_type" : "Satellite data (MHS)"  , "TAC": None, "subcategory" : "003/006"}, 
             
             "IOB" : { "data_type" : "Buoy Observations", "TAC": "BUOY", "subcategory" : "001/025"},
             "IOI" : { "data_type" : "Sea Ice", "TAC": None, "subcategory" : None}, 
             "IOP" : { "data_type" : "Sub-surface profiling floats", "TAC": "TESAC", "subcategory" : "031/004"},
             "IOR" : { "data_type" : "Sea surface observations", "TAC": "TRACKOB", "subcategory" : "031/001"}, 
             "IOS" : { "data_type" : "Sea surface and below soundings", "TAC": "BATHY,TESAC", "subcategory" : "031/005"}, 
             "IOT" : { "data_type" : "Sea surface temperature",}, 
             "IOW" : { "data_type" : "Sea surface waves", "TAC": "WAVEOB", "subcategory" : "031/002"}, 
             "IOX" : { "data_type" : "Other sea environmental", "TAC": "WAVEOB", "subcategory" : "031/002"}, 
             
             "IPC" : { "data_type" : "Radar composite imagery data", "TAC": None, "subcategory" : None}, 
             "IPI" : { "data_type" : "Satellite imagery data", "TAC": None, "subcategory" : None}, 
             "IPR" : { "data_type" : "Radar imagery data", "TAC": None, "subcategory" : None}, 
             "IPX" : { "data_type" : "Not defined", "TAC": None, "subcategory" : None}, 
            
             "ISA" : [
                      { "ii": range(01,29+1), "data_type" : "Routinely scheduled observations for distribution from automatic (fixed or mobile) land stations (e.g. 0000, 0100, ... or 0220, 0240, 0300, ..., or 0715, 0745, ... UTC)", "TAC": None, "subcategory" : "000/006"},
                      { "ii": range(30,59+1), "data_type" : "N-minute observations from automatic (fixed or mobile) land stations", "TAC": None, "subcategory" : "000/007"},
                     ],
                     
             "ISB"  : { "data_type" : "Radar reports (parts A and B)", "TAC": "RADOB", "subcategory" : "006/003"}, 
           }

T1_to_A1_MAPPING = {
                      
                     "I" : C6_TABLE
                    
                   }



class WMOBullParser(object):
    '''
       WMO Bull Parser
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def parse_header(self, header_str):
        """
           parse a bulletin header
        """
        
        T1 = header_str[0]
        T2 = header_str[1]
        
        t1_desc = T1_TABLE.get(T1, None)
        
        if not t1_desc:
            raise Exception("T1 %s doesn't exists" % (T1))
        
        t2_table = T1_to_T2_MAPPING.get(T1, None)
        
        if not t2_table:
            raise Exception("No T2 mapping for T1" % (T1))
        
        t2_desc = t2_table.get(T2, None)
        
        if not t2_desc:
            raise Exception("combination %s%s is not reference in GTS manual" % (T1,T2))
        
        print("T1 description = %s, T2 description = %s \n" %(t1_desc, t2_desc))
        
        
        
if __name__ == '__main__':
    
    parser = WMOBullParser()
    
    parser.parse_header("INMX04EUMP")
        