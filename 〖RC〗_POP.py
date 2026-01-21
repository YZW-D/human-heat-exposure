#https://blog.csdn.net/x2434417239/article/details/111354200
"""
本代码实现ArcGIS中的区域统计功能（Zonal），将统计的属性值直接赋予矢量文件属性表，可实现批量统计
"""



# -*- coding: utf-8 -*-

import ogr, os
from rasterstats import zonal_stats


def zonal(input_vector, in_raster, Stats_type, raster_name):
    shp = ogr.Open(input_vector, 1)
    lyr = shp.GetLayer()
    # 添加字段
    zonal_Field = ogr.FieldDefn("{}".format(raster_name), ogr.OFTReal)
    # 添加字段名称为栅格文件名称，可根据自己需求修改
    zonal_Field.SetPrecision(10)
    lyr.CreateField(zonal_Field)

    zonal_method = zonal_stats(input_vector, in_raster, stats=[Stats_type])
    FID = 0
    for feat in lyr:
        Index = zonal_method[FID][Stats_type]
        feat.SetField("{}".format(raster_name), Index)
        feat.SetFID(FID)
        lyr.SetFeature(feat)
        FID += 1


if __name__ == "__main__":

    input_shp = r"G:\06Python_Study\Project\TEST\11LST_UTCI_Exposure\DATA_RESULT\11_01DATA\global_all_country_HE-LFT_LFT.shp"
    #in_folder = r"G:\06Python_Study\Project\TEST\09UTCI_World_DATA\10_03Data"##栅格所在的文件夹
    in_folder = r"K:\E_LST&UTCI_Exposure\Data03_UTCI_08_HE-LFT_01LFT"  ##栅格所在的文件夹
    Stats_type = 'sum'
    # Stats_type表示统计的类型，包括：'min', 'max', 'mean', 'count', 'sum', 'std', 'median', 'majority', 'minority', 'unique', 'range
    files = os.listdir(in_folder)
    for file in files:
        if file[-4:] == '.tif':
            input_raster = os.path.join(in_folder, file)
            raster_name = file[:-4]
            zonal(input_shp, input_raster, Stats_type, raster_name)
