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
Mean_BG 人口数据
    人口总量: 312471327
    洲的个数: 52
    
美国地图数据
    纬度 latitude 28 ~ 48
    经度 longitute -125 ~ -67
"""
from __future__ import print_function
from matplotlib import pyplot as plt
from sklearn.neighbors import DistanceMetric
from HSH.Misc.shgeo import dist
import pandas as pd, numpy as np
import time

## columns = STATEFP, COUNTYFP, TRACTCE, BLKGRPCE, POPULATION, LATITUDE, LONGITUDE
# df = pd.read_csv(r"dataset\Mean_BG.txt", header = 0, index_col = False)
# print("US population = %s" % df["POPULATION"].sum())
# print("how many states = %s" % len(df["STATEFP"].unique()))
# print("how many county = %s" % len(df["COUNTYFP"].unique()))
# print(df["LATITUDE"].max(), df["LATITUDE"].min())
# print(df["LONGITUDE"].max(), df["LONGITUDE"].min())

def earthdist(x, y): # latitude, longitude earth surface distance
    return dist((x[0], x[1]), (y[0], y[1]))

def map_view():
    """检视人口数据
    """
    df = pd.read_csv(r"dataset\Mean_BG.txt", header = 0, index_col = False)
    print(df.shape[0])
    ct1 = df["POPULATION"].map(lambda x: x > 0)
    ct2 = df["LATITUDE"].map(lambda x: (x >= 50) and (x <= 75))
    ct3 = df["LONGITUDE"].map(lambda x: (x >= -180) and (x <= - 130))

    df = df[ct1 & ct2 & ct3]
    
    la, lo = df["LATITUDE"].values, df["LONGITUDE"].values
    train = [np.array(i) for i in zip(la, lo)]
    
    dist_cal = DistanceMetric.get_metric(earthdist)
    
    st = time.clock()
    matrix = dist_cal.pairwise(train, train)
    print(time.clock() - st)
    
map_view()