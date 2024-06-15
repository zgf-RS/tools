import json
import os
import geopandas as gpd
import pandas as pd
import tqdm

def json2geojson(folder_path ,output_path):
    # 
    geodataframes = []
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    # 打印文件列表
    for file in files:
        # 加载JSON数据
        if not file.endswith('json'):
            continue
        with open(file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            geojson = convert_to_geojson(original_data)
            geodataframes.append(geojson)
    # 使用concat合并GeoDataFrames
    merged_gdf = geodataframes[0]
    if len(geodataframes) > 1:
        for geodataframe in tqdm.tqdm(geodataframes[1:]):
            merged_gdf["features"] += geodataframe["features"]

    with open(output_path+'/hblin.geojson', 'w', encoding='utf-8') as file:
        json.dump(merged_gdf, file, separators=(',', ':'), ensure_ascii=False)
    print("GeoJSON数据已成功写入到output.geojson文件中。")
# 将原始数据转换为GeoJSON格式的函数
def convert_to_geojson(original_data):
    # 创建GeoJSON FeatureCollection对象
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # 遍历原始数据中的每个数据项
    for data_item in original_data['datas']:
        if data_item['SHENG_DESC'] != '广西壮族自治区' or data_item['RW_LX_DESC'] != '1-林地':
            continue
        # 解析几何数据，假设几何数据是有效的JSON格式
        geodict = json.loads(data_item['SHAPE'])

        # # 核实图斑
        # keys_to_select = ["PK_UID", "FHZT", "SJ_BQ", "RW_LX","RW_LX_DESC","LAI_YUAN_DESC","BGYJ_DESC","QQYX_SJ","HQYX_SJ","PD_BHYY_DESC","YZ_BHYY_DESC","BH_MIAN_JI",
        # "PAN_NO_TB", "BHTB_NO","PD_BHYY","YZ_BHYY","LIN_BAN","XIAO_BAN","SEN_LIN_LB_DESC","DI_LEI_DESC","QI_YUAN_DESC","ZBFGLX_DESC","QYKZ_DESC","SEN_LIN_LB_DESC"]
        
        # 变化图斑
        keys_to_select = ["PK_UID", "FHZT", "SJ_BQ", "RW_LX", "NIAN_DU", "SHENG_DESC", "PAN_NO_TB", "PAN_BHLX_DESC", "PAN_BHLX", "PDXH", "Q_DI_LEI", "Q_DI_LEI_DESC", "QQYX_SJ", "HQYX_SJ", "LIN_BAN", "XIAOBAN", "MIAN_JI"]
        select_dict = {key: data_item[key] for key in keys_to_select}

        geodictfil = {}
        geodictfil['coordinates'] = geodict['coordinates'][0]
        geodictfil['type'] = 'Polygon'

        # 创建GeoJSON Feature对象
        feature = {
            "type": "Feature",
            "geometry": geodictfil,
            "properties": select_dict  # 将原始数据项作为属性
        }
        
        # 将Feature添加到FeatureCollection中
        geojson["features"].append(feature)
    
    return geojson

# # 执行转换函数
# geojson_data = convert_to_geojson(original_data)

# # 将GeoJSON数据写入文件
# with open('/Users/zgf/Downloads/同步空间/毕业设计/database/guangxi/geojson/Gcheck2023.geojson', 'w', encoding='utf-8') as file:
#     json.dump(geojson_data, file, indent=2, ensure_ascii=False)
# print("GeoJSON数据已成功写入到output.geojson文件中。")

if __name__ == '__main__':
    # convert_to_geojson(original_data)
    # 指定文件夹路径
    folder_path = '/Users/zgf/Downloads/同步空间/毕业设计/database/guangxi/变化图斑/json'
    output_path = '/Users/zgf/Downloads/同步空间/毕业设计/database/guangxi/变化图斑/geojson'
    json2geojson(folder_path, output_path)
