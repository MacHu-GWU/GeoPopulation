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

###解决方案1









-------
**待编辑内容**
可用资源：
	www.census.gov
		Centers of Population = http://www.census.gov/geo/reference/centersofpop.html

	美国领土边界

系统实现架构和方法:
	1. 美国领土分块
	2. 分块计算人口数量
	3. 多边形面积，质心计算
	4. 多边形分割，计算多边形在地图上占了哪些格子
	5. 数据库的设计，和算法的设计
	6. query的时间复杂度分析

应用：
	应用1. 
		Charlie的会议论文需要
		NWS数据中有大量的多边形，需要计算出人口密度
	应用2.
		DTA数据是闪电云数据
		闪电云所影响的多边形区域内，如果闪电云的闪电能量以及闪电概率综合指标很高，说明这个闪电云的影响很大，那么我们就需要计算出这个区域内的人口密度，来确定这个闪电云的影响

所用算法:
	多边形重叠面积，http://www.iro.umontreal.ca/~plante/compGeom/algorithm.html
	点是否在多边形内，http://geospatialpython.com/2011/01/point-in-polygon.html
	
	
"""
INPUT
-----
    polygon = [(x1, y1), (x2, y2), ..., ] 多边形的顶点坐标
    
    
OUTPUT
------
    population_density

step1. 分析人口普查数据，将其预处理为我们需要的数据格式
    <1> 对于每个数据点，我们根据一定的半径，将其均匀分布到临近的栅格上
        例如半径为10km，那么质心距离离该数据点距离差不到10km的所有栅格
        数量设为N,那么我们将人口除以N均匀分布到临近栅格上
    <2> 如何决定半径
        我们将离数据点最近的那个数据点的距离作为半径
    
    这样均匀化数据点有助于帮助我们提高精度
    
step2. 分析多边形坐标，统计多边形面积，和人口
    多边形面积的统计方法：
    对于每个栅格
        1. 如果四个角都在多边形内，则算1格
        2. 如果四个角都不在多边形内，则算0格
        3. 如果四个角部分在多边形内，则算0.5格

step3. 统计多边形的面积，和多变形内的人口，得到人口密度


类 - 栅格：
    中心坐标 = (x, y)
    顶点坐标 = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    人口数
    栅格面积
"""