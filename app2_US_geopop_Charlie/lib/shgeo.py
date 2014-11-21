##################################
#encoding=utf8                   #
#version =py27, py33             #
#author  =sanhe                  #
#date    =2014-10-29             #
#                                #
#    (\ (\                       #
#    ( -.-)o    I am a Rabbit!   #
#    o_(")(")                    #
#                                #
##################################

"""
Useful funcationality repack from geopy
Import:
    from HSH.Misc.shgeo import dist, ApiKeyManager, geocode_one
"""

from __future__ import print_function
from geopy.geocoders import GoogleV3
from geopy.distance import vincenty
import time
import itertools

class ApiKeyManager(object):
    """Api_key的循环器
    用于每次用self.nextkey来呼叫一个api_key进行使用
    平均使用可用的api_key资源
    """
    def __init__(self, list_of_keys):
        self.list_of_keys = itertools.cycle(list_of_keys)
    
    def nextkey(self):
        return next(self.list_of_keys)
    
class FailedGeocoding(Exception):
    def __init__(self, max_try):
        self.max_try = max_try
        
    def __str__(self):
        return "Tried %s times, but failed to geocode." % self.max_try

def sleep(n):
    """sleep for n seconds"""
    time.sleep(n)
    
def dist(coordinate1, coordinate2, unit = "mile"):
    """Calculate distance
    INPUT: coordinate tuple = (latitude, longitude) in decimal format (not degree)
    Output: distance in mileage, kilometers or feet. Default is mileage.
    """
    distance = vincenty(coordinate1, coordinate2)
    if unit == "mile":
        return distance.miles
    elif unit == "km":
        return distance.kilometers
    elif unit == "feet":
        return distance.feet
    else:
        raise Exception("""Error! please set unit as "mile", "km" or "feet".""")

def geocode_one(address_or_coordinate, api_key, max_try = 1, reverse = False):
    """Return json reply from googleV3 geocoder result of one address
    if it is not able to geocode the address, return None
    """
    engine = GoogleV3(api_key)
    for i in range(max_try): # try #max_try times
        if reverse: # 根据坐标查找
            location = engine.reverse(address_or_coordinate)[0] # 如果出错会返回None
        else: # 根据地址查找
            location = engine.geocode(address_or_coordinate) # 如果出错则会返回None
        if location:
            LOC = location.raw
            return LOC
    raise FailedGeocoding(max_try) # if never success, then raise error

if __name__ == "__main__":
    def unit_test1():
        """calculate distance"""
        cd1 = (38.953165, -77.396170) # EFA
        cd2 = (38.899697, -77.048557) # GWU
        print(dist(cd1, cd2))

#     unit_test1()
    
    def unit_test2():
        api_keys = ["AIzaSyAuzs8xdbysdYZO1wNV3vVw1AdzbL_Dnpk", # sanhe
                    "AIzaSyBfgV3y5z_od63NdoTSgu9wgEdg5D_sjnk", # rich
                    "AIzaSyDsaepgzV7qoczqTW7P2fMmvigxnzg-ZdE", # meng yan
                    "AIzaSyBqgiVid6V2xPZoADmv7dobIfvbhvGhEZA", # zhang tao
                    "AIzaSyBtbvGbyAwiywSdsk8-okThcN3q515GDZQ", # jack
                    "AIzaSyC5XmaneaaRYLr4H0x7HMRoFPgjW9xcu2w", # fenhan
                    "AIzaSyDgM5xmKIjS_nooN_TBRLxrFDypVyON9bU", # Amina
                    "AIzaSyCl95-wDqhxM1CtUzXjvirsAXCU_c1ihu8"] # Ryan
        akm = ApiKeyManager(api_keys)
        for i in range(10):
            print(akm.nextkey())
    
    unit_test2()

    def unit_test3():
        from HSH.Misc.logger import Log
        log = Log()
        api_keys = ["AIzaSyAuzs8xdbysdYZO1wNV3vVw1AdzbL_Dnpk", # sanhe
                    "AIzaSyBfgV3y5z_od63NdoTSgu9wgEdg5D_sjnk", # rich
                    "AIzaSyDsaepgzV7qoczqTW7P2fMmvigxnzg-ZdE", # meng yan
                    "AIzaSyBqgiVid6V2xPZoADmv7dobIfvbhvGhEZA", # zhang tao
                    "AIzaSyBtbvGbyAwiywSdsk8-okThcN3q515GDZQ", # jack
                    "AIzaSyC5XmaneaaRYLr4H0x7HMRoFPgjW9xcu2w", # fenhan
                    "AIzaSyDgM5xmKIjS_nooN_TBRLxrFDypVyON9bU", # Amina
                    "AIzaSyCl95-wDqhxM1CtUzXjvirsAXCU_c1ihu8"] # Ryan
        akm = ApiKeyManager(api_keys)
        address = "hello world, I am a python programmer"
        try:
            data = geocode_one(address, akm.nextkey(), 2)
            print(data)
        except Exception as e:
            log.write(e, e.__class__.__name__)
            
#     unit_test3()