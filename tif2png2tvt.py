from PIL import Image
import os
from tqdm import tqdm
import os
import random
import shutil

def tif2png2tvt(basePath, pngPath, tvtPath, ratio):
    imgids = os.listdir(basePath + 'A/')
    os.makedirs(pngPath + 'A/', exist_ok=True)
    # 打开.tif图像文件
    for imgid in tqdm(imgids):
        if imgid[-4:] == '.tif':
            with Image.open(basePath + 'A/' + imgid) as img:
                # 转换图像为PNG格式并保存
                r, g, b, a = img.split()
                # 合并这三个波段为新的RGB图像
                img_rgb = Image.merge("RGB", (r, g, b))
                
                # 转换图像为PNG格式并保存
                img_rgb.save(pngPath + 'A/' + imgid[:-4] + '.png')
                # img.save(pngPath + 'A/'+ imgid[:-4]+'.png')

    imgids = os.listdir(basePath + 'B/')
    os.makedirs(pngPath + 'B/', exist_ok=True)
    # 打开.tif图像文件
    for imgid in tqdm(imgids):
        if imgid[-4:] == '.tif':
            with Image.open(basePath + 'B/' + imgid) as img:
                # 转换图像为PNG格式并保存
                r, g, b, a = img.split()
                # 合并这三个波段为新的RGB图像
                img_rgb = Image.merge("RGB", (r, g, b))
                
                # 转换图像为PNG格式并保存
                img_rgb.save(pngPath + 'B/' + imgid[:-4] + '.png')

    os.makedirs(pngPath + 'label/', exist_ok=True)
    imgids = os.listdir(basePath + 'label/')
    # 打开.tif图像文件
    for imgid in tqdm(imgids):
        if imgid[-4:] == '.tif':
            with Image.open(basePath + 'label/' + imgid) as img:
                # 转换图像为PNG格式并保存
                img.save(pngPath + 'label/'+ imgid[:-4]+'.png')


    # 数据集切分

    # 获取所有数据的集合
    imgids = os.listdir(pngPath + 'B/')

    # 打乱列表顺序
    random.shuffle(imgids)

    # 定义切分比例
    train_ratio = ratio[0]
    val_ratio = ratio[1]
    test_ratio = ratio[2]

    # 确保比例加起来为1
    assert train_ratio + val_ratio + test_ratio == 1

    # 计算每份数据的数量
    total_count = len(imgids)
    train_count = int(total_count * train_ratio)
    val_count = int(total_count * val_ratio)

    # 计算切分索引
    train_end = train_count
    val_end = train_end + val_count

    # 切分列表
    train_set = imgids[:train_end]
    val_set = imgids[train_end:val_end]
    test_set = imgids[val_end:]

    # 打印结果
    print(f"train set: {len(train_set)} items")
    print(f"Validation set: {len(val_set)} items")
    print(f"Test set: {len(test_set)} items")
    setnum = {}
    setnum['train'] = train_set
    setnum['val'] = val_set
    setnum['test'] = test_set

    # 根据切分情况，划分三个集合
    for huafen in ['train', 'val', 'test']:
        savetvtPath = tvtPath + huafen + '/'
        os.makedirs(savetvtPath  + 'A/',exist_ok=True)
        os.makedirs(savetvtPath  + 'B/',exist_ok=True)
        os.makedirs(savetvtPath  + 'label/',exist_ok=True)
        for imgid in setnum[huafen]:
            a = pngPath +'A/' + imgid
            b = pngPath + 'B/' + imgid
            l = pngPath + 'label/' + imgid
            aa = savetvtPath + 'A/' + imgid
            bb = savetvtPath+ 'B/' + imgid
            ll = savetvtPath + 'label/' + imgid
            shutil.copy(a, aa)
            shutil.copy(b, bb)
            shutil.copy(l, ll)

if __name__ == '__main__':
    basePath = '/Users/zgf/Desktop/训练数据集/C105_24_106_25/'
    pngPath = basePath[:-1] + '_png/'
    tvtPath = basePath[:-1] + '_tvt/'
    # train val test
    ratio = [0.8, 0.1, 0.1]
    tif2png2tvt(basePath, pngPath, tvtPath, ratio)