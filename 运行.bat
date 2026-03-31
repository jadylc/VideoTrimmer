@echo off
chcp 65001 >nul
echo ================================================
echo              视频剪辑工具 - 启动脚本
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [1/3] 检查Python依赖...
pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装Python依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查FFmpeg
echo [2/3] 检查FFmpeg...
if not exist ffmpeg.exe (
    echo [警告] 未在当前目录找到ffmpeg.exe
    echo.
    echo 请按以下步骤操作：
    echo 1. 访问 https://www.gyan.dev/ffmpeg/builds/
    echo 2. 下载 ffmpeg-git-full.7z
    echo 3. 解压后将 ffmpeg.exe 复制到本目录
    echo.
    echo 或者将FFmpeg添加到系统PATH环境变量
    echo.
    pause
)

REM 启动程序
echo [3/3] 启动程序...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败
    pause
)
