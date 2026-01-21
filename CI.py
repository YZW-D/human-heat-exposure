# coding=gb2312
# #https://blog.csdn.net/x2434417239/article/details/111354200

# -*- coding: utf-8 -*-


"""
示例脚本：从 Excel 读取 '人均GDP（美元）'、'HHE_变化率' 字段，
计算集中指数(CI)并绘制平滑的集中曲线。
在图中标注 CI 值，并导出 PDF。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


def concentration_index(health_values, ses_values):
    """
    根据给定的健康指标数组和 SES 数组，计算集中指数(CI)。
    常用公式: CI = (2 / (μ * n)) * sum(h_i * R_i) - 1
    其中 R_i = (i - 0.5) / n, i 为按 SES 排序后的序号(1~n).

    参数:
    --------
    health_values : array-like
        需要测度不平等的健康指标（如 HHE_变化率）
    ses_values : array-like
        社会经济地位指标（如 人均GDP、收入水平等），用于排序

    返回:
    --------
    float
        计算得到的集中指数 CI, 取值范围通常在 [-1, 1]
    """
    # 转为 numpy array
    h = np.asarray(health_values, dtype=float)
    ses = np.asarray(ses_values, dtype=float)

    n = len(h)
    if n == 0:
        return np.nan

    # 1) 按 SES 从低到高排序
    order = np.argsort(ses)
    h_sorted = h[order]

    # 2) 计算健康指标平均值 μ
    mu = h_sorted.mean()

    # 3) 定义秩 R_i
    i = np.arange(1, n + 1)
    R_i = (i - 0.5) / n

    # 4) sum(h_i * R_i)
    sum_h_R = np.sum(h_sorted * R_i)

    # 5) CI
    CI = (2.0 / (mu * n)) * sum_h_R - 1.0
    return CI


def plot_concentration_curve(health_values, ses_values, ci_value=None, output_pdf=None):
    """
    绘制集中曲线，并对离散点进行平滑处理。在图中可标注 CI 值。

    参数:
    --------
    health_values : array-like
        需要绘制分布的健康指标（如 HHE_变化率）
    ses_values : array-like
        用于排序的 SES 指标（如 人均GDP）
    ci_value : float, optional
        若提供，则在图中显示此 CI 值
    output_pdf : str, optional
        若提供文件路径，则将图表保存为 PDF 文件
    """
    h = np.asarray(health_values, dtype=float)
    ses = np.asarray(ses_values, dtype=float)

    n = len(h)
    if n == 0:
        print("没有可用数据，无法绘图。")
        return

    # 按 SES 从低到高排序
    order = np.argsort(ses)
    h_sorted = h[order]

    # 计算健康指标累计和及总和
    cum_h = np.cumsum(h_sorted)
    total_h = cum_h[-1]

    # 原始离散点 X: 人群累计占比, Y: 健康指标累计占比
    X_raw = np.arange(1, n + 1) / n  # [1/n, 2/n, ..., 1]
    Y_raw = cum_h / total_h  # 对应的累计占比

    # 在开头插入 (0, 0)，以保证曲线从 (0,0) 开始
    # 如果 X_raw[-1] 就是 1 且 Y_raw[-1] ~ 1，则不再重复拼接 (1,1)
    X_points = np.concatenate(([0], X_raw))
    Y_points = np.concatenate(([0], Y_raw))

    # 使用 Cubic Spline 进行平滑插值
    # 要求 X_points 严格升序且无重复
    # 若你担心某些情况下 X_points 内有重复, 可用 np.unique 去重
    spline = make_interp_spline(X_points, Y_points, k=3)

    # 生成高分辨率 X 坐标并插值
    X_smooth = np.linspace(0, 1, 200)
    Y_smooth = spline(X_smooth)

    # 绘制图表
    plt.figure(figsize=(6, 6))
    # 1) 平滑后的集中曲线
    plt.plot(X_smooth, Y_smooth, color='blue', label="Concentration Curve (Smoothed)")
    # 2) 对角线 (完全平等线)
    plt.plot([0, 1], [0, 1], 'k--', label="Line of Equality")

    plt.xlabel("Cumulative share of population (by SES)")
    plt.ylabel("Cumulative share of health indicator")
    plt.title("Concentration Curve (Smoothed)")

    # 在图中标注 CI
    if ci_value is not None:
        plt.text(
            0.05, 0.9,  # 在 Axes 坐标 (x=5%, y=90%) 处
            f"CI = {ci_value:.4f}",  # 显示 CI 数值，保留4位小数
            fontsize=12,
            transform=plt.gca().transAxes,
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3)
        )

    plt.legend()
    plt.grid(True)

    # 若指定了 PDF 输出，则保存
    if output_pdf:
        plt.savefig(output_pdf, format='pdf', bbox_inches='tight')
        print(f"集中曲线已保存为: {output_pdf}")

    # 显示绘图窗口
    plt.show()


if __name__ == "__main__":
    # ========== 1) 读取 Excel 数据 ==========
    excel_path = r"G:\06Python_Study\Project\TEST\11LST_UTCI_Exposure\DATA_NEW\20_02STEP_表格梳理\02GZX的不平等绘制.xlsx"
    # 注意指定 engine="openpyxl" 以支持 xlsx 文件
    df = pd.read_excel(excel_path, engine="openpyxl")

    # 根据你的实际字段名替换
    gdp_col = "人均GDP（美元）"
    hhe_col = "GZX_变化率"

    ses_values = df[gdp_col].values  # SES 指标
    health_values = df[hhe_col].values  # 健康指标

    # ========== 2) 计算集中指数 CI ==========
    ci = concentration_index(health_values, ses_values)
    print(f"集中指数 (CI): {ci:.4f}")

    # ========== 3) 绘制平滑的集中曲线并标注 CI ==========
    output_pdf_path = "集中曲线_平滑示例.pdf"
    plot_concentration_curve(
        health_values,
        ses_values,
        ci_value=ci,
        output_pdf=output_pdf_path
    )
