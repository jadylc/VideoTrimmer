#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频处理核心模块
使用FFmpeg进行视频剪辑，保持原始质量
"""

import subprocess
import os
import sys
import re
import locale
from pathlib import Path
import tempfile


# 创建日志文件
log_file = os.path.join(tempfile.gettempdir(), 'video_trimmer_debug.log')

def log(msg):
    """写入日志"""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{msg}\n")


class VideoTrimmer:
    """视频剪辑器"""

    def __init__(self):
        """初始化"""
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """
        查找FFmpeg可执行文件
        优先级：打包目录 > 当前目录 > 系统PATH
        """
        log("=" * 50)
        log("开始查找FFmpeg...")
        log(f"sys.frozen = {getattr(sys, 'frozen', False)}")

        # 首先检查打包后的目录（PyInstaller打包后）
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_path = sys._MEIPASS
            log(f"打包环境，_MEIPASS = {base_path}")

            ffmpeg_exe = os.path.join(base_path, 'ffmpeg.exe')
            log(f"检查路径1: {ffmpeg_exe}, 存在: {os.path.exists(ffmpeg_exe)}")
            if os.path.exists(ffmpeg_exe):
                log(f"找到FFmpeg: {ffmpeg_exe}")
                return ffmpeg_exe

            # 也可能在临时目录
            ffmpeg_exe = os.path.join(os.path.dirname(sys.executable), 'ffmpeg.exe')
            log(f"检查路径2: {ffmpeg_exe}, 存在: {os.path.exists(ffmpeg_exe)}")
            if os.path.exists(ffmpeg_exe):
                log(f"找到FFmpeg: {ffmpeg_exe}")
                return ffmpeg_exe

        # 检查当前目录
        current_dir = Path(__file__).parent
        log(f"当前目录: {current_dir}")

        ffmpeg_exe = current_dir / 'ffmpeg.exe'
        log(f"检查路径3: {ffmpeg_exe}, 存在: {ffmpeg_exe.exists()}")
        if ffmpeg_exe.exists():
            log(f"找到FFmpeg: {ffmpeg_exe}")
            return str(ffmpeg_exe)

        # 检查系统PATH
        log("检查系统PATH...")
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                log("在系统PATH中找到FFmpeg")
                return 'ffmpeg'
        except FileNotFoundError:
            log("系统PATH中未找到FFmpeg")

        log("未找到FFmpeg!")
        log("=" * 50)
        return None

    def _decode_output(self, output):
        """解码FFmpeg输出，兼容中文路径和不同终端编码。"""
        if not output:
            return ""

        if isinstance(output, str):
            return output

        encodings = [
            'utf-8',
            locale.getpreferredencoding(False),
            'gbk',
        ]

        for encoding in encodings:
            try:
                return output.decode(encoding)
            except UnicodeDecodeError:
                continue

        return output.decode('utf-8', errors='replace')

    def is_ffmpeg_available(self):
        """检查FFmpeg是否可用"""
        return self.ffmpeg_path is not None

    def get_video_info(self, video_path):
        """
        获取视频信息

        Args:
            video_path: 视频文件路径

        Returns:
            dict: 包含时长、分辨率、码率等信息
        """
        log(f"get_video_info被调用")
        log(f"ffmpeg_path: {self.ffmpeg_path}")
        log(f"video_path: {video_path}")

        if not self.ffmpeg_path:
            log("FFmpeg未找到，抛出异常")
            raise Exception("FFmpeg未找到")

        # 使用utf-8编码处理路径
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-hide_banner'
        ]

        log(f"执行命令: {' '.join(cmd)}")

        try:
            # Windows特定设置
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                timeout=10,
                env=env,
                startupinfo=startupinfo
            )

            log(f"FFmpeg返回码: {result.returncode}")

            # 从stderr中解析视频信息，避免默认编码在中文路径下把stderr读成None
            output = self._decode_output(result.stderr)
            if not output:
                output = self._decode_output(result.stdout)

            log(f"FFmpeg stderr字节长度: {len(result.stderr or b'')}")
            log(f"FFmpeg stdout字节长度: {len(result.stdout or b'')}")
            log(f"FFmpeg 输出内容:\n{output[:1000]}")

            if not output.strip():
                raise Exception("FFmpeg未返回可解析的视频信息")

            info = {
                'duration': 0,
                'width': 0,
                'height': 0,
                'bitrate': 0,
                'fps': 0,
                'codec': '',
                'size': 0
            }

            # 提取时长
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', output)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                info['duration'] = hours * 3600 + minutes * 60 + seconds
                log(f"解析到时长: {info['duration']}")

            # 提取分辨率和帧率
            video_stream = re.search(
                r'Video:.*?(\d{3,4})x(\d{3,4}).*?(\d+(?:\.\d+)?)\s*fps',
                output
            )
            if video_stream:
                info['width'] = int(video_stream.group(1))
                info['height'] = int(video_stream.group(2))
                info['fps'] = float(video_stream.group(3))
                log(f"解析到分辨率: {info['width']}x{info['height']}, fps: {info['fps']}")

            # 提取码率
            bitrate_match = re.search(r'bitrate:\s*(\d+)\s*kb/s', output)
            if bitrate_match:
                info['bitrate'] = int(bitrate_match.group(1))
                log(f"解析到码率: {info['bitrate']}")

            # 提取编码器
            codec_match = re.search(r'Video:\s*(\w+)', output)
            if codec_match:
                info['codec'] = codec_match.group(1)
                log(f"解析到编码器: {info['codec']}")

            # 获取文件大小
            file_size = os.path.getsize(video_path)
            info['size'] = file_size
            log(f"文件大小: {file_size}")

            if info['duration'] <= 0:
                raise Exception("无法解析视频时长，请检查视频文件或FFmpeg输出")

            return info

        except Exception as e:
            log(f"异常: {str(e)}")
            raise Exception(f"获取视频信息失败: {str(e)}")

    def trim_video(self, input_path, output_path, start_time, progress_callback=None):
        """
        剪切视频（移除开头指定时间）

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start_time: 要移除的开头时长（秒）
            progress_callback: 进度回调函数

        Returns:
            bool: 是否成功
        """
        if not self.ffmpeg_path:
            raise Exception("FFmpeg未找到，请先安装FFmpeg")

        if not os.path.exists(input_path):
            raise Exception("输入文件不存在")

        # 获取视频总时长
        try:
            video_info = self.get_video_info(input_path)
            total_duration = video_info['duration']
        except Exception as e:
            raise Exception(f"无法获取视频时长: {str(e)}")

        if start_time >= total_duration:
            raise Exception("移除时间不能大于等于视频总时长")

        # 构建FFmpeg命令
        # 使用 -ss 参数指定起始时间
        # 使用 -c:v copy -c:a copy 保持原始编码，不重新编码
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-ss', str(start_time),  # 从指定时间开始
            '-c:v', 'copy',  # 视频流直接复制，不重新编码
            '-c:a', 'copy',  # 音频流直接复制，不重新编码
            '-y',  # 覆盖输出文件
            output_path
        ]

        try:
            # Windows特定设置
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                startupinfo=startupinfo
            )

            # 读取进度
            for line in process.stderr:
                if progress_callback:
                    # 解析时间信息来计算进度
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if time_match:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        seconds = float(time_match.group(3))
                        current_time = hours * 3600 + minutes * 60 + seconds

                        # 计算进度百分比（基于已处理的时间）
                        progress = min((current_time / (total_duration - start_time)) * 100, 100)
                        progress_callback(progress)

            # 等待进程完成
            return_code = process.wait()

            if return_code != 0:
                raise Exception(f"FFmpeg处理失败，返回码: {return_code}")

            return True

        except KeyboardInterrupt:
            process.kill()
            raise Exception("用户取消操作")
        except Exception as e:
            if 'process' in locals():
                process.kill()
            raise Exception(f"视频处理失败: {str(e)}")
