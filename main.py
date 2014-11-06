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
from HSH.Data.js import load_js
from HSH.Misc.logger import Log
import numpy as np, pandas as pd
import sqlite3
import math

log = Log()
conn = sqlite3.connect("geopop.db")
c = conn.cursor()

def create_table():
    """准备数据计算所需要的数据库
    
    每个栅格我们所需要的属性有：
    中心坐标 
        center_la, center_lg 小数点后保留四位，字符串格式。用于作为字符主键进行O(1)的定位
    中心坐标的浮点数形式 
        center_la_f, center_lg_f 浮点数格式。用于作为Select Where 进行数值上的查找，需要建立索引
    四角坐标
        corner1_la, corner1_lg - corner4_la, corner4_lg。用于判定此栅格是否在多边形内部
    区域面积
        area栅格创建时就是以resolution ** 2的规模创建的
    区域人口总数
        population，从人口普查数据中填充进来
    """
    try:
        cmd = \
        """
        CREATE TABLE gridmap (
        center_la TEXT NOT NULL, center_lg TEXT NOT NULL,
        center_la_f REAL NOT NULL, center_lg_f REAL NOT NULL,
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

def length_of_1degree_longitutde(latitude):
    """在不同纬度上，1经度的mile数"""
    return math.cos(math.pi*latitude/180.0) * 69.17056598823741

def bounded_plus(a, b):
    """循环有界加法"""
    if a + b > 180:
        return a + b - 360
    else:
        return a + b

def bounded_minus(a, b):
    """循环有界减法"""
    if a - b < -180:
        return a - b + 360
    else:
        return a - b 

def polygon_area(corners):
    """
    [CN]多边形面积计算器，适用平面坐标
    [EN]polygon_area calculator
    此处由于栅格尺寸很小，可以近似于平面计算
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
    一些常量：
        在任意的经度，纬度上，一纬度差的距离是68.8857854648
        而一经度差的距离是随着纬度变化的，在赤道上最大，为69.1707246778;在北极点最小，为0
    
        la_axis的刻度是均匀的
        而lg_axis的刻度是不均匀的
    
    创建方法：
        resolution是我们设定的栅格边长。设定为10也就是说一个栅格的长，宽都是10mile
        la_resolution是一个栅格的纬度跨越。例如栅格纬度宽为10，而地球上任意位置1纬度都是68.8857...
            所以la_resolution = resolution/68.8857
            
        lg_resolution同理。只不过1经度的跨度跟纬度有关，其值为length_of_1degree_longitutde(latitude)
        
        我们不考虑纬度为 -90 ~ -85 和 85 ~ 90 的北极点和南极点。所以纬度范围是 -85 ~ 85，经度范围是
        -180 ~ 180
    """
    resolution = 10.0 # 划分为变长为10mile的小栅格
    la_resolution = resolution/68.8857854648
    la_axis = np.arange(-85, 85, la_resolution)
    
    for la in la_axis: # la = center_la in db
        miles_per_lg = length_of_1degree_longitutde(la)
        lg_resolution = resolution/miles_per_lg
        lg_axis = np.arange(-180, 180, lg_resolution)
        for lg in lg_axis: # lg = center_lg in db
            center_la, center_lg = la, lg # 中心点
            corner1_la, corner1_lg = (bounded_plus(center_la, la_resolution/2), # 左上角顶点
                                      bounded_minus(center_lg, lg_resolution/2))
            
            corner2_la, corner2_lg = (bounded_minus(center_la, la_resolution/2), # 左下角顶点
                                      bounded_minus(center_lg, lg_resolution/2))
            
            corner3_la, corner3_lg = (bounded_minus(center_la, la_resolution/2), # 右下角顶点
                                      bounded_plus(center_lg, lg_resolution/2))
            
            corner4_la, corner4_lg = (bounded_plus(center_la, la_resolution/2), # 右上角顶点
                                      bounded_plus(center_lg, lg_resolution/2))
                                 
            c.execute("INSERT INTO gridmap VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      ("%.4f" % center_la, "%.4f" % center_lg,
                       center_la, center_lg,
                       corner1_la, corner1_lg,
                       corner2_la, corner2_lg,
                       corner3_la, corner3_lg,
                       corner4_la, corner4_lg,
                       100, 0))
        print("la = %s complete!" % la)
    c.execute("CREATE INDEX coordinate_index ON gridmap (center_la_f, center_lg_f)") # 为浮点数的坐标建立索引
    conn.commit()

def find_closest_grid(la, lg):
    """给一个任意的坐标，找到最近的栅格的中心点
    """
    resolution = 10.0 # 取得某些常量
    la_resolution = resolution/68.8857854648
    
    nearest_la = (round((la + 85)/la_resolution)) * la_resolution - 85 # 找到最近的栅格的纬度
    
    miles_per_lg = length_of_1degree_longitutde(nearest_la) # 取得某些常量
    lg_resolution = resolution/miles_per_lg
    
    nearest_lg = (round((lg + 180)/lg_resolution)) * lg_resolution - 180 # 找到最近的栅格的经度
    return "%.4f" % nearest_la, "%.4f" % nearest_lg

def find_4closest_grid(la, lg):
    """给一个任意的坐标，找到最近的4个栅格的中心点
    """
    resolution = 10.0 # 取得某些常量
    la_resolution = resolution/68.8857854648
    
    nearest_la1 = (math.floor((la + 85)/la_resolution)) * la_resolution - 85
    miles_per_lg = length_of_1degree_longitutde(nearest_la1)
    lg_resolution = resolution/miles_per_lg
    nearest_lg1 = (math.floor((lg + 180)/lg_resolution)) * lg_resolution - 180

    nearest_la2 = (math.floor((la + 85)/la_resolution)) * la_resolution - 85
    miles_per_lg = length_of_1degree_longitutde(nearest_la2)
    lg_resolution = resolution/miles_per_lg
    nearest_lg2 = (math.ceil((lg + 180)/lg_resolution)) * lg_resolution - 180
    
    nearest_la3 = (math.ceil((la + 85)/la_resolution)) * la_resolution - 85
    miles_per_lg = length_of_1degree_longitutde(nearest_la3)
    lg_resolution = resolution/miles_per_lg
    nearest_lg3 = (math.ceil((lg + 180)/lg_resolution)) * lg_resolution - 180
    
    nearest_la4 = (math.ceil((la + 85)/la_resolution)) * la_resolution - 85
    miles_per_lg = length_of_1degree_longitutde(nearest_la4)
    lg_resolution = resolution/miles_per_lg
    nearest_lg4 = (math.floor((lg + 180)/lg_resolution)) * lg_resolution - 180
    
    return (("%.4f" % nearest_la1, "%.4f" % nearest_lg1),
            ("%.4f" % nearest_la2, "%.4f" % nearest_lg2),
            ("%.4f" % nearest_la3, "%.4f" % nearest_lg3),
            ("%.4f" % nearest_la4, "%.4f" % nearest_lg4))

def fill_population():
    """fill cencus data to grid blocks
    """
    df = pd.read_csv(r"dataset\Mean_BG.txt", header = 0, index_col = False)
    ct1 = df["POPULATION"].map(lambda x: x > 0)
    df = df[ct1]
    for la, lg, pop in zip(df["LATITUDE"].values, df["LONGITUDE"].values, df["POPULATION"]):
        la, lg = find_closest_grid(float(la), float(lg)) # 取得最近的栅格，把人口数赋值加上去
        current_pop = c.execute("""SELECT population FROM gridmap WHERE center_la = '%s' 
        AND center_lg = '%s'""" % (la, lg)).fetchall()[0][0]
        c.execute("UPDATE gridmap SET population = %s WHERE center_la = '%s' AND center_lg = '%s'" % (pop + current_pop, la, lg))
    conn.commit() 

""" GEO functions
"""

def centroid(polygon):
    """return the centroid latitude and longitude of a polygon"""
    la, lg = zip(*polygon)
    return sum(la)/len(la), sum(lg)/len(lg)

def point_inside_polygon(x,y,poly):
    """classify a point as being inside a polygon"""
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def polygon_info(polygon):
    """
    argv
    ----
        polygon, corners' latitude and longitude pair
        
    returns
    -------
        population
        area
        density
        
    通过计算多边形内部有多少个栅格，获得面积
    通过统计在多边形内部的栅格的人口，获得人口
    人口密度 = 人口/面积
    
        多边形面积的统计方法：
        对于每个栅格
            1. 如果四个角都在多边形内，则算1格
            2. 如果四个角都不在多边形内，则算0格
            3. 如果四个角部分在多边形内，则算0.5格
    
    当多边形面积过小时候，以上方法效果并不好。本函数采用如下方法替代：
        计算多边形的质心，找到离质心最近的4个栅格，并用这4个栅格的人口总数/总面积作为人口密度
    """    
    
    la, lg = zip(*polygon) # 取得顶点坐标的极值
    c.execute("""SELECT corner1_la, corner1_lg, corner2_la, corner2_lg, corner3_la, corner3_lg,
    corner4_la, corner4_lg, population FROM gridmap WHERE center_la_f BETWEEN %s AND %s AND
    center_lg_f BETWEEN %s AND %s;""" % (min(la), max(la), min(lg), max(lg) ) )
    area, population = 0, 0
    for la1, lg1, la2, lg2, la3, lg3, la4, lg4, pop, in c.fetchall():
        flag = sum( [point_inside_polygon(la1, lg1, polygon),
                     point_inside_polygon(la2, lg2, polygon),
                     point_inside_polygon(la3, lg3, polygon),
                     point_inside_polygon(la4, lg4, polygon) ] )
        if flag == 4: # 完全在内部
            area += 100
            population += pop
        elif flag >= 1: # 部分在内部
            area += 50 # 面积/2
            population += pop/2.0 # 人口/2

    try:
        return population, area, float(population)/area
    except: # area 一定是等于0，那么取最近的栅格的人口为准
        log.write("%s" % polygon, "polygon error")
        population = 0
        centroid_la, centroid_lg = centroid(polygon)
        for la, lg in find_4closest_grid(centroid_la, centroid_lg):
            c.execute("""SELECT population FROM gridmap WHERE center_la = '%s' 
            AND center_lg = '%s';""" % (la, lg))
            population += c.fetchall()[0][0]
        return -1, -1, population/400.0

if __name__ == "__main__":
#     create_table()
#     gridmap()
#     fill_population()
#     print(find_4closest_grid(32.41, 102.43))

    jsonfile = load_js(r"dataset\32229polygons.json") # 读取数据
    with open("density.txt", "w") as f:
        res = list()
        for polygon in jsonfile:
            area, population, density = polygon_info(polygon)
            print(area, population, density)
            res.append("%.4f" % density)
        f.write("\n".join(res)) # 把密度写入数据