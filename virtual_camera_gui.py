import sys
import os
import cv2
import numpy as np
import pyvirtualcam
import threading
import time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class VirtualCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("虚拟摄像头控制面板")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 创建样式
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        
        # 状态变量
        self.is_running = False
        self.camera_thread = None
        self.stop_event = threading.Event()
        self.current_image = None
        self.cam = None
        
        # 创建UI
        self.create_widgets()
        
        # 初始状态
        self.update_ui_state()
        
        # 检查OBS是否安装
        self.check_obs_installed()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="虚拟摄像头控制面板", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # 创建左右面板
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 左侧面板 - 图像选择
        image_frame = ttk.LabelFrame(left_panel, text="选择图像", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.image_preview = tk.Label(image_frame, bg='white', relief=tk.SUNKEN)
        self.image_preview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.select_btn = ttk.Button(
            image_frame, 
            text="选择图片...", 
            command=self.select_image,
            width=15
        )
        self.select_btn.pack(pady=5)
        
        # 右侧面板 - 控制面板
        control_frame = ttk.LabelFrame(right_panel, text="摄像头控制", padding=10)
        control_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 分辨率设置
        res_frame = ttk.Frame(control_frame)
        res_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(res_frame, text="分辨率:").pack(side=tk.LEFT, padx=5)
        
        self.res_var = tk.StringVar(value="640x480")
        resolutions = ["640x480", "480x640", "600x600", "1024x768", "1280x720", "1920x1080"]
        self.res_combo = ttk.Combobox(
            res_frame, 
            textvariable=self.res_var, 
            values=resolutions,
            state="readonly",
            width=12
        )
        self.res_combo.pack(side=tk.LEFT, padx=5)
        
        # 帧率设置
        fps_frame = ttk.Frame(control_frame)
        fps_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(fps_frame, text="帧率 (FPS):").pack(side=tk.LEFT, padx=5)
        
        self.fps_var = tk.StringVar(value="30")
        self.fps_slider = ttk.Scale(
            fps_frame, 
            from_=1, 
            to=60, 
            orient=tk.HORIZONTAL,
            variable=self.fps_var,
            length=150
        )
        self.fps_slider.pack(side=tk.LEFT, padx=5)
        
        self.fps_label = ttk.Label(fps_frame, text="30")
        self.fps_label.pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            btn_frame, 
            text="启动虚拟摄像头", 
            command=self.start_camera,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame, 
            text="停止", 
            command=self.stop_camera,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪: 请选择一张图片")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=3
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定事件
        self.fps_var.trace_add("write", self.update_fps_label)
    
    def update_fps_label(self, *args):
        """更新帧率标签显示"""
        try:
            fps = int(float(self.fps_var.get()))
            self.fps_label.config(text=str(fps))
        except ValueError:
            pass
    
    def select_image(self):
        """选择图片文件并显示预览"""
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=filetypes
        )
        
        if file_path:
            try:
                # 加载图片
                img = Image.open(file_path)
                img.thumbnail((400, 400))  # 调整预览大小
                
                # 保存原始图片路径
                self.image_path = file_path
                
                # 更新预览
                photo = ImageTk.PhotoImage(img)
                self.image_preview.config(image=photo)
                self.image_preview.image = photo  # 保持引用
                
                # 更新状态
                self.status_var.set(f"已选择: {os.path.basename(file_path)}")
                self.update_ui_state()
                
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {e}")
    
    def start_camera(self):
        """启动虚拟摄像头"""
        if not hasattr(self, 'image_path') or not os.path.exists(self.image_path):
            messagebox.showwarning("警告", "请先选择一张图片")
            return
        
        try:
            # 解析分辨率
            width, height = map(int, self.res_var.get().split('x'))
            
            # 获取帧率
            fps = int(float(self.fps_var.get()))
            
            # 加载原始图片
            img = cv2.imread(self.image_path)
            if img is None:
                raise ValueError(f"无法加载图片: {self.image_path}")
            
            # 调整图片到指定分辨率
            self.camera_img = cv2.resize(img, (width, height))
            
            # 更新UI状态
            self.is_running = True
            self.stop_event.clear()
            self.update_ui_state()
            self.status_var.set(f"运行中: 输出到虚拟摄像头 ({width}x{height} @ {fps}fps)")
            
            # 启动摄像头线程
            self.camera_thread = threading.Thread(
                target=self.run_camera, 
                args=(width, height, fps),
                daemon=True
            )
            self.camera_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动虚拟摄像头失败: {e}")
            self.is_running = False
            self.update_ui_state()
    
    def run_camera(self, width, height, fps):
        """在单独线程中运行虚拟摄像头"""
        try:
            with pyvirtualcam.Camera(width, height, fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
                self.cam = cam
                print(f"虚拟摄像头已激活: {cam.device}")
                
                while not self.stop_event.is_set():
                    # 发送图片到虚拟摄像头
                    cam.send(self.camera_img)
                    
                    # 按帧率等待
                    time.sleep(1 / fps)
        
        except Exception as e:
            # 在主线程中显示错误
            self.root.after(0, lambda: messagebox.showerror("摄像头错误", str(e)))
            self.is_running = False
            self.root.after(0, self.update_ui_state)
    
    def stop_camera(self):
        """停止虚拟摄像头"""
        self.stop_event.set()
        self.is_running = False
        
        # 等待线程结束
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=2.0)
        
        self.update_ui_state()
        self.status_var.set("已停止")
    
    def update_ui_state(self):
        """根据当前状态更新UI控件状态"""
        # 更新按钮状态
        self.start_btn.config(state=tk.NORMAL if not self.is_running and hasattr(self, 'image_path') else tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL if self.is_running else tk.DISABLED)
        self.select_btn.config(state=tk.NORMAL if not self.is_running else tk.DISABLED)
        
        # 更新其他控件状态
        self.res_combo.config(state=tk.NORMAL if not self.is_running else tk.DISABLED)
        self.fps_slider.config(state=tk.NORMAL if not self.is_running else tk.DISABLED)
    
    def check_obs_installed(self):
        """检查OBS是否安装"""
        # 在Windows上，我们检查OBS的常见安装路径
        obs_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "obs-studio"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "obs-studio")
        ]
        
        installed = any(os.path.exists(path) for path in obs_paths)
        
        if not installed:
            self.status_var.set("警告: 未检测到OBS安装 - 虚拟摄像头可能无法工作")
    
    def on_close(self):
        """关闭窗口时的处理"""
        if self.is_running:
            self.stop_camera()
        self.root.destroy()

if __name__ == "__main__":
    # 检查依赖
    try:
        import pyvirtualcam
        import cv2
        import PIL
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请安装以下依赖:")
        print("pip install opencv-python pyvirtualcam pillow")
        sys.exit(1)
    
    root = tk.Tk()
    app = VirtualCameraApp(root)
    root.mainloop()