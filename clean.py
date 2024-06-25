import os
import shutil

# 排除存在不同日期的256切片
def rmcount2(nflist):
    # 使用字典来统计每个元素出现的次数
    counts = {}
    for item in nflist:
        counts[item] = counts.get(item, 0) + 1

    # 根据出现次数过滤元素，只保留出现次数小于2次的元素
    new_nflist = [item for item in nflist if counts[item] < 2]
    return new_nflist

def clean(Basemappath,  partition):
    # 设置文件夹路径
    folderQ = Basemappath + '/' + partition + '/A'
    folderH = Basemappath + '/' + partition + '/B'
    folderL = Basemappath + '/' + partition + '/label'

    # 获取文件夹中的文件列表
    filesQ = os.listdir(folderQ)
    filesH = os.listdir(folderH)
    filesL = os.listdir(folderL)

    # 字典记录日期
    DATEQ = {}
    DATEH = {}

    ## 怎么判断 只要该切片对应下载的前期影像和后期影像分别存在不止一个，该位置需要被舍弃
    nflist = []
    for file in filesQ:
        # 去除日期
        nf = file[:14] + file[22:]
        DATEQ[nf] = file[14:22]
        nflist.append(nf)
    qrm = rmcount2(nflist)

    nflist = []
    for file in filesH:
        # 去除日期
        nf = file[:14] + file[22:]
        DATEH[nf] = file[14:22]
        nflist.append(nf)
    hrm = rmcount2(nflist)

    # 使用集合的交集操作
    intersection = set(qrm).intersection(hrm).intersection(filesL)

    # 转换回列表（如果需要）
    intersection_list = list(intersection)

    print(len(intersection_list), '交集个数')
    print(len(qrm), '前期影像个数')
    print(len(hrm), '后期影像个数')

    # 新文件夹路径
    CfolderQ = 'C' + folderQ

    # 如果新文件夹不存在，则创建它
    if not os.path.exists(CfolderQ):
        os.makedirs(CfolderQ)

    # 记录了需要的文件名的列表
    intersection_lis = intersection_list

    # 遍历列表中的每个文件名
    for filename in intersection_lis:
        # 构造原始文件的完整路径
        srcname = filename[:14]+ DATEQ[filename] + filename[14:]
        src_file = os.path.join(folderQ, srcname)
        # 构造新文件夹中的目标文件路径
        dest_file = os.path.join(CfolderQ, filename)
        
        # 检查原始文件是否存在
        if os.path.exists(src_file):
            # 复制文件到新文件夹
            shutil.copy(src_file, dest_file)
            print(f"Copied: {srcname}")
        else:
            print(f"File not found: {src_file}")

    # 新文件夹路径
    CfolderH = 'C' + folderH

    # 如果新文件夹不存在，则创建它
    if not os.path.exists(CfolderH):
        os.makedirs(CfolderH)

    # 记录了需要的文件名的列表
    intersection_lis = intersection_list

    # 遍历列表中的每个文件名
    for filename in intersection_lis:
        # 构造原始文件的完整路径
        srcname = filename[:14]+ DATEH[filename] + filename[14:]
        src_file = os.path.join(folderH, srcname)
        # 构造新文件夹中的目标文件路径
        dest_file = os.path.join(CfolderH, filename)
        
        # 检查原始文件是否存在
        if os.path.exists(src_file):
            # 复制文件到新文件夹
            shutil.copy(src_file, dest_file)
            print(f"Copied: {srcname}")
        else:
            print(f"File not found: {src_file}")

    # 新文件夹路径
    CfolderL = 'C' + folderL

    # 如果新文件夹不存在，则创建它
    if not os.path.exists(CfolderL):
        os.makedirs(CfolderL)

    # 记录了需要的文件名的列表
    intersection_lis = intersection_list

    # 遍历列表中的每个文件名
    for filename in intersection_lis:
        # 构造原始文件的完整路径
        srcname = filename
        src_file = os.path.join(filesL, srcname)
        # 构造新文件夹中的目标文件路径
        dest_file = os.path.join(CfolderL, filename)
        
        # 检查原始文件是否存在
        if os.path.exists(src_file):
            # 复制文件到新文件夹
            shutil.copy(src_file, dest_file)
            print(f"Copied: {srcname}")
        else:
            print(f"File not found: {src_file}")

if __name__ == '__main__':

    Basemappath = '/Users/zgf/Desktop/planetBasemap'  # 请替换为实际的路径
    partition = '106_21_107_26'  # 请替换为实际的分区名称
    # clean文件名partition前面加C
    clean(Basemappath,  partition)