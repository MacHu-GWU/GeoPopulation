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
from __future__ import print_function
import numpy as np
import sqlite3
import math
import time

conn = sqlite3.connect("geopop.db")
c = conn.cursor()

def create_table():
    """每个栅格我们所需要的属性有：
    中心坐标 center_la, center_lg
    四角坐标 corner1_la, corner1_lg - corner4_la, corner4_lg
    区域面积 area
    人口总数 population
    """
    try:
        cmd = \
        """
        CREATE TABLE gridmap (
        center_la REAL NOT NULL, center_lg REAL NOT NULL,
        corner1_la REAL, corner1_lg REAL,
        corner2_la REAL, corner2_lg REAL,
        corner3_la REAL, corner3_lg REAL,
        corner4_la REAL, corner4_lg REAL,
        area REAL, population INT, PRIMARY KEY (center_la, center_lg) );
        """
        c.execute(cmd)
    except:
        pass
    try:
        c.execute("CREATE TABLE constants (name TEXT unique, value REAL);")
    except:
        pass

create_table()

def length_of_1degree_longitutde(latitude):
    return math.cos(math.pi*latitude/180.0) * 69.17056598823741

def bounded_plus(a, b):
    if a + b > 180:
        return a + b - 360
    else:
        return a + b

def bounded_minus(a, b):
    if a - b < -180:
        return a - b + 360
    else:
        return a - b 

def polygon_area(corners):
    """polygon_area calculator
    """
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area

def gridmap():
    """创建栅格数据库
    在任意的经度，纬度上，一纬度差的距离是68.8857854648
    而一经度差的距离是随着纬度变化的，在赤道上最大，为69.1707246778;在北极点最小，为0
    
    la_resolution经度的长度的里程数 = resolution
    
    la_axis的刻度是均匀的
    而lg_axis的刻度是不均匀的
    """
    resolution = 10.0 # 划分为变长为10mile的小栅格
    la_resolution = resolution/68.8857854648
    la_axis = np.arange(-85, 85, la_resolution)
    
    for la in la_axis:
        miles_per_lg = length_of_1degree_longitutde(la)
        lg_resolution = resolution/miles_per_lg
        lg_axis = np.arange(-180, 180, lg_resolution)
        for lg in lg_axis:
            center_la, center_lg = la, lg # 中心点
            corner1_la, corner1_lg = (bounded_plus(center_la, la_resolution/2), # 左上角顶点
                                      bounded_minus(center_lg, lg_resolution/2))
            
            corner2_la, corner2_lg = (bounded_minus(center_la, la_resolution/2), # 左下角顶点
                                      bounded_minus(center_lg, lg_resolution/2))
            
            corner3_la, corner3_lg = (bounded_minus(center_la, la_resolution/2), # 右下角顶点
                                      bounded_plus(center_lg, lg_resolution/2))
            
            corner4_la, corner4_lg = (bounded_plus(center_la, la_resolution/2), # 右上角顶点
                                      bounded_plus(center_lg, lg_resolution/2))
             
#             area = polygon_area([(corner1_la, corner1_lg),
#                                  (corner2_la, corner2_lg),
#                                  (corner3_la, corner3_lg),
#                                  (corner4_la, corner4_lg),]) * miles_per_lg * 68.8857854648
                                 
            c.execute("INSERT INTO gridmap VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (center_la, center_lg,
                                                                               corner1_la, corner1_lg,
                                                                               corner2_la, corner2_lg,
                                                                               corner3_la, corner3_lg,
                                                                               corner4_la, corner4_lg,
                                                                               100, 0))
        print("la = %s complete!" % la)
    conn.commit()
    
# gridmap()

