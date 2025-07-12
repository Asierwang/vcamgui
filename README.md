# 虚拟摄像头控制面板


## 功能特性
- ✔️ 实时虚拟摄像头输出
- ✔️ 支持多种图片格式（JPG/PNG/BMP/GIF）
- ✔️ 可调分辨率（640x480 至 1920x1080）
- ✔️ 动态帧率控制（1-60 FPS）
- ✔️ OBS集成检测功能

## 安装要求
- Python 3.8+
- Windows 10/11
- OBS Studio 26+

# 安装依赖
pip install -r requirements.txt

# 启动程序
python vcamgui/virtual_camera_gui.py
```

## 功能使用指南
1. 启动程序后点击【选择图片】按钮
2. 调整分辨率和帧率设置
3. 点击【启动虚拟摄像头】开始推流
4. 在视频会议软件中选择"Virtual Camera"设备

## 依赖项
```requirements.txt
pyvirtualcam==0.6.0
opencv-python==4.5.5.64
Pillow==9.0.1
```

## 常见问题
Q: 无法检测到虚拟摄像头设备
A: 请确保已安装OBS Studio并启用虚拟摄像头功能

## 许可证
MIT License