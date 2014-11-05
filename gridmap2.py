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
美国地图数据
    纬度 28 ~ 48
    经度 -125 ~ -67

def example1():
    # 纬度不变，经度变化，经线上的距离基本不变
    print([dist((38.085845, lg), (39.085845, lg)) for lg in range(-120, -70)]) 68.98
    # 经度不变，随着纬度的上升，纬线上距离越来越小
    print([dist((la, -102.1234), (la, -103.1234)) for la in range(28, 48)]) 61.12 ～ 47.25

example1()

"""

from __future__ import print_function
from HSH.Data.pk import load_pk, dump_pk
import numpy as np
# import sys
# from HSH.Misc.shgeo import dist
# import math


class Grid(object):
    """
    w_r, h_r 分别是 width的分辨率和height的分辨率
    x_axis, y_axis 分别是栅格中心的经度值，和纬度值列表
    map_value 是栅格的权值，在本project中是人口数值
    """
    def __init__(self, width_resolution, height_resolution):
        self.w_r, self.h_r = width_resolution, height_resolution
        self.x_axis, self.y_axis = ({i: value for i, value in enumerate(np.arange(-180, 180, self.w_r))}, 
                                    {i: value for i, value in enumerate(np.arange(-90, 90, self.h_r))} )
        self.map_value = {"%.4f" % y : {"%.4f" % x : 0 for x in self.x_axis.values()} for y in self.y_axis.values()}

    def closest(self, y, x):
        """找到离 纬度 = y, 经度 = x的点最近的栅格点坐标
        """
        ind_x1, ind_y1 = int((x+180)/self.w_r), int((y+90)/self.h_r)
        ind_x2, ind_y2 = ind_x1 + 1, ind_y1 + 1
#         print(ind_x1, ind_x2, ind_y1, ind_y2)
        lower_x, upper_x, lower_y, upper_y = (self.x_axis[ind_x1], self.x_axis[ind_x2],
                                              self.y_axis[ind_y1], self.y_axis[ind_y2])
        if (x - lower_x) <= self.w_r/2:
            nearest_x = lower_x
        else:
            nearest_x = upper_x

        if (y - lower_y) <= self.h_r/2:
            nearest_y = lower_y
        else:
            nearest_y = upper_y
        return "%.4f" % nearest_y, "%.4f" % nearest_x
    
def unit_test():
    resolution = 10.0 # 1纬度从等于 0 - 100mile不等, 1经度固定等于 68.931 mile
    width, height = resolution/68.9310090506, resolution/54.4613603793
    grid = Grid(width, height)
     
    dump_pk(grid, "grid.p")
    grid = load_pk("grid.p")
    # print(sys.getsizeof(grid.map_value))
    # print(sys.getsizeof(grid.x_axis))
    # print(sys.getsizeof(grid.y_axis))
    # print(grid.closest(38.3478773082, -101.948565) )

if __name__ == "__main__":
    unit_test()
