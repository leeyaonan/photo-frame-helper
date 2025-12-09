import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PhotoFrameHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("照片相框助手")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.photo_files = []
        self.selected_params = []
        self.frame_color = "black"
        self.frame_width = 20
        self.output_dir = ""
        
        # 创建GUI布局
        self.create_widgets()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 1. 照片文件选择
        ttk.Label(main_frame, text="照片文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.photo_listbox = tk.Listbox(main_frame, height=5, selectmode=tk.MULTIPLE)
        self.photo_listbox.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(main_frame, text="选择照片", command=self.select_photos).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(main_frame, text="清除选择", command=self.clear_photos).grid(row=0, column=3, padx=5, pady=5)
        
        # 2. 相框设置
        ttk.Label(main_frame, text="相框设置:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # 相框模板
        ttk.Label(main_frame, text="模板:").grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        self.frame_color_var = tk.StringVar(value="黑色底边")
        color_combo = ttk.Combobox(main_frame, textvariable=self.frame_color_var, values=["黑色底边", "白色底边", "红色", "蓝色", "绿色"], state='readonly')
        color_combo.grid(row=1, column=1, sticky=tk.W, padx=(50, 5))
        
        # 相框宽度
        ttk.Label(main_frame, text="宽度:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.frame_width_var = tk.IntVar(value=20)
        width_spin = ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.frame_width_var)
        width_spin.grid(row=1, column=2, sticky=tk.E, padx=5)
        
        # 3. EXIF参数选择
        ttk.Label(main_frame, text="EXIF参数选择:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 创建滚动框架
        exif_frame = ttk.LabelFrame(main_frame, text="可选择的EXIF参数")
        exif_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        exif_scrollbar = ttk.Scrollbar(exif_frame)
        exif_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.exif_listbox = tk.Listbox(exif_frame, height=8, selectmode=tk.MULTIPLE, yscrollcommand=exif_scrollbar.set)
        self.exif_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        exif_scrollbar.config(command=self.exif_listbox.yview)
        
        # 填充常见EXIF参数
        common_exif = [
            "拍摄时间", "相机型号", "镜头型号", "光圈", "快门速度", 
            "ISO", "焦距", "曝光补偿", "闪光灯", "测光模式"
        ]
        for param in common_exif:
            self.exif_listbox.insert(tk.END, param)
        
        # 4. 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.select_output_dir).grid(row=3, column=2, padx=5, pady=5)
        
        # 5. 预览区域
        ttk.Label(main_frame, text="预览:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.preview_canvas = tk.Canvas(main_frame, width=300, height=200, bg="lightgray")
        self.preview_canvas.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 6. 处理按钮
        ttk.Button(main_frame, text="批量处理", command=self.batch_process).grid(row=5, column=2, sticky=tk.E, pady=10)
    
    def select_photos(self):
        """选择照片文件"""
        files = filedialog.askopenfilenames(
            title="选择照片文件",
            filetypes=[("JPG文件", "*.jpg"), ("JPEG文件", "*.jpeg")]
        )
        
        # 清空当前列表
        self.photo_listbox.delete(0, tk.END)
        self.photo_files = list(files)
        
        # 添加到列表框
        for file in self.photo_files:
            self.photo_listbox.insert(tk.END, os.path.basename(file))
    
    def clear_photos(self):
        """清除选择的照片"""
        self.photo_listbox.delete(0, tk.END)
        self.photo_files = []
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def batch_process(self):
        """批量处理图片"""
        if not self.photo_files:
            messagebox.showwarning("警告", "请先选择照片文件")
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "请先选择输出目录")
            return
        
        # 获取选中的参数
        selected_indices = self.exif_listbox.curselection()
        selected_params = [self.exif_listbox.get(i) for i in selected_indices]
        
        messagebox.showinfo("信息", f"批量处理功能需要Pillow库\n\n已选择 {len(self.photo_files)} 张照片\n相框模板: {self.frame_color_var.get()}\n相框宽度: {self.frame_width_var.get()} 像素\n选择的EXIF参数: {', '.join(selected_params) if selected_params else '无'}\n输出目录: {output_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFrameHelper(root)
    root.mainloop()
