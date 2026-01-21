##https://blog.csdn.net/qq_51697761/article/details/129873669



"""
将所生成的栅格中，像元值为0的，确认为无数据区域，即将改值删除
"""
#读取“08_01result”中的栅格
#异常值转为nodata，新栅格导入“09_01result”

# import os
# import numpy as np
# from osgeo import gdal

# 导入所需的库
import rasterio
import numpy as np

# 定义输入和输出的栅格文件路径
input1 = r"K:\E_LST&UTCI_Exposure\Data03_UTCI_04_HZA×HZI×HZQ_LiFangTi\HZA×HZI×HZQ_2021.tif"#热区立方体
input2 = r"K:\E_LST&UTCI_Exposure\Data03_UTCI_00_POP\UTCI_POP_2021.tif"#重采样后的人口
output = r"K:\E_LST&UTCI_Exposure\TEST\ExposureHuman_2021.tif"


# 读取两个栅格的数据和元数据
with rasterio.open(input1) as src1:
    data1 = src1.read(1) # 读取第一个波段的数据
    profile = src1.profile # 获取栅格的元数据
with rasterio.open(input2) as src2:
    data2 = src2.read(1) # 读取第一个波段的数据


# # 将两个栅格的数据转换为“int16”类型，并将0值替换为-9999
# data1 = data1.astype(np.int16)
# data1[data1 == 0] = -9999
# data2 = data2.astype(np.int16)
# data2[data2 == 0] = -9999
# data3 = data3.astype(np.int16)
# data3[data3 == 0] = -9999

# 计算两个栅格的对应像元的相除
result = data1 * data2 / 100

# # 将结果中的-9999值替换为0
# result[result == -9999] = 0
# # 将结果中的1值替换为0
# result[result == 1] = 0


# 将结果转换为“int16”类型
result = result.astype(np.int32)

# 修改输出栅格的元数据，将nodata值设为0，将数据类型设为“int16”
profile.update(nodata=0, dtype=np.int32)

# 将结果写入输出的栅格文件
with rasterio.open(output, "w", **profile) as dst:
    dst.write(result, 1) # 写入第一个波段的数据
