import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ExifTags, ImageTk
import glob
from entity.photo import Photo
from template.template_context import get_template_context
from template import FrameTemplate

class PhotoFrameHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("照片相框助手")
        self.root.geometry("800x600")  # 增加窗口高度以容纳预览区域
        
        # 初始化变量
        self.photo_files = []
        self.selected_params = []
        self.frame_color = "black"
        self.frame_width = 20
        self.output_dir = ""
        self.processed_files = []  # 保存处理成功的照片路径
        
        # 输出目录设置变量
        self.output_mode = tk.StringVar(value="指定目录")  # 输出模式：指定目录、原始照片所在文件夹
        self.subfolder_var = tk.StringVar(value="output")  # 子文件夹名称
        self.use_subfolder = tk.BooleanVar(value=False)  # 是否使用子文件夹
        
        # 初始化模板上下文管理器
        self.template_context = get_template_context()
        # 获取所有模板名称
        self.available_templates = self.template_context.get_all_template_names()
        # 默认模板
        self.default_template = self.template_context.get_default_template()
        
        # 创建样式
        style = ttk.Style()
        style.configure("Process.TButton", 
                       font=(".AppleSystemUIFont", 12, "bold"),
                       foreground="black",
                       background="lightblue",
                       padding=10)
        style.map("Process.TButton",
                 background=[("active", "#4a90e2")],
                 foreground=[("active", "white")])
        
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
        main_frame.rowconfigure(4, weight=1)  # 处理结果区域使用第4行并设置权重
        
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
        # 使用从模板上下文获取的模板名称列表
        self.template_var = tk.StringVar(value=self.available_templates[0] if self.available_templates else "")
        template_combo = ttk.Combobox(main_frame, textvariable=self.template_var, values=self.available_templates, state='readonly')
        template_combo.grid(row=1, column=1, sticky=tk.W, padx=(50, 5))
        
        # 3. 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 输出方式下拉框
        output_mode_frame = ttk.Frame(main_frame)
        output_mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        output_mode_frame.columnconfigure(0, weight=1)
        output_mode_frame.columnconfigure(1, weight=2)
        
        self.output_mode_combo = ttk.Combobox(output_mode_frame, textvariable=self.output_mode, 
                                              values=["指定目录", "原始照片所在的文件夹"], state='readonly', width=15)
        self.output_mode_combo.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.output_mode_combo.bind("<<ComboboxSelected>>", self.on_output_mode_change)
        
        # 指定目录输入框和按钮
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(output_mode_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.output_dir_button = ttk.Button(main_frame, text="选择目录", command=self.select_output_dir)
        self.output_dir_button.grid(row=2, column=2, padx=5, pady=5)
        
        # 子文件夹设置
        self.subfolder_frame = ttk.Frame(main_frame)
        self.subfolder_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.use_subfolder_check = ttk.Checkbutton(self.subfolder_frame, text="存储到子文件夹:", variable=self.use_subfolder)
        self.use_subfolder_check.grid(row=0, column=0, sticky=tk.W, padx=(5, 5))
        
        self.subfolder_entry = ttk.Entry(self.subfolder_frame, textvariable=self.subfolder_var, width=30)
        self.subfolder_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 初始化时根据输出模式显示/隐藏控件
        self.on_output_mode_change(None)
        
        # 4. 处理结果和预览区域
        ttk.Label(main_frame, text="处理结果:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 创建左右分栏框架
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=4, column=1, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置分栏框架的行列权重
        result_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(1, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 左边：处理结果列表
        self.processed_listbox = tk.Listbox(result_frame, height=15, selectmode=tk.SINGLE)
        self.processed_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.processed_listbox.yview)
        scrollbar.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E), padx=(0, 5))
        self.processed_listbox.config(yscrollcommand=scrollbar.set)
        
        # 添加双击事件
        self.processed_listbox.bind('<Double-Button-1>', self.on_processed_item_double_click)
        
        # 添加点击事件，用于实时预览
        self.processed_listbox.bind('<<ListboxSelect>>', self.on_processed_item_select)
        
        # 右边：实时预览区域
        preview_label = ttk.Label(result_frame, text="预览:")
        preview_label.grid(row=0, column=1, sticky=tk.N, padx=5)
        
        self.preview_canvas = tk.Canvas(result_frame, bg="lightgray")
        self.preview_canvas.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # 初始化预览画布的尺寸
        self.preview_canvas.config(width=350, height=350)
        
        # 5. 处理按钮
        # 创建一个单独的框架来放置处理按钮，确保它在底部可见
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20)
        button_frame.columnconfigure(0, weight=1)  # 让按钮居中
        
        # 创建一个美观的按钮
        self.process_button = tk.Button(button_frame, text="批量处理", command=self.batch_process,
                                       font=(".AppleSystemUIFont", 12, "bold"),
                                       bg="#4CAF50", fg="black",  # 将字体颜色改为黑色
                                       width=12, height=1,
                                       relief=tk.RAISED, bd=2)
        self.process_button.grid(row=0, column=0, padx=20, pady=5)
    
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
    
    def on_output_mode_change(self, event):
        """输出模式变更事件处理"""
        if self.output_mode.get() == "指定目录":
            # 显示指定目录输入框和按钮
            self.output_dir_entry.grid()
            self.output_dir_button.grid()
            # 隐藏子文件夹设置
            self.subfolder_frame.grid_remove()
        else:
            # 隐藏指定目录输入框和按钮
            self.output_dir_entry.grid_remove()
            self.output_dir_button.grid_remove()
            # 显示子文件夹设置
            self.subfolder_frame.grid()
    
    def decimal_to_fraction(self, decimal):
        """将小数转换为分数形式"""
        from fractions import Fraction
        # 转换为分数并简化
        fraction = Fraction(decimal).limit_denominator(1000)
        numerator, denominator = fraction.numerator, fraction.denominator
        
        if denominator == 1:
            # 整数形式
            return f"{numerator}s"
        elif numerator == 1:
            # 1/分母 形式
            return f"1/{denominator}s"
        else:
            # 分子/分母 形式
            return f"{numerator}/{denominator}s"

    def get_exif_data(self, image_path):
        """获取照片的EXIF数据"""
        exif_data = {}
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
        except Exception as e:
            print(f"读取EXIF数据失败: {e}")
        return exif_data
    
    def process_image(self, photo):
        """处理单张图片（使用策略模式）"""
        try:
            # 1. 处理照片方向（根据EXIF信息旋转图片）
            photo.fix_orientation()
            
            # 2. 获取用户选择的模板名称
            selected_template_name = self.template_var.get()
            
            # 3. 从模板上下文管理器中获取对应的模板实例
            template = self.template_context.get_template(selected_template_name)
            if not template:
                raise ValueError(f"找不到模板: {selected_template_name}")
            
            # 4. 使用模板实例的create_frame方法处理图片
            # 设置固定的EXIF参数列表
            selected_params = ["相机型号", "镜头型号", "焦距", "光圈", "快门速度", "ISO", "拍摄时间"]
            
            # 使用模板处理图片
            new_img = template.create_frame(
                photo=photo,
                frame_width=self.frame_width,
                frame_color=self.frame_color,
                selected_params=selected_params
            )
            
            return new_img
        except Exception as e:
            print(f"处理图片失败: {e}")
            return None
    
    def map_param_to_exif_tag(self, param):
        """将中文参数映射到EXIF标签"""
        mapping = {
            "拍摄时间": "DateTimeOriginal",
            "相机型号": "Model",
            "镜头型号": "LensModel",
            "光圈": "FNumber",
            "快门速度": "ExposureTime",
            "ISO": "ISOSpeedRatings",
            "焦距": "FocalLength",
            "曝光补偿": "ExposureBiasValue",
            "闪光灯": "Flash",
            "测光模式": "MeteringMode"
        }
        return mapping.get(param, param)
    
    def batch_process(self):
        """批量处理图片"""
        if not self.photo_files:
            messagebox.showwarning("警告", "请先选择照片文件")
            return
        
        # 检查输出目录设置
        output_mode = self.output_mode.get()
        if output_mode == "指定目录":
            output_dir = self.output_dir_var.get()
            if not output_dir:
                messagebox.showwarning("警告", "请先选择输出目录")
                return
        
        # 清空之前的处理结果
        self.processed_files = []
        self.processed_listbox.delete(0, tk.END)
        
        # 处理每张图片
        success_count = 0
        for file_path in self.photo_files:
            try:
                # 创建Photo对象封装照片信息
                photo = Photo(file_path)
                # 处理图片
                new_img = self.process_image(photo)
                if new_img:
                    # 确定输出路径
                    filename = os.path.basename(file_path)
                    new_filename = f"framed_{filename}"
                    
                    if self.output_mode.get() == "指定目录":
                        # 输出到指定目录
                        new_file_path = os.path.join(output_dir, new_filename)
                    else:
                        # 输出到原始照片所在文件夹
                        file_dir = os.path.dirname(file_path)
                        if self.use_subfolder.get() and self.subfolder_var.get():
                            # 使用子文件夹
                            subfolder_name = self.subfolder_var.get()
                            output_path = os.path.join(file_dir, subfolder_name)
                            # 创建子文件夹（如果不存在）
                            if not os.path.exists(output_path):
                                os.makedirs(output_path)
                            new_file_path = os.path.join(output_path, new_filename)
                        else:
                            # 直接输出到原始文件夹
                            new_file_path = os.path.join(file_dir, new_filename)
                    
                    try:
                        new_img.save(new_file_path, "JPEG")
                        success_count += 1
                        # 添加到处理成功列表
                        self.processed_files.append(new_file_path)
                        self.processed_listbox.insert(tk.END, new_filename)
                    except Exception as e:
                        messagebox.showerror("错误", f"保存图片失败: {e}")
            except Exception as e:
                messagebox.showerror("错误", f"处理图片 {file_path} 失败: {e}")
        
        messagebox.showinfo("完成", f"批量处理完成！成功处理 {success_count} 张图片")
    
    def on_processed_item_double_click(self, event):
        """处理双击事件，打开对应的图片"""
        selection = self.processed_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.processed_files):
                file_path = self.processed_files[index]
                try:
                    # 使用系统默认程序打开图片
                    os.system(f'open "{file_path}"')
                except Exception as e:
                    messagebox.showerror("错误", f"打开图片失败: {e}")
    
    def on_processed_item_select(self, event):
        """处理点击事件，实时预览选中的图片"""
        selection = self.processed_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.processed_files):
                file_path = self.processed_files[index]
                self.preview_image(file_path)
    
    def preview_image(self, image_path):
        """在预览画布上显示图片"""
        try:
            # 清空画布
            self.preview_canvas.delete("all")
            
            # 打开图片
            image = Image.open(image_path)
            
            # 获取画布尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 调整图片大小以适应画布，保持比例
            image_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height
            
            if image_ratio > canvas_ratio:
                # 图片更宽，按宽度缩放
                new_width = canvas_width
                new_height = int(new_width / image_ratio)
            else:
                # 图片更高，按高度缩放
                new_height = canvas_height
                new_width = int(new_height * image_ratio)
            
            # 缩放图片
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 将PIL图片转换为tkinter兼容的格式
            tk_image = ImageTk.PhotoImage(resized_image)
            
            # 保存图片引用，防止被垃圾回收
            self.preview_image_ref = tk_image
            
            # 计算居中位置
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # 在画布上显示图片
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=tk_image)
            
        except Exception as e:
            messagebox.showerror("预览错误", f"无法预览图片: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFrameHelper(root)
    root.mainloop()
