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
from lib.js import load_js, dump_js
from lib.logger import Log
from lib.knn import earthdist, dist
from sklearn import neighbors
from matplotlib import pyplot as plt
import numpy as np, pandas as pd
import sqlite3
import math

log = Log()
conn = sqlite3.connect("geopop.db")
c = conn.cursor()

## 栅格常数设定，按照mile划分栅格
grid_resolution = 5.0 # 划分为5mile见方的小栅格
la_resolution = grid_resolution/68.8857854648
la_min, la_max = 17.0, 71.0
lg_min, lg_max = -176, -65.0

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
        area REAL, 
        population INT,
        pop_density REAL,
        is_conus INT,
        PRIMARY KEY (center_la, center_lg) );
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

    ## 创建栅格网点
    la_axis = np.arange(la_min+0.5*la_resolution, # 创建纬度坐标轴
                        la_max, 
                        la_resolution)
    
    for la in la_axis: # la = center_la in db
        miles_per_lg = length_of_1degree_longitutde(la)
        lg_resolution = grid_resolution/miles_per_lg
        
        lg_axis = np.arange(lg_min+0.5*lg_resolution, # 创建经度坐标轴
                            lg_max, 
                            lg_resolution)
       
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
#             print(center_la, center_lg, corner1_la, corner1_lg)
            c.execute("INSERT INTO gridmap VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      ("%.4f" % center_la, "%.4f" % center_lg,  # 字符串化的中心坐标，用于primarykey
                       center_la, center_lg,                    # 浮点数的中心坐标，用于select
                       corner1_la, corner1_lg,                  # 四个顶点的坐标
                       corner2_la, corner2_lg,
                       corner3_la, corner3_lg,
                       corner4_la, corner4_lg,
                       polygon_area([(corner1_la, corner1_lg),  # 栅格面积
                                     (corner2_la, corner2_lg),
                                     (corner3_la, corner3_lg),
                                     (corner4_la, corner4_lg),]) * 68.8857854648 * length_of_1degree_longitutde(la), 
                       0,                                       # 人口，先置0
                       0,                                       # 人口密度，先置0
                       0)                                       # 是否是美国本土大陆，先置0
                      )

        print("la = %s complete!" % la)
    c.execute("CREATE INDEX coordinate_index ON gridmap (center_la_f, center_lg_f)") # 为浮点数的坐标建立索引
    conn.commit()

def find_closest_grid(la, lg):
    """给一个任意的坐标，找到最近的栅格的中心点
    """
    nearest_la = (round( (la - (la_min+0.5*la_resolution))/la_resolution ) ) * la_resolution + la_min+0.5*la_resolution # 找到最近的栅格的纬度
    
    miles_per_lg = length_of_1degree_longitutde(nearest_la) # 取得某些常量
    lg_resolution = grid_resolution/miles_per_lg
    nearest_lg = (round( (lg - (lg_min+0.5*lg_resolution))/lg_resolution) ) * lg_resolution + lg_min+0.5*lg_resolution # 找到最近的栅格的经度
    
    return "%.4f" % nearest_la, "%.4f" % nearest_lg

def find_4closest_grid(la, lg):
    """给一个任意的坐标，找到最近的4个栅格的中心点
    """
    nearest_la1 = (math.floor((la - (la_min+0.5*la_resolution))/la_resolution)) * la_resolution + la_min+0.5*la_resolution
    miles_per_lg = length_of_1degree_longitutde(nearest_la1)
    lg_resolution = grid_resolution/miles_per_lg
    nearest_lg1 = (math.floor((lg - (lg_min+0.5*lg_resolution))/lg_resolution)) * lg_resolution + lg_min+0.5*lg_resolution

    nearest_la2 = (math.floor((la - (la_min+0.5*la_resolution))/la_resolution)) * la_resolution + la_min+0.5*la_resolution
    miles_per_lg = length_of_1degree_longitutde(nearest_la2)
    lg_resolution = grid_resolution/miles_per_lg
    nearest_lg2 = (math.ceil((lg - (lg_min+0.5*lg_resolution))/lg_resolution)) * lg_resolution + lg_min+0.5*lg_resolution
    
    nearest_la3 = (math.ceil((la - (la_min+0.5*la_resolution))/la_resolution)) * la_resolution + la_min+0.5*la_resolution
    miles_per_lg = length_of_1degree_longitutde(nearest_la3)
    lg_resolution = grid_resolution/miles_per_lg
    nearest_lg3 = (math.ceil((lg - (lg_min+0.5*lg_resolution))/lg_resolution)) * lg_resolution + lg_min+0.5*lg_resolution
    
    nearest_la4 = (math.ceil((la - (la_min+0.5*la_resolution))/la_resolution)) * la_resolution + la_min+0.5*la_resolution
    miles_per_lg = length_of_1degree_longitutde(nearest_la4)
    lg_resolution = grid_resolution/miles_per_lg
    nearest_lg4 = (math.floor((lg - (lg_min+0.5*lg_resolution))/lg_resolution)) * lg_resolution + lg_min+0.5*lg_resolution
    
    return (("%.4f" % nearest_la1, "%.4f" % nearest_lg1),
            ("%.4f" % nearest_la2, "%.4f" % nearest_lg2),
            ("%.4f" % nearest_la3, "%.4f" % nearest_lg3),
            ("%.4f" % nearest_la4, "%.4f" % nearest_lg4))

def fill_population():
    """fill cencus data to grid blocks
    """
    df = pd.read_csv(r"dataset\rawdata\CenPop2010_Mean_BG.txt", header = 0, index_col = False)
    ct1 = df["POPULATION"].map(lambda x: x > 0)
    df = df[ct1]
    for la, lg, pop in zip(df["LATITUDE"].values, df["LONGITUDE"].values, df["POPULATION"]):
        la, lg = find_closest_grid(float(la), float(lg)) # 取得最近的栅格，把人口数赋值加上去
        
        try:
            current_pop = c.execute("""SELECT population FROM gridmap WHERE center_la = '%s' 
            AND center_lg = '%s'""" % (la, lg)).fetchall()[0][0]        
            c.execute("UPDATE gridmap SET population = %s WHERE center_la = '%s' AND center_lg = '%s'" % (pop + current_pop, la, lg))
        except:
            pass
        print("%s, %s population updated." % (la, lg))
        
    for la, lg, area, pop in c.execute("SELECT center_la, center_lg, area, population FROM gridmap;").fetchall():
        c.execute("UPDATE gridmap SET pop_density = %s WHERE center_la = '%s' AND center_lg = '%s'" % (pop/area, la, lg) )
        
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
    corner4_la, corner4_lg, area, population FROM gridmap WHERE center_la_f BETWEEN %s AND %s AND
    center_lg_f BETWEEN %s AND %s;""" % (min(la), max(la), min(lg), max(lg) ) )
    polygon_area, polygon_population = 0, 0
    for la1, lg1, la2, lg2, la3, lg3, la4, lg4, area, pop, in c.fetchall():
        flag = sum( [point_inside_polygon(la1, lg1, polygon),
                     point_inside_polygon(la2, lg2, polygon),
                     point_inside_polygon(la3, lg3, polygon),
                     point_inside_polygon(la4, lg4, polygon) ] )
        if flag == 4: # 完全在内部
            polygon_area += area
            polygon_population += pop
        elif flag >= 1: # 部分在内部
            polygon_area += area*0.5 # 面积/2
            polygon_population += pop*0.5 # 人口/2

    try:
        return polygon_population, polygon_area, float(polygon_population)/polygon_area
    except: # area 一定是等于0，那么取最近的栅格的人口为准
        log.write("%s" % polygon, "polygon error")
        polygon_area, polygon_population = 0, 0
        centroid_la, centroid_lg = centroid(polygon)
        for la, lg in find_4closest_grid(centroid_la, centroid_lg):
            c.execute("""SELECT area, population FROM gridmap WHERE center_la = '%s' 
            AND center_lg = '%s';""" % (la, lg))
            area, pop = c.fetchall()[0]
            polygon_area += area
            polygon_population += pop
        return -1, -1, polygon_population/polygon_area

def fill_island():
    """判定栅格是否是美国本土大陆
    """
    ### === 按照州的边界，只要在边界内部的，就算作大陆
    boundary = load_js(r"dataset\processed\US_state_boundary_sparse.json")
    for la, lg, population in c.execute("SELECT center_la, center_lg, population from gridmap").fetchall():
             
        flag = 0
        if population > 0: # 如果人口大于0，则直接判定是陆地
            flag = 1
        else:
            for _, polygon in boundary.items():
                is_in_state = point_inside_polygon(float(la), float(lg), polygon)
                if is_in_state: # 只要在某个州里，就算是大陆
                    flag = 1
                    break
            
        if flag: # 如果是大陆
            c.execute("""UPDATE gridmap SET is_conus = 1 WHERE 
            center_la = '{0}' AND center_lg = '{1}';""".format(la, lg))
        else: # 如果不是大陆
            c.execute("""UPDATE gridmap SET is_conus = 0 WHERE 
            center_la = '{0}' AND center_lg = '{1}';""".format(la, lg))
        
    conn.commit()

    ### === 按照水域的数据，只要栅格离水域中心点过近，就不算作大陆
    df = pd.read_csv(r"dataset\rawdata\NLDASmask_UMDunified.asc", sep="\t", header = False, index_col = None)
    df.columns = list("abcde")
    waters = df[df["e"] == 0][["c", "d"]]
    
    ## 选择目前为止，人口为0，但是根据州边界，已经被划入大陆一类的栅格
    for la, lg in c.execute("SELECT center_la, center_lg from gridmap WHERE is_conus = 1 AND population = 0;").fetchall():
        test = np.array([[float(la), float(lg)]]) # grid center coordinate

        ct1 = waters["c"].map(lambda x: abs(x - float(la)) <= 1 )
        ct2 = waters["d"].map(lambda x: abs(x - float(lg)) <= 1 )
        near_waters = waters[ct1 & ct2].values # 只选择栅格点附近的水域点进行对比，节约计算时间
        
        try:
            distances = dist(near_waters, test, earthdist).T[0] # find distance matrix
            nearest_water_index = np.where(distances == distances.min() )[0]
            nearest_water_distance = distances[ nearest_water_index ] # find nearest water distance
             
            grid_radius = grid_resolution * (2.0 ** 0.5) # 栅格半径等于栅格的对角线长
            if nearest_water_distance <= grid_radius: # 说明离栅格很近的地方有水，则设置栅格为不是大陆
                c.execute("""UPDATE gridmap SET is_conus = 0 WHERE 
                center_la = '{0}' AND center_lg = '{1}';""".format(la, lg))
                print(la, lg)
            else:
                print("\t", la, lg)
        except:
            pass
        
    conn.commit()
    
def plot_conus():
    c.execute("""SELECT center_la, center_lg from gridmap WHERE is_conus = 1;""")
    sparse = [(float(la), float(lg)) for la, lg in c.fetchall()]
    la, lg = list(zip(*sparse))
    
    plt.plot(lg, la, ".")
    plt.show()

def plot_population():
    c.execute("""SELECT center_la, center_lg from gridmap WHERE population > 0;""")
    sparse = [(float(la), float(lg)) for la, lg in c.fetchall()]
    la, lg = list(zip(*sparse))
    plt.plot(lg, la, ".")
    plt.show()

def plot_population_contour():
    from matplotlib.colors import BoundaryNorm
    from matplotlib.ticker import MaxNLocator
    
#     print(c.execute("SELECT count(*) FROM (SELECT distinct center_la from gridmap)").fetchall()) # 744
#     print(c.execute("SELECT count(*) FROM (SELECT distinct center_lg from gridmap)").fetchall()) # 566911 因为经度不均匀
    
    c.execute("""SELECT center_la, center_lg, pop_density from gridmap;""")
    sparse = [(float(la), float(lg), pop_density) for la, lg, pop_density in c.fetchall()]
    la, lg, pop_density = list(zip(*sparse)) # 104, 236
    
    dx, dy = 0.005, 0.005
    x = np.array(la).reshape(855, 926)
    y = np.array(lg).reshape(855, 926)
    z = np.array(pop_density).reshape(855, 926)
    z[np.where(z <= 0.1)] = -54000
    
    levels = MaxNLocator(nbins=30).tick_values(z.min(), z.max())
    print(levels)
    cmap = plt.get_cmap("afmhot")
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
  
    plt.subplot(2, 1, 1)
    plt.pcolormesh(y, x, z, cmap=cmap, norm=norm)
    plt.colorbar()
    plt.axis([y.min(), y.max(), x.min(), x.max()])
    plt.title('pcolormesh with levels')

    
    plt.subplot(2, 1, 2)
    plt.contourf(y + dy / 2.,
                 x + dx / 2., z, levels=levels,
                 cmap=cmap)
    plt.colorbar()
    plt.title('contourf with levels')

    plt.show()
 
def exam():
    print(c.execute("SELECT count(*) from (SELECT * from gridmap);").fetchall())

if __name__ == "__main__":
#     create_table()
#     gridmap()
#     fill_population()
#     fill_island()

#     plot_conus()
#     plot_population()
    plot_population_contour()
    
    exam()
    pass