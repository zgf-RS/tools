# 输入 geojson
# geojson有哪些属性
# 1. 前期影像 后期影像路径
# 给geojson加一个属性 质心(84)
# 质心在4096的哪个像素中
# 裁剪以该像素为中心的一对image（256✖️256）
# 裁剪后 图像与json对应关系


import os
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from rasterio.crs import CRS

import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from rasterio.crs import CRS
from pyproj import Proj, transform

import geopandas as gpd
# 读取GeoJSON
geopath = '/Users/zgf/Downloads/同步空间/毕业设计/tools/test.geojson'
lindi = gpd.read_file(geopath)

def clip_raster_by_bounds(raster_path, center_lon, center_lat, output_path):
    # 定义WGS84坐标系和Web Mercator坐标系
    wgs84 = Proj(init='epsg:4326')
    web_mercator = Proj(init='epsg:3857')
    .centroid.iloc[0]
    # 将WGS84坐标转换为Web Mercator坐标
    x, y = transform(wgs84, web_mercator, center_lon, center_lat)
    with rasterio.open(raster_path) as src:
        pixel_width = src.res[0]  # X 方向的像素分辨率
        pixel_height = src.res[1]  # Y 方向的像素分辨率
    # 计算裁剪区域的边界
    left = x - (256 * pixel_width / 2)
    bottom = y - (256 * pixel_height / 2)
    right = x + (256 * pixel_width / 2)
    top = y + (256 * pixel_height / 2)
    
    # 创建裁剪区域的矩形几何形状
    bbox = box(left, bottom, right, top)
    
    # 打开栅格数据
    with rasterio.open(raster_path) as src:
        # 裁剪栅格数据
        out_image, out_transform = mask(src, [bbox], crop=True)
        
        # 确保裁剪后的影像大小为256x256
        out_image = out_image[0:256, 0:256]
        
        # 更新元数据
        out_meta = src.meta.copy()
        out_meta.update({
            'driver': 'GTiff',
            'height': 256,
            'width': 256,
            'transform': out_transform
        })
        
        # 保存裁剪后的影像
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)

# 使用示例
raster_path = '/Users/zgf/Desktop/planet/q2205/1661-1209_quad.tif'  # 待裁剪的tif文件路径
center_lon = 112.094906  # 中心点经度
center_lat = 31.014514    # 中心点纬度
output_path = 'path_to_output.tif'  # 输出裁剪后的tif文件路径
clip_raster_by_bounds(raster_path, center_lon, center_lat, output_path)