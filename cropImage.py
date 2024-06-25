# 筛选相交json
from osgeo import gdal
from shapely.geometry import box, shape
import geopandas as gpd
import os
from tqdm import tqdm


def crop_image_byPOI(input_tif, output_folder, grid_size, points_of_interest):
    """
    根据兴趣点裁剪GeoTIFF图像。
    
    Args:
        input_tif (str): 输入的GeoTIFF文件路径。
        output_folder (str): 输出文件夹路径。
        grid_size (int): 裁剪图像的网格大小（像素）。
        points_of_interest (dict): 包含兴趣点信息的字典，其中：
            - 'type' (str): 兴趣点类型。
            - 'PK_UID' (str): 兴趣点的唯一标识符。
            - 'x' (list[float]): 兴趣点的X坐标列表（地理坐标）。
            - 'y' (list[float]): 兴趣点的Y坐标列表（地理坐标）。
    
    Returns:
        None: 该函数无返回值，裁剪后的图像将保存在指定的输出文件夹中。
    
    """
    downld = {}
    dataset = gdal.Open(input_tif)
    geotransform = dataset.GetGeoTransform()
    # points_of_interest解析
    type = points_of_interest['type']
    PK_UID = points_of_interest['PK_UID']
    # date = points_of_interest['date']
    # PK_UIDlist = points_of_interest['PK_UID']
    xlist = points_of_interest['x']
    ylist = points_of_interest['y']

    for x, y in zip(xlist, ylist):
        # 将地理坐标转换为像素坐标
        x_pixel = (x- geotransform[0]) / geotransform[1]
        y_pixel = -(geotransform[3] - y) / geotransform[5]
        x_pos = x_pixel - (x_pixel % grid_size)
        y_pos = y_pixel - (y_pixel % grid_size)
        # 裁剪图像
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx * dy == 1 or dx * dy == -1:
                    continue  # 跳过中心格网，只裁剪周围的
                x0 = x_pos + dx * grid_size
                y0 = y_pos + dy * grid_size
                x1 = grid_size
                y1 = grid_size

                # 使用 outputBounds 指定裁剪区域
                outputBounds = [x0, y0, x1, y1]
                isdown = True
                for pos in [x0, y0]:
                    if pos < 0 or pos > (4096 - grid_size):
                        isdown = False
                        break
                posxy = f'{x0}_{y0}'
                if isdown and not posxy in downld:
                    creationOptions = [
                        f'XSIZE={grid_size}', 
                        f'YSIZE={grid_size}'
                    ]
                    downld[posxy] = 1
                    # 裁剪并保存图像
                    gdal.Translate(
                        output_folder + f"/{type}/{PK_UID}_{x0}_{y0}.tif",
                        dataset,
                        srcWin=outputBounds,
                        format='GTiff',
                        # outputSRS='EPSG:3857'  # 指定输出坐标系
                    )

    dataset = None  # 关闭原始图像

def cropImage(geojson3857, imagepath, labelpath, grid_size = 256):

    # 打开GeoJSON文件
    geojson_src = gpd.read_file(geojson3857)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_folder + '/A', exist_ok=True)
    os.makedirs(output_folder + '/B', exist_ok=True)
    os.makedirs(output_folder + '/label', exist_ok=True)
    entries = os.listdir(labelpath)

    for img_path in tqdm(entries):
    # 获取目录中所有的项
    
    label_path = os.path.join(labelpath, img_path)
    quad = img_path[:-4]
    # 打开栅格影像文件
    # quad = '1625-1160_quad'
    dataset = gdal.Open(label_path)

    geotransform = dataset.GetGeoTransform()

    # 计算栅格影像的边界框
    min_x = geotransform[0]
    max_y = geotransform[3]
    max_x = min_x + geotransform[1] * dataset.RasterXSize
    min_y = max_y + geotransform[5] * dataset.RasterYSize

    # 使用Shapely创建栅格影像的边界框（矩形）
    raster_bbox = box(min_x, min_y, max_x, max_y)
    # 使 spatial_index 进行空间查询
    intersecting_ids = list(geojson_src.sindex.query(raster_bbox, predicate='intersects'))
    interFea = geojson_src.iloc[intersecting_ids].drop_duplicates()
    interFea['x'] = interFea['geometry'].apply(lambda geo: geo.centroid.x)
    interFea['y'] = interFea['geometry'].apply(lambda geo: geo.centroid.y)
    qqdate = interFea['QQ_month'].unique()
    hqdate = interFea['HQ_month'].unique()

    # 裁剪label
    points_of_interest = {}
    points_of_interest['type'] = 'label'
    points_of_interest['PK_UID'] = quad
    # interFea['PK_UID'].tolist()
    points_of_interest['x'] = interFea['x'].tolist()
    points_of_interest['y'] = interFea['y'].tolist()
    input_tif = label_path
    
    crop_image_byPOI(input_tif, output_folder, grid_size, points_of_interest)

    # 裁剪前期影像
    for date in qqdate: 
        datefea = interFea[interFea['QQ_month'] == date]
        points_of_interest = {}
        points_of_interest['type'] = 'A'
        points_of_interest['PK_UID'] = quad + '_' + date
        # datefea['PK_UID'].tolist()
        points_of_interest['x'] = datefea['x'].tolist()
        points_of_interest['y'] = datefea['y'].tolist()
        
        input_tif = f'{imagepath}/{date}/{quad}.tif'
        
        crop_image_byPOI(input_tif, output_folder, grid_size, points_of_interest)

    # 裁剪后期影像
    for date in hqdate: 
        datefea = interFea[interFea['HQ_month'] == date]
        points_of_interest = {}
        points_of_interest['type'] = 'B'
        points_of_interest['date'] = date
        points_of_interest['PK_UID'] = quad + '_' + date
        # datefea['PK_UID'].tolist()
        points_of_interest['x'] = datefea['x'].tolist()
        points_of_interest['y'] = datefea['y'].tolist()
        input_tif = f'{imagepath}/{date}/{quad}.tif'

        crop_image_byPOI(input_tif, output_folder, grid_size, points_of_interest)


if __name__ == '__main__':

    Basemappath = '/Users/zgf/Desktop/planetBasemap'  # 请替换为实际的路径
    partition = '106_21_107_26'  # 请替换为实际的分区名称
    imagepath = f'{Basemappath}/{partition}'
    labelpath= f'{Basemappath}/{partition}/labeltif'
    geojson3857 = f'{Basemappath}/{partition}/{partition}_3857.geojson'
    output_folder = f'{partition}'
    grid_size = 256
    cropImage(geojson3857, imagepath, labelpath, grid_size)
