# 视频剪辑工具 (Video Trimmer)

一个简单易用的Windows视频剪辑工具，可以快速切除视频开头的指定时间，同时保持原始视频的分辨率、码率和清晰度。

## 功能特点

- 🎬 **快速剪辑**：切除视频开头的任意时长
- 🎯 **无损质量**：保持原始分辨率、码率、编码格式
- 🖥️ **现代化界面**：Windows 11风格的友好界面
- 📊 **实时预览**：显示视频信息和剩余时长
- 🔄 **进度显示**：实时显示处理进度
- ⚡ **多格式支持**：支持MP4、AVI、MKV、MOV、FLV、WMV、WebM等常见格式

## 系统要求

- 操作系统：Windows 10/11
- Python 3.8+
- FFmpeg（用于视频处理）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd VideoTrimmer
```

或直接下载并解压到任意目录。

### 2. 安装Python依赖

打开命令提示符（CMD）或PowerShell，进入项目目录，运行：

```bash
pip install -r requirements.txt
```

### 3. 安装FFmpeg

#### 方法一：使用预编译版本（推荐）

1. 访问 [FFmpeg官网](https://ffmpeg.org/download.html) 或 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. 下载Windows版本的FFmpeg
3. 解压下载的压缩包
4. 将 `ffmpeg.exe` 复制到 `VideoTrimmer` 项目根目录下

#### 方法二：添加到系统PATH（可选）

如果你想将FFmpeg添加到系统PATH，使其在任何地方都可用：

1. 解压FFmpeg到某个目录，例如 `C:\ffmpeg`
2. 将该目录添加到系统环境变量PATH中
3. 重启命令提示符

### 4. 运行程序

在项目目录下运行：

```bash
python main.py
```

## 使用方法

### 基本操作流程

1. **选择视频**：点击"选择视频"按钮选择要处理的视频文件
2. **查看信息**：程序会自动显示视频的时长、分辨率、码率等信息
3. **设置时间**：在"移除开头"输入框中输入要移除的时间（秒）
4. **确认输出**：程序会自动生成输出文件路径，可点击"打开目录"查看保存位置
5. **开始剪辑**：点击"开始剪辑"按钮开始处理
6. **等待完成**：程序会显示处理进度，完成后会提示成功

## GitHub 自动打包

仓库已经可以通过 GitHub Actions 自动打包 Windows `exe`：

1. 推送代码到 `main` 分支，或在 GitHub 的 `Actions` 页面手动运行 `Build Windows EXE`
2. 工作流会在 `windows-latest` 上安装 Python 依赖、下载 FFmpeg，并执行 `PyInstaller`
3. 打包完成后，可在对应工作流页面下载 `VideoTrimmer-windows-exe` artifact

当前自动打包使用的是 [VideoTrimmer.spec](VideoTrimmer.spec)，产物文件名为 `dist/VideoTrimmer.exe`

### 注意事项

- 移除时间不能大于等于视频总时长
- 原始视频不会被修改，新文件会保存到指定位置
- 处理时间取决于视频大小和计算机性能

## 技术细节

### 工作原理

程序使用FFmpeg的 `-ss` 参数指定开始时间，并通过 `-c:v copy -c:a copy` 参数直接复制音视频流，而不重新编码。

这样做的好处：
- **速度快**：不需要重新编码，处理速度很快
- **质量无损**：保持原始分辨率、码率、清晰度
- **格式兼容**：保留原始编码格式

### 命令示例

```bash
ffmpeg -i input.mp4 -ss 10 -c:v copy -c:a copy -y output.mp4
```

这个命令会：
- 从输入视频第10秒开始
- 直接复制视频流（`-c:v copy`）
- 直接复制音频流（`-c:a copy`）
- 输出到新文件

## 文件结构

```
VideoTrimmer/
├── main.py              # 主程序入口
├── video_trimmer.py     # 视频处理核心模块
├── requirements.txt     # Python依赖
├── README.md           # 说明文档
└── ui/                 # UI模块
    ├── __init__.py
    └── main_window.py  # 主窗口UI
```

## 常见问题

### Q: 提示"未检测到FFmpeg"怎么办？

A: 确保FFmpeg已正确安装：
1. 检查 `ffmpeg.exe` 是否在项目根目录
2. 或检查FFmpeg是否已添加到系统PATH
3. 重新运行程序

### Q: 处理后的视频文件在哪里？

A: 默认保存在原视频同目录下，文件名后添加 `_trimmed`，例如：
- 原文件：`video.mp4`
- 输出文件：`video_trimmed.mp4`

### Q: 支持哪些视频格式？

A: 支持FFmpeg支持的所有格式，包括：
- MP4, AVI, MKV, MOV, FLV, WMV, WebM等

### Q: 处理速度很慢怎么办？

A: 本工具使用流复制，速度应该很快。如果慢可能是：
1. 硬盘读写速度慢（建议使用SSD）
2. 视频文件太大
3. 计算机性能较低

## 许可证

本项目仅供学习和个人使用。

## 更新日志

### v1.0.0 (2026-03-31)
- 初始版本发布
- 支持切除视频开头指定时间
- Windows 11风格界面
- 保持原始视频质量
