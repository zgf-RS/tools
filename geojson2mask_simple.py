import glob
import os
from osgeo import gdal
import os
import sys
import numpy as np
import cv2
import geojson
from tqdm import tqdm
import geopandas as gpd
from shapely.geometry import box, shape

def _gt_convert(x_geo, y_geo, geotf):
    a = np.array([[geotf[1], geotf[2]], [geotf[4], geotf[5]]])
    b = np.array([x_geo - geotf[0], y_geo - geotf[3]])
    return np.round(np.linalg.solve(a,
                                    b)).tolist()  # Solve a quadratic equation


# @time_it
# TODO: update for vector2raster
def convert_data(src_img_path, geojson_path, save_path):
    # raster = Raster(src_img_path)
    raster = gdal.Open(src_img_path, gdal.GA_ReadOnly)
    tmp_img = np.zeros((raster.RasterYSize, raster.RasterXSize), dtype=np.uint8)
    # vector to EPSG from raster
    # temp_geojson_path = translate_vector(geojson_path, raster.proj)
    temp_geojson_path = geojson_path
    geojson_src = gpd.read_file(geojson_path)


    geotransform = raster.GetGeoTransform()
    # 计算栅格影像的边界框
    min_x = geotransform[0]
    max_y = geotransform[3]
    max_x = min_x + geotransform[1] * raster.RasterXSize
    min_y = max_y + geotransform[5] * raster.RasterYSize

    # 使用Shapely创建栅格影像的边界框（矩形）
    raster_bbox = box(min_x, min_y, max_x, max_y)
    # 使 spatial_index 进行空间查询
    intersecting_ids = list(geojson_src.sindex.query(raster_bbox, predicate='intersects'))
    interFea = geojson_src.iloc[intersecting_ids].drop_duplicates()
    interFealist = interFea["geometry"]
    # 遍历几何对象，打印它们的坐标
    # for geom in interFea["geometry"]:
    #     coords = list(geom.exterior.coords)  # 获取几何对象的坐标列表
    #     print(coords)
    for geo in tqdm(interFealist):
        # geo = feat["geometry"]
        if geo.geom_type == "Polygon":
            geo_points = list(geo.exterior.coords)

        else:
            raise TypeError(
                "Geometry type must be 'Polygon', not {}.".
                format(geo.geom_type))
        xy_points = np.array([
            _gt_convert(point[0], point[1], raster.GetGeoTransform()) for point in geo_points
        ]).astype(np.int32)
        # TODO: Label category
        cv2.fillPoly(tmp_img, [xy_points], 255)  # Fill with polygons
    # save_geotiff(tmp_img, save_path, raster.GetProjection(), raster.GetGeoTransform())
    # 创建一个GDAL数据集，并将tmp_img作为其波段
    # cv2.imwrite('/home/map/zhangguangfei/data/test.png', tmp_img)
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(save_path, raster.RasterXSize, raster.RasterYSize, 1, gdal.GDT_Byte)

    # 将NumPy数组赋值给数据集的波段
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(tmp_img)

    # 设置输出数据集的投影和地理变换参数
    out_dataset.SetProjection(raster.GetProjection())
    out_dataset.SetGeoTransform(raster.GetGeoTransform())

    # 清理资源
    out_band = None
    out_dataset = None
    raster = None
    print(f"栅格数据已保存到 {save_path}")
    # os.remove(temp_geojson_path)


if __name__ == "__main__":

    basepath = '/Users/zgf/Desktop/planetBasemap/106_21_107_26/bound'
    geojson_path = '/Users/zgf/Desktop/planetBasemap/106_21_107_26/106_21_107_26_3857.geojson'
    save_path = '/Users/zgf/Desktop/planetBasemap/106_21_107_26/labeltif'
    os.makedirs(save_path, exist_ok=True)
    # 使用glob遍历所有文件
    entries = os.listdir(basepath)
    for img_path in tqdm(entries):
        # 获取目录中所有的项
        
        full_path = os.path.join(basepath, img_path)
        if os.path.isfile(full_path):
            print(full_path)
            convert_data(full_path, geojson_path, save_path + '/' + img_path.split('/')[-1])
