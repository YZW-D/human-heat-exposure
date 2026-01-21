# coding=gb2312
# #https://blog.csdn.net/x2434417239/article/details/111354200
"""
使用Python编程，实现以下需求：一个excel文件“F:\E_UTCI_Exposure\07表格数据\33_国家尺度_总和_HE-LFT_Test.xlsx”，
其中第一列“Name”为列名，其他列为2001年到2021年每一年的数据值。
需要对这个excel中的每一行开展MK趋势分析（包括趋势类型、Theil-Sen斜率估算值、显著性检验等），
并将结果输出为“Result.csv”,保存在文件夹“F:\E_UTCI_Exposure\07表格数据\02MK趋势分析结果”。
df = pd.read_excel(file_path, engine='openpyxl')
"""



# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from scipy.stats import kendalltau

# 读取Excel文件
file_path = r"F:\E_UTCI_Exposure\07表格数据\12_国家尺度_总和_LFT.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')

# 计算Theil-Sen斜率估算值和MK趋势显著性
def theil_sen_slope(x):
    n = len(x)
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            slopes.append((x[j] - x[i]) / (j - i))
    return np.median(slopes)

def mk_test(x):
    tau, p_value = kendalltau(range(len(x)), x)
    return tau, p_value

# 对每一行进行MK趋势分析
result = pd.DataFrame(columns=["CNTRY_NAME", "Theil-Sen Slope", "MK Trend Significance"])
for index, row in df.iterrows():
    name = row["CNTRY_NAME"]
    data = row[1:]  # 去除第一列的Name
    slope = theil_sen_slope(data)
    trend_significance, p_value = mk_test(data)
    result = result.append({"CNTRY_NAME": name, "Theil-Sen Slope": slope, "MK Trend Significance": trend_significance, "P-Value": p_value}, ignore_index=True)

# 保存结果到CSV文件
result_file_path = r"F:\E_UTCI_Exposure\07表格数据\03MK趋势分析结果\11_国家尺度_总和_LFT_MK.csv"
result.to_csv(result_file_path, index=False)

print(f"结果已保存到 {result_file_path}")
