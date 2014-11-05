from __future__ import print_function
from HSH.Data.js import dump_js

res = list()
with open("polygons_coordinates.txt", "r") as f:
    for line in f.xreadlines():
        points = [int(i)/100.00 for i in line.strip().split(",")]
        res.append(zip(points[::2], points[1::2]))
        
dump_js(res, "32229polygons.json", fastmode = True, replace = True)