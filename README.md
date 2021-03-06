#Population grid map project
------
##项目所要实现的功能

 1. 以多边形顶点的形式在地图上给一个多边形（通常不超过6边形）。计算：
- 多边形面积
- 多边形内人口总数
- 多边形fuzzy人口密度（有多个不同的定义）
        - 取离区域的质心最近的county或者city的人口密度
        - 取人口总数/区域面积
- 多边形所属区域是否海洋，boolean输出

###解决方案
能找到的数据只有美国统计局的2010年的 [人口普查数据][1]，一共有220355条格式如下的数据：

- 人口
- 纬度
- 经度
- 其余为无用信息


第一步

> 将地球地图分为等长宽的小矩形，记录下矩形的中心坐标，4个顶点的坐标，并存入数据库。使得可以根据栅格的中心坐标，以O(1)的时间复杂度得到栅格信息。

第二步

> 读取人口普查数据库，根据每个统计的人口点坐标，将其人口加到最近的栅格上。这样我们就得到了每个栅格内的人口总数

第三步
> 对于任意给定的多边形。我们可以通过数栅格的方法得到多边形的面积。根据每个栅格的人口数可以很快估计出多边形内的人口。从而得到人口密度。

>       多边形面积的统计方法（经典地图学面积统计数值算法）：
      对于被多边形覆盖到的每个栅格
        1. 如果四个角都在多边形内，则算1格
        2. 如果四个角都不在多边形内，则算0格
        3. 如果四个角部分在多边形内，则算0.5格
当多边形的面积过小，面积不足一个栅格时，前面的算法并不能较好的反映出多边形所在区域的人口密度。所以我们把算法改进为：

>       找到多边形的质心。离质心最近的四个栅格的人口密度的均值作为多边形的人口密度

##项目文件

- dataset/32229polygons.json  **32229个多边形顶点数据**
- dataset/Mean_BG.txt  **220355个人口普查点数据**
- gridmap.db  **sqlite栅格信息数据库**
- main.py  **主python脚本**
- density.txt  **输出的人口密度信息**

##参考资料
- [多边形面积算法](http://en.wikipedia.org/wiki/Shoelace_formula)
- [点是否在多边形内](http://geospatialpython.com/2011/01/point-in-polygon.html)
