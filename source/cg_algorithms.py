#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive': 
        if x0 == x1: # 垂直线段
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1: # 确保从左到右绘制线段
                x0, y0, x1, y1 = x1, y1, x0, y0 # 交换
            k = (y1 - y0) / (x1 - x0) # 计算斜率
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA': # TODO
        # 垂直（x 坐标相同）
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(int(y0), int(y1) + 1):
                result.append((x0, y))
            return result
        # 计算斜率
        dx, dy = x1 - x0, y1 - y0
        k = abs(dy / dx)
        # x 为主变量
        if k < 1:
            if x0 > x1: # 确保 x 坐标从小到大递增
                x0, y0, x1, y1 = x1, y1, x0, y0
            delta_y = dy / dx # 通过增量逐步增加 y 值
            y = y0
            for x in range(int(x0), int(x1) + 1):
                result.append((x, round(y)))
                y += delta_y
        # y 为主变量（k >= 1）
        else:
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            delta_x = dx / dy # 斜率取倒数
            x = x0
            for y in range(int(y0), int(y1) + 1):
                result.append((round(x), y))
                x += delta_x
    elif algorithm == 'Bresenham': # TODO
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(int(y0), int(y1) + 1):
                result.append((x0, y))
            return result
        # 计算 dx 和 dy
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx  # 判断是否为陡直线

        if steep:
            # 如果是陡直线，交换 x 和 y
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            dx, dy = dy, dx

        if x0 > x1:
            # 保证 x 从小到大遍历
            x0, y0, x1, y1 = x1, y1, x0, y0

        # 初始化决策参数
        p_k = 2 * dy - dx
        y_step = 1 if y0 < y1 else -1  # 确定 y 的增长方向
        y = y0

        # Bresenham 主循环
        for x in range(int(x0), int(x1) + 1):
            if steep:
                result.append((y, x))  # 如果是陡直线，交换回来
            else:
                result.append((x, y))
            if p_k >= 0:
                y += y_step
                p_k -= 2 * dx
            p_k += 2 * dy
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    # TODO
    result = []
    # 包含椭圆的矩形包围框的
    x0, y0 = p_list[0] # 左上角坐标
    x1, y1 = p_list[1] # 右下角坐标
    center_x, center_y = (x0 + x1) // 2, (y0 + y1) // 2 # 中心点
    rx, ry = abs(x1 - x0) // 2, abs(y1 - y0) // 2 # 水平半径，垂直直径 
    # 方便后续计算
    rx_2, ry_2 = rx ** 2, ry ** 2 

    # 椭圆点生成函数：在椭圆的四个象限对称点处初始添加4个点，以便从中心四个方向开始绘制椭圆
    def add_symmetric_points(cx, cy, x, y):
        """根据对称性添加椭圆的四个象限点"""
        result.append([cx + x, cy + y])
        result.append([cx - x, cy + y])
        result.append([cx + x, cy - y])
        result.append([cx - x, cy - y])

    # 第一象限的点生成：x 主导
    x_k, y_k = 0, ry # 设置初始点（椭圆的顶部点）
    p_k = ry_2 - rx_2 * ry + rx_2 / 4 # 决策参数
    add_symmetric_points(center_x, center_y, x_k, y_k)
    while ry_2 * x_k < rx_2 * y_k:
        if p_k < 0: # 仅沿x方向移动
            p_k += 2 * ry_2 * x_k + 3 * ry_2
        else:       # 同时沿x和y方向移动
            p_k += 2 * ry_2 * x_k + 3 * ry_2 - 2 * rx_2 * y_k + 2 * rx_2
            y_k -= 1
        x_k += 1
        # 对称性生成四个点
        add_symmetric_points(center_x, center_y, x_k, y_k)

    # 第二象限的点生成：y 主导
    p_k = ry_2 * (x_k + 0.5) ** 2 + rx_2 * (y_k - 1) ** 2 - rx_2 * ry_2
    while y_k > 0:
        if p_k > 0:
            p_k += -2 * rx_2 * y_k + 3 * rx_2
        else:
            p_k += 2 * ry_2 * x_k + 3 * rx_2 - 2 * rx_2 * y_k + 2 * ry_2
            x_k += 1
        y_k -= 1
        add_symmetric_points(center_x, center_y, x_k, y_k)

    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    # TODO
    # 计算i控制点的基函数值，表示该点对当前u值下曲线点的权重
    def de_boor_cox(i, k, u): 
        # 二维数组（k x k）：存储每个基函数值
        N = [[0] * k for _ in range(k)]

        # 第 1 阶的基函数值
        for j in range(k):
            N[j][0] = 1 if i + j <= u < i + j + 1 else 0
            # 1有影响，0没有影响

        # 从 2 阶开始，迭代计算更高阶的基函数值
        for d in range(1, k):
            for j in range(k - d):
                # 计算左边项
                left = 0
                if (u - (i + j)) != 0:
                    left = (u - (i + j)) / d * N[j][d - 1]
                # 计算右边项
                right = 0
                if ((i + j + d + 1) - u) != 0:
                    right = ((i + j + d + 1) - u) / d * N[j + 1][d - 1]
                # 更新当前阶次的基函数值
                N[j][d] = left + right

        # 最高阶次（k-1）的第一个基函数值
        return N[0][k - 1]
    
    du = 0.001 # 控制曲线的分辨率
    # 值越小，生成点越多，曲线越平滑
    result = []
    if algorithm == 'Bezier':
        n = len(p_list) - 1 # 控制点数量减一，即Bezier曲线的阶数
        result.append(p_list[0]) 
        u = du 
        # 在0到1之间的小增量：控制点的线性插值生成曲线
        # 步长设置为0.001：曲线的分辨率较高
        while u < 1:
            res = p_list.copy() # 每轮迭代生成当前u值下的曲线上点
            for i in range(n): # n次插值
                temp = [] # 中间点
                for j in range(len(res) - 1): # 相邻两点
                    x1, y1 = res[j]
                    x2, y2 = res[j + 1]
                    temp.append([(1 - u) * x1 + u * x2, (1 - u) * y1 + u * y2]) # De Casteljau算法
                res = temp.copy()
            x, y = round(res[0][0]), round(res[0][1])
            result.append([x, y])
            u += du
        result.append(p_list[-1])
    elif algorithm == 'B-spline':
        k = 4
        n = len(p_list)
        if n < k: 
            return []

#        k = 4 # 样条的阶数，取值为4，表示三次B样条曲线
#        u = 3 # 曲线在控制点的权重位置
        u = k - 1

        while u < n:
            x1, y1 = 0, 0
            for i in range(n):
                x0, y0 = p_list[i]
                res = de_boor_cox(i, k, u)
                x1 += x0 * res
                y1 += y0 * res
            result.append([round(x1), round(y1)])
            u += du
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    # TODO
    result = []
    for p in p_list:
        result.append([p[0] + dx, p[1] + dy])
    return result


def rotate(p_list, x, y, r, unit=True):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :param unit: (bool) 角度单位
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    # TODO
    # 根据单位选择：角度制 / 弧度制
    angle = r if not unit else math.radians(r)  # 转换为弧度制

    # 计算旋转矩阵的常量项
    cos_r, sin_r = math.cos(angle), math.sin(angle)

    def rotate_point(px, py):
        """单点旋转计算"""
        x0, y0 = px - x, py - y  # 平移到以旋转中心为原点的坐标系
        x_new = x0 * cos_r - y0 * sin_r
        y_new = x0 * sin_r + y0 * cos_r
        return [round(x_new) + x, round(y_new) + y]  # 旋转后平移回原坐标系

    # 对每个点进行旋转变换
    return [rotate_point(px, py) for px, py in p_list]


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    # TODO
    result = []
    for p in p_list:
        x0 = p[0] - x
        y0 = p[1] - y
        x_scaled = round(x0 * s) + x
        y_scaled = round(y0 * s) + y
        result.append([x_scaled, y_scaled])
    return result
#    return [[round((res[0] - x) * s) + x, round((res[1] - y) * s) + y] for res in p_list]


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    # TODO
    result = []
    # 检查裁剪窗口是否有效
    if x_min == x_max or y_min == y_max:
        return [[0, 0], [0, 0]]
    # 保证窗口左上角为 (x_min, y_min)，右下角为 (x_max, y_max)
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    # 提取线段的起点和终点
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]

    if algorithm == 'Cohen-Sutherland':
        def compute_code(x, y):
            """计算点 (x, y) 的区域编码"""
            code = 0
            if x < x_min:
                code |= 1  # 左
            if x > x_max:
                code |= 2  # 右
            if y < y_min:
                code |= 4  # 下
            if y > y_max:
                code |= 8  # 上
            return code
        while True:
            code0, code1 = compute_code(x0, y0), compute_code(x1, y1)
            # 完全在窗口内
            if code0 | code1 == 0:
                return [[int(x0), int(y0)], [int(x1), int(y1)]]
            # 完全在窗口外
            if code0 & code1 != 0:
                return [[0, 0], [0, 0]]

            # 找出需要裁剪的点
            code_out = code0 if code0 != 0 else code1
            if code_out & 1:  # 左
                x_new, y_new = x_min, y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
            elif code_out & 2:  # 右
                x_new, y_new = x_max, y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
            elif code_out & 4:  # 下
                x_new, y_new = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0), y_min
            elif code_out & 8:  # 上
                x_new, y_new = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0), y_max

            # 更新被裁剪点
            if code_out == code0:
                x0, y0 = x_new, y_new
            else:
                x1, y1 = x_new, y_new

    elif algorithm == 'Liang-Barsky':
        dx, dy = x1 - x0, y1 - y0
        u0, u1 = 0, 1  # 初始化参数范围

        def clip_param(p, q):
            """裁剪参数计算"""
            nonlocal u0, u1
            if p < 0:  # 潜在的进入点
                u0 = max(u0, q / p)
            elif p > 0:  # 潜在的离开点
                u1 = min(u1, q / p)
            elif q < 0:  # 平行且在线外
                return False
            return u0 <= u1

        # 四个边界
        if (not clip_param(-dx, x0 - x_min) or  # 左
            not clip_param(dx, x_max - x0) or   # 右
            not clip_param(-dy, y0 - y_min) or  # 下
            not clip_param(dy, y_max - y0)):    # 上
            return [[0, 0], [0, 0]]  # 裁剪窗口外的线段

        # 裁剪后的点
        clipped_x0, clipped_y0 = round(x0 + u0 * dx), round(y0 + u0 * dy)
        clipped_x1, clipped_y1 = round(x0 + u1 * dx), round(y0 + u1 * dy)
        result = [[clipped_x0, clipped_y0], [clipped_x1, clipped_y1]]

    return result