#!/usr/bin/python
# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2026/2/10 16:42
# @File           : alignment.py
# @IDE            : PyCharm
# @desc           :
from enum import Enum


class HorizontalAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlignment(str, Enum):
    TOP = "top"
    """ 顶对齐, 多的文字向下延伸  """
    CENTER = "center"
    """ 居中对齐, 文字向顶部和底部延伸 """
    BOTTOM = "bottom"
    """ 底对齐, 多的文字向上延伸 """
    ADAPT = "adapt"
    """ 固定区域, 字号自适应 """
    EXTEND = "extend"
    """ 高度满足, 水平延伸 """


# 图片字幕的遮罩
class ImageMaskType(int, Enum):
    NoMask = 0
    """ 无文本框 """
    RecMask = 1
    """ 跟随内容长度的矩形圆角文本框 """
    TextMask = 2
    """ 内容宽度文本框 """
    RecBgMask = 3
    """ 固定尺寸遮罩的矩形圆角文本框 """
