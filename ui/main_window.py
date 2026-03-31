#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口UI模块
Windows 11 风格的现代化界面
"""

import sys
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QMessageBox, QGroupBox, QDoubleSpinBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QDir
from PyQt5.QtGui import QFont, QDesktopServices

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_trimmer import VideoTrimmer


class WorkerThread(QThread):
    """工作线程 - 执行视频处理"""
    progress = pyqtSignal(float)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, trimmer, input_path, output_path, start_time):
        super().__init__()
        self.trimmer = trimmer
        self.input_path = input_path
        self.output_path = output_path
        self.start_time = start_time

    def run(self):
        try:
            def callback(progress):
                self.progress.emit(progress)

            self.trimmer.trim_video(
                self.input_path,
                self.output_path,
                self.start_time,
                callback
            )
            self.finished.emit(True, "视频处理完成！")
        except Exception as e:
            self.error.emit(str(e))


class VideoInfoThread(QThread):
    """后台加载视频信息，避免阻塞主界面。"""
    loaded = pyqtSignal(str, object)
    error = pyqtSignal(str)

    def __init__(self, trimmer, video_path):
        super().__init__()
        self.trimmer = trimmer
        self.video_path = video_path

    def run(self):
        try:
            video_info = self.trimmer.get_video_info(self.video_path)
            self.loaded.emit(self.video_path, video_info)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.trimmer = VideoTrimmer()
        self.video_info = None
        self.worker = None
        self.video_info_worker = None
        self.is_loading_video = False

        self.init_ui()
        self.check_ffmpeg()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("视频剪辑工具")
        self.setMinimumSize(760, 580)
        self.resize(880, 640)

        # 稳定优先的简洁样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f6f9;
            }
            QWidget {
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                font-size: 10pt;
                color: #203040;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 10.5pt;
                border: 1px solid #d8e0e8;
                border-radius: 10px;
                margin-top: 12px;
                padding: 16px 14px 14px 14px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 4px;
                color: #153a63;
                background: transparent;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: 700;
                color: #16324f;
            }
            QLabel#subtitleLabel {
                color: #5e7288;
                font-size: 10pt;
            }
            QLabel#statusBadge {
                border-radius: 12px;
                padding: 7px 12px;
                font-weight: 600;
                border: 1px solid transparent;
            }
            QLabel#statusBadge[state="ready"] {
                color: #236f45;
                background-color: #e9f7ee;
                border-color: #c9e7d3;
            }
            QLabel#statusBadge[state="warn"] {
                color: #9a5b00;
                background-color: #fff4df;
                border-color: #f3d49a;
            }
            QLabel#fieldLabel {
                color: #486078;
                font-weight: 600;
            }
            QLabel#helperText, QLabel#sectionHint, QLabel#statusText {
                color: #667a8d;
            }
            QLabel#infoBox, QLabel#previewBox {
                border: 1px solid #dce4ed;
                border-radius: 8px;
                background-color: #f8fbfe;
                padding: 10px 12px;
            }
            QLabel#infoBox {
                color: #26435f;
            }
            QLabel#previewBox {
                color: #0f5fa8;
                font-size: 12pt;
                font-weight: 700;
            }
            QPushButton {
                border-radius: 8px;
                padding: 0 16px;
                min-height: 36px;
                font-weight: 600;
                border: 1px solid transparent;
            }
            QPushButton#browseButton, QPushButton#ghostButton, QPushButton#secondaryButton {
                background-color: #ffffff;
                color: #1f405e;
                border-color: #c8d3df;
            }
            QPushButton#browseButton:hover, QPushButton#ghostButton:hover, QPushButton#secondaryButton:hover {
                background-color: #f3f8fc;
                border-color: #aebfd1;
            }
            QPushButton#browseButton:pressed, QPushButton#ghostButton:pressed, QPushButton#secondaryButton:pressed {
                background-color: #e6eef6;
            }
            QPushButton#primaryButton {
                background-color: #0f6cbd;
                color: white;
                border-color: #0f6cbd;
            }
            QPushButton#primaryButton:hover {
                background-color: #0f7dd9;
                border-color: #0f7dd9;
            }
            QPushButton#primaryButton:pressed {
                background-color: #0d5ea5;
                border-color: #0d5ea5;
            }
            QPushButton:disabled {
                background-color: #e5ebf2;
                color: #8191a1;
                border-color: #dbe3eb;
            }
            QLineEdit {
                border: 1px solid #c9d5e2;
                border-radius: 8px;
                padding: 6px 10px;
                min-height: 30px;
                background-color: #ffffff;
                selection-background-color: #0f6cbd;
            }
            QLineEdit:focus {
                border: 1px solid #0f6cbd;
            }
            QDoubleSpinBox {
                border: 1px solid #c9d5e2;
                border-radius: 8px;
                padding: 6px 10px;
                min-height: 30px;
                background-color: #ffffff;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #0f6cbd;
            }
            QProgressBar {
                border: 1px solid #d1dbe5;
                border-radius: 8px;
                text-align: center;
                min-height: 18px;
                background-color: #eef3f8;
                color: #284560;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1787d8,
                    stop: 1 #0f6cbd
                );
                border-radius: 7px;
            }
        """)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 18, 20, 18)

        # 顶部说明
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        hero_text_layout = QVBoxLayout()
        hero_text_layout.setSpacing(4)
        title_label = QLabel("视频剪辑工具")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("快速裁掉视频开头片段，保留原始画质与编码，适合录屏和课程视频的即时整理。")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setWordWrap(True)
        hero_text_layout.addWidget(title_label)
        hero_text_layout.addWidget(subtitle_label)
        header_layout.addLayout(hero_text_layout, 1)

        self.ffmpeg_badge = QLabel("正在检测 FFmpeg")
        self.ffmpeg_badge.setObjectName("statusBadge")
        self.ffmpeg_badge.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.ffmpeg_badge, 0, Qt.AlignTop)
        main_layout.addLayout(header_layout)

        # 视频选择组
        video_group = QGroupBox("文件")
        video_layout = QGridLayout()
        video_layout.setHorizontalSpacing(12)
        video_layout.setVerticalSpacing(12)
        video_layout.setColumnStretch(1, 1)

        input_label = QLabel("输入文件")
        input_label.setObjectName("fieldLabel")
        input_label.setFixedWidth(72)
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("点击右侧按钮选择需要剪辑的视频...")
        self.input_path_edit.setReadOnly(True)
        self.input_btn = QPushButton("选择视频")
        self.input_btn.setObjectName("browseButton")
        self.input_btn.setFixedWidth(100)
        self.input_btn.clicked.connect(self.select_input_video)
        video_layout.addWidget(input_label, 0, 0)
        video_layout.addWidget(self.input_path_edit, 0, 1)
        video_layout.addWidget(self.input_btn, 0, 2)

        output_label = QLabel("输出文件")
        output_label.setObjectName("fieldLabel")
        output_label.setFixedWidth(72)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("输出文件会自动生成在原视频目录...")
        self.output_path_edit.setReadOnly(True)
        self.output_btn = QPushButton("打开目录")
        self.output_btn.setObjectName("browseButton")
        self.output_btn.setFixedWidth(100)
        self.output_btn.clicked.connect(self.open_output_directory)
        video_layout.addWidget(output_label, 1, 0)
        video_layout.addWidget(self.output_path_edit, 1, 1)
        video_layout.addWidget(self.output_btn, 1, 2)

        self.output_hint_label = QLabel("输出文件名会自动追加 `_trimmed`，右侧按钮直接打开所在目录。")
        self.output_hint_label.setObjectName("helperText")
        self.output_hint_label.setWordWrap(True)
        video_layout.addWidget(self.output_hint_label, 2, 1, 1, 2)

        video_group.setLayout(video_layout)
        main_layout.addWidget(video_group)

        # 时间设置组
        time_group = QGroupBox("剪辑设置")
        time_layout = QVBoxLayout()
        time_layout.setSpacing(12)

        self.info_label = QLabel("请先选择视频文件")
        self.info_label.setObjectName("infoBox")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(48)
        time_layout.addWidget(self.info_label)

        # 移除时间设置
        time_input_layout = QHBoxLayout()
        time_input_layout.setSpacing(12)
        remove_label = QLabel("移除开头")
        remove_label.setObjectName("fieldLabel")
        remove_label.setFixedWidth(72)
        self.time_spin = QDoubleSpinBox()
        self.time_spin.setRange(0, 9999)
        self.time_spin.setSuffix(" 秒")
        self.time_spin.setDecimals(2)
        self.time_spin.setMinimumWidth(160)
        self.time_spin.setEnabled(False)
        self.time_spin.valueChanged.connect(self.update_preview)
        time_input_layout.addWidget(remove_label)
        time_input_layout.addWidget(self.time_spin, 0)
        precision_label = QLabel("支持 0.01 秒精度")
        precision_label.setObjectName("helperText")
        time_input_layout.addWidget(precision_label)
        time_input_layout.addStretch()
        time_layout.addLayout(time_input_layout)

        self.preview_label = QLabel("剩余时长: -- 秒")
        self.preview_label.setObjectName("previewBox")
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(54)
        time_layout.addWidget(self.preview_label)

        time_group.setLayout(time_layout)
        main_layout.addWidget(time_group)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        self.trim_btn = QPushButton("开始剪辑")
        self.trim_btn.setObjectName("primaryButton")
        self.trim_btn.setFixedWidth(120)
        self.trim_btn.setEnabled(False)
        self.trim_btn.clicked.connect(self.start_trim)
        button_layout.addWidget(self.trim_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setFixedWidth(120)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 状态栏和日志
        status_layout = QHBoxLayout()
        status_layout.setSpacing(12)
        self.status_label = QLabel("就绪，选择视频后即可开始。")
        self.status_label.setObjectName("statusText")
        self.status_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        status_layout.addWidget(self.status_label, 1)

        self.log_btn = QPushButton("查看日志")
        self.log_btn.setObjectName("ghostButton")
        self.log_btn.setFixedWidth(110)
        self.log_btn.clicked.connect(self.view_log)
        status_layout.addWidget(self.log_btn, 0, Qt.AlignRight)
        main_layout.addLayout(status_layout)

        self.set_badge_state("ready", "FFmpeg 已就绪")
        self.refresh_controls()

    def check_ffmpeg(self):
        """检查FFmpeg是否可用"""
        if not self.trimmer.is_ffmpeg_available():
            self.set_badge_state("warn", "FFmpeg 未就绪")
            msg = QMessageBox(self)
            msg.setWindowTitle("警告")
            msg.setText("未检测到FFmpeg")
            msg.setInformativeText(
                "FFmpeg未找到，程序将无法处理视频。\n\n"
                "当前程序已包含FFmpeg，可能路径配置有问题。\n"
                "请尝试重新下载程序。"
            )
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        self.set_badge_state("ready", "FFmpeg 已就绪")

    def set_badge_state(self, state, text):
        """更新顶部状态徽标。"""
        self.ffmpeg_badge.setProperty("state", state)
        self.ffmpeg_badge.setText(text)
        self.ffmpeg_badge.style().unpolish(self.ffmpeg_badge)
        self.ffmpeg_badge.style().polish(self.ffmpeg_badge)

    @staticmethod
    def format_path(path):
        """统一路径显示为 Windows 原生格式。"""
        if not path:
            return ""
        return QDir.toNativeSeparators(os.path.normpath(path))

    def select_input_video(self):
        """选择输入视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm);;所有文件 (*.*)"
        )

        if file_path:
            normalized_path = self.format_path(file_path)
            self.input_path_edit.setText(normalized_path)
            self.load_video_info(normalized_path)

    def load_video_info(self, video_path):
        """加载视频信息"""
        self.video_info = None
        self.is_loading_video = True
        self.info_label.setText("正在读取视频信息...")
        self.preview_label.setText("剩余时长: -- 秒")
        self.output_path_edit.clear()
        self.time_spin.blockSignals(True)
        self.time_spin.setRange(0, 0)
        self.time_spin.setValue(0)
        self.time_spin.blockSignals(False)
        self.status_label.setText("正在加载视频信息...")
        self.refresh_controls()

        self.video_info_worker = VideoInfoThread(self.trimmer, video_path)
        self.video_info_worker.loaded.connect(self.video_info_loaded)
        self.video_info_worker.error.connect(self.video_info_error)
        self.video_info_worker.finished.connect(self.video_info_worker.deleteLater)
        self.video_info_worker.start()

    def video_info_loaded(self, video_path, video_info):
        """视频信息加载完成"""
        self.is_loading_video = False
        self.video_info = video_info

        duration_min = self.video_info['duration'] / 60
        info_text = (
            f"时长: {duration_min:.2f} 分钟 | "
            f"分辨率: {self.video_info['width']}x{self.video_info['height']} | "
            f"码率: {self.video_info['bitrate']} kb/s | "
            f"帧率: {self.video_info['fps']:.2f} fps"
        )
        self.info_label.setText(info_text)

        max_trim_time = max(self.video_info['duration'] - 0.01, 0)
        self.time_spin.blockSignals(True)
        self.time_spin.setRange(0, max_trim_time)
        self.time_spin.setValue(0)
        self.time_spin.blockSignals(False)

        input_path = Path(video_path)
        output_name = f"{input_path.stem}_trimmed{input_path.suffix}"
        output_path = input_path.parent / output_name
        self.output_path_edit.setText(self.format_path(str(output_path)))

        self.refresh_controls()
        self.update_preview()
        self.status_label.setText("视频加载完成")

    def video_info_error(self, error_msg):
        """视频信息加载失败"""
        self.is_loading_video = False
        self.video_info = None
        self.info_label.setText("视频信息加载失败")
        self.preview_label.setText("剩余时长: -- 秒")
        self.output_path_edit.clear()
        self.refresh_controls()
        self.status_label.setText("加载失败")
        QMessageBox.critical(self, "错误", f"加载视频失败:\n{error_msg}")

    def open_output_directory(self):
        """打开输出文件所在目录。"""
        output_path = self.output_path_edit.text().strip()

        if not output_path:
            QMessageBox.information(self, "提示", "请先选择视频并生成输出路径")
            return

        output_dir = self.format_path(str(Path(output_path).parent))
        if not os.path.isdir(output_dir):
            QMessageBox.warning(self, "提示", f"输出目录不存在：\n{output_dir}")
            return

        if QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir)):
            return

        try:
            os.startfile(output_dir)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"打开目录失败：\n{str(e)}")

    def update_preview(self):
        """更新预览信息"""
        if self.video_info:
            start_time = self.time_spin.value()
            remaining = self.video_info['duration'] - start_time
            remaining_min = remaining / 60
            self.preview_label.setText(f"剩余时长: {remaining:.2f} 秒 ({remaining_min:.2f} 分钟)")
        else:
            self.preview_label.setText("剩余时长: -- 秒")

    def start_trim(self):
        """开始剪辑"""
        input_path = self.format_path(self.input_path_edit.text())
        output_path = self.format_path(self.output_path_edit.text())
        start_time = self.time_spin.value()

        if self.is_loading_video:
            QMessageBox.warning(self, "警告", "视频信息仍在加载中，请稍候")
            return

        if not self.video_info:
            QMessageBox.warning(self, "警告", "请先加载有效的视频文件")
            return

        if not input_path or not output_path:
            QMessageBox.warning(self, "警告", "请先选择输入和输出文件")
            return

        if start_time <= 0:
            QMessageBox.warning(self, "警告", "请设置要移除的时间")
            return

        # 禁用按钮
        self.refresh_controls(is_processing=True)

        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("正在处理视频...")

        # 创建工作线程
        self.worker = WorkerThread(self.trimmer, input_path, output_path, start_time)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.trim_finished)
        self.worker.error.connect(self.trim_error)
        self.worker.start()

    def update_progress(self, value):
        """更新进度"""
        self.progress_bar.setValue(int(value))

    def trim_finished(self, success, message):
        """剪辑完成"""
        self.reset_ui()
        self.progress_bar.setValue(100)
        self.status_label.setText(message)

        QMessageBox.information(
            self,
            "完成",
            f"{message}\n\n输出文件:\n{self.output_path_edit.text()}"
        )

    def trim_error(self, error_msg):
        """剪辑错误"""
        self.reset_ui()
        self.progress_bar.setVisible(False)
        self.status_label.setText("处理失败")

        QMessageBox.critical(self, "错误", f"视频处理失败:\n{error_msg}")

    def cancel_operation(self):
        """取消操作"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.status_label.setText("操作已取消")

        self.reset_ui()
        self.progress_bar.setVisible(False)

    def reset_ui(self):
        """重置UI状态"""
        self.refresh_controls()

    def refresh_controls(self, is_processing=False):
        """根据当前状态刷新控件可用性。"""
        has_video = self.video_info is not None
        can_edit_video = has_video and not self.is_loading_video and not is_processing

        self.input_btn.setEnabled(not self.is_loading_video and not is_processing)
        self.output_btn.setEnabled(can_edit_video)
        self.time_spin.setEnabled(can_edit_video)
        self.trim_btn.setEnabled(can_edit_video)
        self.cancel_btn.setEnabled(is_processing)

    def view_log(self):
        """打开日志文件"""
        import tempfile
        log_path = os.path.join(tempfile.gettempdir(), 'video_trimmer_debug.log')

        if os.path.exists(log_path):
            if QDesktopServices.openUrl(QUrl.fromLocalFile(log_path)):
                return

            try:
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                subprocess.Popen(['notepad.exe', log_path], creationflags=creationflags)
            except Exception as e:
                QMessageBox.warning(self, "日志", f"打开日志失败:\n{str(e)}")
            return

        QMessageBox.information(self, "日志", "日志文件不存在")
