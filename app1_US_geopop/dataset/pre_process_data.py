##encoding=utf8

from __future__ import print_function
import pandas as pd

processed_dir = "processed"

def population_stat_points():
    """美国全国土经纬度范围"""
    df = pd.read_csv(r"rawdata\CenPop2010_Mean_BG.txt", header = 0, index_col = False)
    print(df.columns) # ['STATEFP', 'COUNTYFP', 'TRACTCE', 'BLKGRPCE', 'POPULATION', 'LATITUDE', 'LONGITUDE']
    print(df["LATITUDE"].min(), df["LATITUDE"].max())   # 17.901633 71.300949
    print(df["LONGITUDE"].min(), df["LONGITUDE"].max()) # -175.86004 -65.30086
    
population_stat_points()