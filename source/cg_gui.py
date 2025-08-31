#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg # 自定义的图形算法模块
from typing import Optional # 类型提示：表示一个变量可能有值，也可能是None
import math     # TODO
import pickle   # TODO: 对象的序列化和反序列化（对象 <-> 字节流）

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QGraphicsRectItem, # TODO: 绘制矩形
    QColorDialog, QInputDialog, QFileDialog, QMessageBox) # TODO: 弹出对话框的类
# 用于绘图和事件处理
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QKeySequence # TODO: 快捷键
# 用于定义矩形区域
from PyQt5.QtCore import QRectF, Qt # TODO: Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    # 构造函数，初始化画布，设置初始状态和变量
    def __init__(self, *args):
        super().__init__(*args) # 初始化父类
        self.main_window = None # 指向主窗口的引用
        self.list_widget = None # 指向列表控件的引用，用于显示图元ID
        self.item_dict = {}     # 存储图元对象的字典
        self.selected_id = ''   # 当前选中的图元ID
        
        self.status = ''            # 当前画布的状态
        self.temp_algorithm = ''    # 临时存储算法名称
        self.temp_id = ''           # 临时存储图元ID
        self.temp_item = None       # 临时存储图元对象
        self.temp_color = QColor(0, 0, 0)   # TODO: 临时存储画笔颜色
        
        # TODO: 辅助数据的初始化
        # TRANSFORM
        self.origin_p_list = None   
        self.origin_pos = None
        self.trans_center = None
        # CLIP
        self.border = None

    # TODO: 开始绘制不同类型的图形（设置当前状态&算法）
    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        #self.temp_algorithm = algorithm
        self.temp_id = item_id
    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None   # TODO
    
    def finish_draw(self):
        self.temp_id = self.main_window.get_id()    # 完成绘图操作，生成图元ID
    
    # TODO: transformation
    def set_transform_status(self, status, selected_only=False):
        """
        设置画布的变换状态。

        :param status: 变换类型，如 'translate', 'scale', 'rotate', 'clip' 等。
        :param selected_only: 是否仅对选中的图元进行变换，默认为 False。
        """
        self.status = status
        self.temp_item = None
        self.trans_center = None
        self.origin_p_list = None
        self.origin_pos = None

        # 选中了图元 并且 仅对选中的图元
        if selected_only and self.selected_id:
            self.temp_item = self.item_dict.get(self.selected_id)
        else:
            for k in self.item_dict:
                self.temp_item = self.item_dict[k]
                break  # 只取第一个图元对象

    def start_translate(self):
        self.set_transform_status('translate', selected_only=True)
    def start_scale(self):
        self.set_transform_status('scale', selected_only=True)
    def start_rotate(self):
        self.set_transform_status('rotate', selected_only=True)
    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.set_transform_status('clip', selected_only=True)
    # TODO: 刪除
    def start_delete(self):
        if not self.selected_id:
            return  # 提前退出，减少嵌套

        self.main_window.isModified = True  # 标记数据被修改
        # 获取选中元素的对象
        temp_id = self.selected_id
        self.temp_item = self.item_dict[temp_id]
        # 清除场景中的图形对象和内部引用
        self.clear_selection()
        self.scene().removeItem(self.temp_item)
        del self.item_dict[temp_id]
        self.temp_item = None
        # 从列表控件中移除对应项
        items = self.list_widget.findItems(temp_id, Qt.MatchContains)
        if items:  # 确保找到了匹配项
            self.list_widget.takeItem(self.list_widget.row(items[0]))
        # 刷新场景  
        self.updateScene([self.sceneRect()])

    # TODO: 選擇模式
    def start_select(self):
        self.status = 'selecting'     
     
    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # 獲取點擊位置
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())

        # TODO: 根據status執行操作
        if self.status in ['line', 'polygon', 'ellipse']:
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.temp_color)
            self.scene().addItem(self.temp_item)
            self.main_window.isModified = True
        elif self.status == 'curve':
            if self.temp_item is None:
                self.temp_id = self.main_window.get_id()
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
            self.main_window.isModified = True

        elif self.status == 'selecting':
            selected = self.scene().itemAt(pos, QTransform())
            if selected in self.item_dict.values():  # 检查是否选中了有效图元
                if self.selected_id:  # 如果之前有选中其他图元，取消其选中状态
                    previous_item = self.item_dict[self.selected_id]
                    previous_item.selected = False
                    previous_item.update()
                # 更新当前选中图元的状态
                self.selected_id = next(key for key, value in self.item_dict.items() if value == selected)
                selected.selected = True
                selected.update()
                self.main_window.list_widget.setCurrentRow(int(self.selected_id))

        elif self.status in ["translate", "rotate", "scale", "clip"]:
            if self.selected_id:
                self.main_window.isModified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
        
            if self.status == "translate":
                self.origin_pos = pos
            elif self.status in ["rotate", "scale"]:
                if self.trans_center is None:
                    self.trans_center = pos
                else:
                    self.origin_pos = pos
            elif self.status == "clip" and self.temp_item.item_type == 'line':  # 針對綫段
                self.origin_pos = pos
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        # TODO
        if self.temp_item:
            if self.status in ['line', 'ellipse']:
                # 更新最后一个点
                self.temp_item.p_list[1] = [x, y]
            elif self.status in ['polygon', 'curve']:
                # 更新多边形或曲线的最后一个点
                self.temp_item.p_list[-1] = [x, y]
            elif self.status == "translate" and self.selected_id:
                # 平移
                dx, dy = x - int(self.origin_pos.x()), y - int(self.origin_pos.y())
                self.temp_item.p_list = alg.translate(self.origin_p_list, dx, dy)
            elif self.status == "rotate" and self.selected_id and self.trans_center and self.origin_pos:
                # 旋转
                r = self.calculate_rotation(x, y)
                self.temp_item.p_list = alg.rotate(self.origin_p_list, 0, 0, r)
            elif self.status == "scale" and self.selected_id and self.trans_center and self.origin_pos:
                # 缩放
                scale_factor = self.calculate_scale_factor(x, y)
                if scale_factor is not None:
                    self.temp_item.p_list = alg.scale(
                        self.origin_p_list,
                        int(self.trans_center.x()),
                        int(self.trans_center.y()),
                        scale_factor
                    )
            elif self.status == "clip" and self.selected_id and self.origin_pos and self.temp_item.item_type == "line":
                # 裁剪
                x_min, x_max = sorted([int(self.origin_pos.x()), x])
                y_min, y_max = sorted([int(self.origin_pos.y()), y])
                if self.border is None:
                    self.border = QGraphicsRectItem(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
                    self.scene().addItem(self.border)
                    self.border.setPen(QColor(0, 255, 255))
                else:
                    self.border.setRect(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)

        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def calculate_rotation(self, current_x, current_y):
        # 计算原点到旋转中心的向量
        origin_dx = int(self.origin_pos.x() - self.trans_center.x())
        origin_dy = int(self.origin_pos.y() - self.trans_center.y())
        origin_distance = math.sqrt(origin_dx ** 2 + origin_dy ** 2)
        # 计算当前点到旋转中心的向量
        current_dx = current_x - int(self.trans_center.x())
        current_dy = current_y - int(self.trans_center.y())
        current_distance = math.sqrt(current_dx ** 2 + current_dy ** 2)
        # 避免除以零的情况
        if origin_distance > 0 and current_distance > 0:
            sin_origin = origin_dy / origin_distance
            cos_origin = origin_dx / origin_distance
            sin_current = current_dy / current_distance
            cos_current = current_dx / current_distance
            # 计算夹角的正弦和余弦
            delta_sin = sin_current * cos_origin - cos_current * sin_origin
            delta_cos = cos_current * cos_origin + sin_current * sin_origin
            # 根据夹角的余弦正负值确定方向
            if delta_cos >= 0:
                rotation_angle = math.asin(delta_sin)
            else:
                rotation_angle = math.pi - math.asin(delta_sin)
            # 返回角度值
            return math.degrees(rotation_angle)
        return 0

    def calculate_scale_factor(self, current_x, current_y):
        # 计算初始点到缩放中心的距离
        initial_dx = int(self.origin_pos.x() - self.trans_center.x())
        initial_dy = int(self.origin_pos.y() - self.trans_center.y())
        initial_distance = math.sqrt(initial_dx ** 2 + initial_dy ** 2)

        # 避免初始距离为零的情况
        if initial_distance > 0:
            # 计算当前点到缩放中心的距离
            current_dx = current_x - int(self.trans_center.x())
            current_dy = current_y - int(self.trans_center.y())
            current_distance = math.sqrt(current_dx ** 2 + current_dy ** 2)
            # 返回缩放比例
            return current_distance / initial_distance
        return None

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        # TODO
        if self.status == 'polygon':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            #pass
        if self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'curve':
            self.item_dict[self.temp_id] = self.temp_item
            if not self.list_widget.findItems(self.temp_id, Qt.MatchContains):
                self.list_widget.addItem(self.temp_id)
        elif self.status == 'clip':
            pos = self.mapToScene(event.localPos().toPoint())
            x, y = int(pos.x()), int(pos.y())
            if self.selected_id and self.temp_item.item_type == 'line':
                self.handle_clip_event(x, y)
        # 更新场景并传递事件
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)

    def handle_clip_event(self, x, y):
        """处理裁剪操作的辅助函数，裁剪图形项"""
        # 计算裁剪区域的最小和最大坐标
        origin_x, origin_y = int(self.origin_pos.x()), int(self.origin_pos.y())
        x, y = int(x), int(y)
        x_min, x_max = min(origin_x, x), max(origin_x, x)
        y_min, y_max = min(origin_y, y), max(origin_y, y)

        # 如果裁剪框的尺寸太小，跳过裁剪
        if x_min == x_max or y_min == y_max:
            return

        # 获取裁剪后有效的点
        temp_p_list = alg.clip(self.origin_p_list, x_min, y_min, x_max, y_max, self.temp_algorithm)

        # 如果裁剪后没有有效的点    
        if not temp_p_list:
            # 标记图形项为删除，隐藏图形项并清空点列表
            self.temp_item.setVisible(False)
            self.temp_item.p_list = []
            self.item_dict[self.selected_id] = None  # 清空图形项引用
            self.clear_selection()  # 清除选择状态
        else:
            # 更新图形项为裁剪后的点列表，并确保其可见
            self.temp_item.p_list = temp_p_list
            self.temp_item.setVisible(True)

        # 移除裁剪框
        if self.border is not None:
            self.scene().removeItem(self.border)
            self.border = None


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '' ,color=QColor(0,0,0),parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color  # TODO

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))   # red
                painter.drawRect(self.boundingRect())
        # TODO
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0)) 
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            #painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        # TODO
        # Helper function to compute bounding box
        # 计算图元点的最小值和最大值，返回包围矩形的四个角坐标
        def calculate_bounding_box(p_list):
            x_min, y_min = p_list[0]    # 初始化最小值，取第一个点的坐标
            x_max, y_max = x_min, y_min # 初始化最大值，取第一个点的坐标
            for point in p_list:
                x, y = point
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            return x_min, y_min, x_max, y_max

        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x_min, y_min, x_max, y_max = min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)

        elif self.item_type == 'polygon':
            x_min, y_min, x_max, y_max = calculate_bounding_box(self.p_list)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x_min, y_min, x_max, y_max = min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)

        elif self.item_type == 'curve':
            x_min, y_min, x_max, y_max = calculate_bounding_box(self.p_list)

        # Width and height of the bounding box
        w = x_max - x_min
        h = y_max - y_min
        return QRectF(x_min - 1, y_min - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0   # 图元计数器

        # TODO
        # 初始化画布宽高，范围限定为 100-1000
        self.width = 600    # 画布的宽度
        self.height = 600   # 画布的高度
        self.isModified = False    # 画布是否被修改
        self.opened_filename = ''   # 当前打开的文件名
        
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        set_pen_act.setShortcut(QKeySequence("Ctrl+P")) # TODO：快捷键
        reset_canvas_act = file_menu.addAction('重置画布')
        reset_canvas_act.setShortcut(QKeySequence("Ctrl+R"))
        # TODO：打开画布
        open_canvas_act = file_menu.addAction('打开画布')
        open_canvas_act.setShortcut(QKeySequence("Ctrl+O"))
        # TODO：保存画布
        save_canvas_act = file_menu.addAction('保存画布')
        save_canvas_act.setShortcut(QKeySequence("Ctrl+S"))
        exit_act = file_menu.addAction('退出')
        exit_act.setShortcut(QKeySequence("Ctrl+X"))    # TODO：快捷键

        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')

        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        # TODO：删除
        delete_act = edit_menu.addAction('删除')
        
        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        # TODO
        reset_canvas_act.triggered.connect(lambda: self.reset_canvas_action())
        # lambda: 将其包裹，使它成为一个延迟执行的函数
        open_canvas_act.triggered.connect(self.open_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        # line
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_DDA_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        # polygon
        polygon_dda_act.triggered.connect(self.polygon_DDA_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        # ellipse
        ellipse_act.triggered.connect(self.ellipse_action)
        # curve
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        # transform
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        delete_act.triggered.connect(self.delete_action)
        #
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    #
    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # TODO: 重置画布
    def reset_canvas_action(self, resize=True):
        if resize:
            valid_input = False
            while not valid_input:
                # 获取宽度
                width, ok = QInputDialog.getInt(self, '请输入', '宽度', 800, 100, 1000)
                if ok and 100 <= width <= 1000:
                    self.width = width
                    valid_input = True
                else:
                    break
                    QMessageBox.warning(self, '无效输入', '宽度必须在100到1000之间，请重新输入.')
            valid_input = False
            while not valid_input:
                # 获取高度
                height, ok = QInputDialog.getInt(self, '请输入', '高度', 800, 100, 1000)
                if ok and 100 <= height <= 1000:
                    self.height = height
                    valid_input = True
                else:
                    break
                    QMessageBox.warning(self, '无效输入', '高度必须在100到1000之间，请重新输入.')
        # 清除选择和项目
        self.list_widget.clearSelection()
        self.list_widget.clear()
        self.canvas_widget.clear_selection()
        self.canvas_widget.item_dict.clear()
        self.canvas_widget.scene().clear()
        # 重置相关变量
        self.item_cnt = 0
        self.canvas_widget.status = ''
        self.opened_filename = ''
        self.isModified = False
        # 设置场景矩形大小和画布尺寸
        self.scene.setSceneRect(0, 0, self.width, self.height)
        self.canvas_widget.setFixedSize(self.width, self.height)

    # TODO: 打开画布
    def open_canvas_action(self):
        # 如果画布正在绘制多边形或曲线，先结束当前绘制
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
    
        self.statusBar().showMessage('打开画布')

        # 检查画布是否已修改，提示保存
        if (self.opened_filename == '' and len(self.canvas_widget.item_dict) > 0) or self.isModified:
            reply = QMessageBox.question(self, '提示', '是否保存更改？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()  # 保存画布
            elif reply == QMessageBox.Cancel:
                return
    
        # 重置画布
        self.reset_canvas_action(False)
        self.statusBar().showMessage('打开画布')

        # 打开文件对话框，选择文件
        path, _ = QFileDialog.getOpenFileName(self, caption='打开画布', filter='BitMap文件 (*.bmp)')
    
        # 检查路径是否为空
        if path != '':
            try:
                # 打开文件并读取内容
                with open(path, 'rb') as fr:
                    # 假设文件是使用pickle序列化的
                    open_list = pickle.load(fr)

                    # 处理文件中的每个项
                    for item in open_list:
                        color = QColor(item[4][0], item[4][1], item[4][2])
                        temp_item = MyItem(item[0], item[1], item[2], item[3], color)
                        self.canvas_widget.scene().addItem(temp_item)  # 添加到画布
                        self.list_widget.addItem(item[0])  # 更新列表
                        self.canvas_widget.item_dict[item[0]] = temp_item  # 更新项目字典

                # 更新项计数
                self.item_cnt = len(open_list)

                # 设置窗口标题
                self.opened_filename = path  # 更新当前文件路径
                name = self.opened_filename.split('/')[-1].split('.')[0]  # 提取文件名
                self.setWindowTitle(f'MYCG - {name}')  # 更新窗口标题

            except Exception as e:
                QMessageBox.critical(self, '文件读取错误', f'打开文件时出错: {e}')

    # TODO: 保存画布
    def save_canvas_action(self):
        # 如果画布正在绘制多边形或曲线，先结束当前绘制
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()

        self.statusBar().showMessage('保存画布')

        # 保存的项目列表
        save_list = []

        # 构建保存的数据
        for item in self.canvas_widget.item_dict.values():
            save_list.append([item.id, item.item_type, item.p_list, item.algorithm, item.color.getRgb()])

        # 如果没有打开文件（即是新画布），需要保存到新路径
        if self.opened_filename == '':
            path, _ = QFileDialog.getSaveFileName(self, caption='保存画布', filter='BitMap文件 (*.bmp)')

            if path != '':
                try:
                    # 保存到选定路径
                    with open(path, 'wb') as fw:
                        pickle.dump(save_list, fw)
                    self.opened_filename = path
                    self.isModified = False

                    # 设置窗口标题
                    name = self.opened_filename.split('/')[-1].split('.')[0]
                    self.setWindowTitle(f'CG Demo - {name}')

                except Exception as e:
                    QMessageBox.critical(self, '保存错误', f'保存文件时出错: {e}')

        else:   
            # 如果已打开文件，直接保存到原文件
            try:
                with open(self.opened_filename, 'wb') as fw:
                    pickle.dump(save_list, fw)
                self.isModified = False
            except Exception as e:
                QMessageBox.critical(self, '保存错误', f'保存文件时出错: {e}')

    # TODO: 設置畫筆顔色
    def set_pen_action(self):
        temp_color = QColorDialog.getColor()
        if temp_color.isValid():
            self.canvas_widget.temp_color = temp_color

    # 启动绘制函数
    # TODO
    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def line_DDA_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def polygon_DDA_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def curve_bezier_action(self):
        # TODO: 避免不完整的圖形
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def curve_b_spline_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移')
    def rotate_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')
    def scale_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')
    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland裁剪')
    def clip_liang_barsky_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky裁剪')
    def delete_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_delete()
        self.statusBar().showMessage('删除')


# 主程序入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())