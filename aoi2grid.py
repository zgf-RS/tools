from shapely.geometry import box
import geopandas as gpd
import numpy as np
# 根据省的边界划分格网（输入格网尺度,单位为度）
def getGridByAOI(AOI, scale):
    # 获取外接矩形的左下角和右上角坐标
    minx, miny, maxx, maxy = AOI.bounds
    # 根据格网尺度划分格网
    grid = []
    xlist = np.linspace(minx, maxx, num=int((maxx - minx) / scale) + 1)
    ylist = np.linspace(miny, maxy, num=int((maxy - miny) / scale) + 1)
    for x in xlist:
        for y in ylist:
            if AOI.intersects(box(x, y, x + scale, y + scale)):
                grid.append([x, y, x + scale, y + scale])
    return grid

def getGridByAOIint(AOI, scale):
    # 获取外接矩形的左下角和右上角坐标
    minx, miny, maxx, maxy = AOI.bounds
    # 根据格网尺度划分格网
    grid = []
    xlist = np.linspace(int(minx), int(maxx), num=(int(maxx)+1-int(minx)) // scale)
    ylist = np.linspace(int(miny), int(maxy), num=int(maxy)+1-int(miny) // scale)
    for x in xlist:
        for y in ylist:
            if AOI.intersects(box(x, y, x + scale, y + scale)):
                grid.append([x, y, x + scale, y + scale])
    return grid
# 返回格网的对角点列表

if __name__ == "__main__":
    sheng = gpd.read_file('/Users/zgf/Downloads/同步空间/毕业设计/林草系统图斑爬虫/依赖文件/省边界/2023年省级.shp')
    
    scale = 1
    shengming = '广西壮族自治区'
    AOI = sheng[sheng['省']==shengming]['geometry'].values[0]
    
    grid = getGridByAOIint(AOI, scale)
    print(grid)
    