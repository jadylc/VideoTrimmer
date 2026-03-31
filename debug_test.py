#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试FFmpeg打包后的路径问题
"""

import sys
import os
import tempfile

def test_ffmpeg_path():
    """测试FFmpeg路径"""
    print("=" * 50)
    print("FFmpeg Path Test")
    print("=" * 50)

    # 检查是否为打包环境
    if getattr(sys, 'frozen', False):
        print("[OK] Running in packaged environment")
        base_path = sys._MEIPASS
        print(f"  _MEIPASS = {base_path}")

        # 检查ffmpeg.exe是否存在
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
        print(f"  Looking for FFmpeg: {ffmpeg_path}")
        print(f"  Exists: {os.path.exists(ffmpeg_path)}")

        # 列出_MEIPASS目录中的文件
        print(f"\n  _MEIPASS directory contents:")
        try:
            for item in os.listdir(base_path):
                print(f"    - {item}")
        except Exception as e:
            print(f"    Error: {e}")
    else:
        print("[FAIL] Running in development environment")
        print(f"  __file__ = {__file__}")

    print("=" * 50)

if __name__ == "__main__":
    test_ffmpeg_path()

if __name__ == "__main__":
    test_ffmpeg_path()
