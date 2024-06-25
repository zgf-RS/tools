import geopandas as gpd

def transform(geojson4326, geojson3857, targetepsg):
    gdf = gpd.read_file(geojson4326)
    gdf = gdf.to_crs(epsg=targetepsg)
    gdf.to_file(geojson3857)

if __name__ == '__main__':
    
    Basemappath = '/Users/zgf/Desktop/planetBasemap'  # 请替换为实际的路径
    partition = '106_21_107_26'  # 请替换为实际的分区名称
    geojson4326 = f'{Basemappath}/{partition}/{partition}.geojson'
    geojson3857 = f'{Basemappath}/{partition}/{partition}_3857.geojson'
    targetepsg = 3857

