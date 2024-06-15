import requests
import gzip
import json
import subprocess
import os
import tqdm
from aoi2grid import getGridByAOI
import time
import random
import geopandas as gpd

def queryByextent(savepath, extent, layerid):
    # 请求的URL
    url = "https://www.stgz.org.cn/yjjc/geodbService/geodata/queryByExtent.do"
    # 创建一个Session对象
    session = requests.Session()
    # 请求头部，包含内容类型和来源等信息
    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        # 添加其他必要的headers，例如Cookie等
    }
    # 手动添加cookie到session中
    cookies = {
        "SESSION": "YjMzNWQwODgtMGIwOS00ZmQ3LWJhZGItY2U0YzdjNzJjMzg2",
        "HWWAFSESID": "bfd65d914d8793d036",
        "HWWAFSESTIME": "1717390870003",
    }

    # SESSION=MGVmMDRmMDItZTE5Yy00M2QzLTkyYTUtOWVhN2RhN2JjNmQ0; HWWAFSESID=bfd65d914d8793d036; HWWAFSESTIME=1717390870003
    # 将cookie添加到session中
    for key, value in cookies.items():
        session.cookies.set(key, value)
    # 请求负载，即发送给服务器的JSON数据

    # 变化图斑（国家下发）
    payload = {
        "type":"f3f1T3J4Q1dgCwZiWIQ83VDk0ay9sSmhuQ0Uy6kQU1CCB0N1lCUT09",
        "layerId":"9912ZzRyUjdQrHXzKoYTdxRmtJU0VoZEgxNU02QT09B",
        "tableName":"44a1Z3RJVmHpOFYNqppR09aODZlOFRmK1NqdzUxQT60gL09",
        "filter":"6f71bUxXdz3dNN2l1aFFYY0VoSlpieHFDQnIzS3Y0MzN4Uld4aTFUa3BoVWJzSuVk7T0="
    }
    
    # # 2023核实图斑 
    # payload = {
    #     # "type": "3381T3J4Q12d3VDk0ay9sSmhuQ0UHXx4U0N1lCUT09",
    #     "type": "7fe1T3J4Q1dT29e1RBVT3VDk0ay9sSmhuQ0U0N1lCUTUkEEQ4O09",
    #     "extent": "e062TlM3MHBsRBMUIoIXFgvZVN2WW1jVnlpa3hSmJQT09",
    #     "layerId": "fa21UFR1VqvOOxpc1psUjIyRHdoNWdodURtk+cSGpVUT09",
    #     "tableName":  "8211WU0vmjBanhrdE9xd3p4Y1Q4MTlkSTg1T0Nybko4K0dSVXZZZDFLOUlqQyeHVSND0="
    # }

    # # 判读图斑2023
    # payload = {
    # # "filter": "d602bUxXdzdNwHbN2l1aFFYY0VoSlpieHFDSWpYcllOSlFyRDErNHNFOVVxeHMvTT0=F",
    # "layerId": "8161eHVyL4BRRiS2RJZ3dmeWdKRDNVQUFjYXhpnbonL1QT09",
    # "tableName": "3bf1S0dzeUJhCbWFQOUhIVWpJQm5nNWlOdz0xdpmP9",
    # "type": "4462T3J4Q1d3VOfKtkzwDk0ay9sSmhuQ0U+FPpwk0N1lCUT09",
    # "extent": "e062TlM3MHBsRBMUIoIXFgvZVN2WW1jVnlpa3hSmJQT09"
    # }

    # # 2023底图
    # payload = {"type":"6911T3J4xUVslQ1d3VDk0ay9sSmhuQ0U0N1lCUT09Ae",
    # "extent": "5f81L3FTRjfF7JLcU0yZU1CNVZ5NWQvUHBNRlJOUCs2TjA1ekhJeVM4aVo1GtBzrwlqVYzYvYz0=",
    # "layerId":"7701Y2NvMPSWxyREwzQzVFTDRyRVNqRitKQT0yvctg9",
    # "tableName":"b932NjZrekhEeGGpCZG5QYzh4V2YwWDF4VXdEdjRNTks5U3h6dVJ0elpCZG5LTT0N5tgR=",
    # "filter":"b131UVBs4ySJLduGbWtlYVpoeE9kc1d0V3Jna1Q2c3A5KzFYS29NR2grZ3gxcUc0bGR1R093b2hmQklmdVFBVUVBbUFWM1JOVzRhMmo0ZXZlMmJrYnNUL1JLSHh0eWJ1M0tqSTZxdDc5MHRqalhjZENENkdoUUdvOFRReGRTTDl5M01yVUwvVjNDZ0VLcnVCdmZoRGQ0L3lmYVpPMEtPVGttd1d4REJwSUd6ZGxGWThwa3Uram04QzVFN3BmR00xV1Rib3BNaXZQVmNvSkJTakhqdG5WUnJlUVhBajIydnE3aTRhdjFsYUhTcDE2ci9nKzhoTHM2TitTaW54aENYMTl1USt4QmQ2WHNHb3VZSnFFc1ZxS3ZaV0hsVVpPQm9ueTBZNUhQVmhpejliMTl6WThZa0RLZTBINzZqWGlENTZVb1ZBMHc0RE9ycHFIazUzRzZWazFEbklzVWVmTZFhBPT0="}

    # 国家下发
    # payload = {
    #     # "type": "3381T3J4Q12d3VDk0ay9sSmhuQ0UHXx4U0N1lCUT09",
    #     "type": "8cd1T3J4Q1dqnH4iI3VDk0ay9sSmhuQ0U0N1lCUT3+fv09",
    #     "filter": "1241bUxXdazdNN2l1aFFYY0VoSlpieHFDQnIzS3Y0MzN4Uld4aTFUa3BoVWJlCDzST0=",
    #     "extent": "f481R0prNUFMRwWnBJT1pZclJEV2EwYTZNYkhMQ2I4MHRzRmtGUVYzWWRKS0JmRHNUNkJjNFl1b0hvQlpYbyt1Tk1xR2tZaVpEQ01xMEZZQVU4VmNtZjRscEE9PQk7N==",
    #     "layerId": "f951ZzRyUi2mfNjdQYTdxRmtJU0VoZEgxNU02QOMWaXT09",
    #     "tableName":  "7212Z3RJVmppEIUVR09aODZlOFRmK1NqSg/SofRdzUxQT09"
    # }


    # 定义要传递给Node.js脚本的参数
    node_script = '/Users/zgf/Downloads/同步空间/毕业设计/林草系统图斑爬虫/坐标加密.js'
    # 运行Node.js脚本并捕获输出
    JMextent = subprocess.run(["node", node_script, extent], capture_output=True, text=True)
    if JMextent.returncode == 0:
        payload['extent'] = JMextent.stdout.strip()
    else:
        print(f"脚本错误: {JMextent.stderr}")
    payload['layerId'] = "8161eHVyL4BRRiS2RJZ3dmeWdKRDNVQUFjYXhpnbonL1QT09"

    # 发起POST请求
    response = session.post(url, headers=headers, data=json.dumps(payload))

    res_data = response.json()
    # 指定要保存的文件名
    os.makedirs(savepath, exist_ok = True)
    filename = os.path.join(savepath, extent+".json")
    # 打开文件，准备写入
    with open(filename, 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将字典写入文件
        json.dump(res_data, f, ensure_ascii=False, separators=(',', ':'))

def queryBygrids(savepath, gridlist, layerid):
    for extent in tqdm.tqdm(gridlist):
        strextent = ','.join(map(str, extent))
        queryByextent(savepath, strextent, layerid)
        # 生成一个随机时间间隔
        random_sleep_time = random.uniform(10, 20)
        time.sleep(random_sleep_time)

if __name__ == "__main__":
    sheng = gpd.read_file('/Users/zgf/Downloads/同步空间/毕业设计/林草系统图斑爬虫/依赖文件/省边界/2023年省级.shp')
    scale = 0.5
    shengming = '广西壮族自治区'
    AOI = sheng[sheng['省']==shengming]['geometry'].values[0]
    gridlist = getGridByAOI(AOI, scale)
    # gridlist = [[107.4, 23.7, 107.5, 23.8]]
    # gridlist = [[115,29,115.5,29.5],[115,29.5,115.5,30],[115.5,29,116,29.5],[115.5,29.5,116,30]]
    # [[110, 32, 111, 33], [111, 29, 112, 30], [111, 30, 112, 31], [111, 31, 112, 32], [111, 32, 112, 33], [112, 29, 113, 30], [112, 30, 113, 31], [112, 31, 113, 32], [112, 32, 113, 33], [113, 29, 114, 30], [113, 30, 114, 31], [113, 31, 114, 32], [113, 32, 114, 33], [114, 29, 115, 30], [114, 30, 115, 31], [114, 31, 115, 32], [115, 29, 116, 30], [115, 30, 116, 31], [115, 31, 116, 32]]

    print(gridlist)
    savepath = "/Users/zgf/Downloads/同步空间/毕业设计/database/guangxi/变化图斑/json"
    layerid = "9912ZzRyUjdQrHXzKoYTdxRmtJU0VoZEgxNU02QT09B"
    # 判读图斑2023 "8161eHVyL4BRRiS2RJZ3dmeWdKRDNVQUFjYXhpnbonL1QT09"
    # 变化图斑 9912ZzRyUjdQrHXzKoYTdxRmtJU0VoZEgxNU02QT09B
    # 
    queryBygrids(savepath, gridlist, layerid)