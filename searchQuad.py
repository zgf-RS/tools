import os
import re
import rasterio
from rasterio import shutil

def list_files(folder_path):
    """
    读取给定文件夹下所有的文件名，并返回文件名列表。
    """
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return []
    
    # 使用os.listdir()获取文件夹中的所有文件和子文件夹名称
    file_names = os.listdir(folder_path)
    
    # 如果只想要文件，不包括子文件夹，可以过滤掉子文件夹
    # file_names = [name for name in file_names if os.path.isfile(os.path.join(folder_path, name))]
    
    return file_names

def traverse_folders(path):
    """
    遍历给定路径下符合 year-month 格式的子文件夹
    """
    # 编译一个正则表达式，用于匹配 year-month 格式
    pattern = re.compile(r'^\d{4}-\d{2}$')
    pathlist = []
    # 遍历路径下的所有文件和文件夹
    for root, dirs, files in os.walk(path):
        # 遍历文件夹
        for dir in dirs:
            # 检查文件夹名称是否符合 year-month 格式
            if pattern.match(dir):
                # 获取完整的文件夹路径
                if root == path:
                    image_dir_path = os.path.join(root, dir)
                    # 输出匹配的文件夹路径（或进行其他操作）
                    pathlist.append(image_dir_path)
    pathlist.sort()
    return pathlist

# 需要处理的quad
def searchQuad(imagepath, Quadpath):
    quaddict = {}

    # 检查目录是否存在
    if not os.path.exists(Quadpath):
        os.mkdir(Quadpath)
    
    imagedatedir = traverse_folders(imagepath)

    for imagepath in imagedatedir:
        date = imagepath.split('/')[-1]
        files = list_files(imagepath)
        for file in files:
            if not file.endswith('.tif'):
                continue
            if file[:-4] not in quaddict:
                quaddict[file[:-4]] = date
                # 创建空img空间对齐tif
                # 打开原始tif文件
                print(f'{imagepath}/{file}')
                with rasterio.open(f'{imagepath}/{file}') as src:
                    
                    # 使用rasterio的copy函数复制文件
                    # 这将复制所有的波段数据、元数据和配置
                    shutil.copy(src, f'{Quadpath}/{file}', driver='GTiff')

            else:
                quaddict[file[:-4]] = quaddict[file[:-4]] + '|' + date

if __name__ == '__main__':
    Basemappath = '/Users/zgf/Desktop/planetBasemap'  # 请替换为实际的路径
    partition = '106_21_107_26'  # 请替换为实际的分区名称
    imagepath = f'{Basemappath}/{partition}'
    Quadpath = f'{Basemappath}/{partition}/bound'
    searchQuad(imagepath, Quadpath)