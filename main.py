#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频剪辑工具 - 主入口
支持切除视频开头的指定时间，保持原始质量
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow


def main():
    # 启用高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("Video Trimmer")
    app.setApplicationVersion("1.0.0")

    # 设置默认字体
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
