import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ExifTags, ImageTk
import glob
from entity.photo import Photo

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
        main_frame.rowconfigure(3, weight=1)  # 处理结果区域使用第3行并设置权重
        
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
        color_combo = ttk.Combobox(main_frame, textvariable=self.frame_color_var, values=["黑色底边", "白色底边"], state='readonly')
        color_combo.grid(row=1, column=1, sticky=tk.W, padx=(50, 5))
        
        # 3. 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="选择目录", command=self.select_output_dir).grid(row=2, column=2, padx=5, pady=5)
        
        # 4. 处理结果和预览区域
        ttk.Label(main_frame, text="处理结果:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # 创建左右分栏框架
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        """处理单张图片"""
        try:
            # 1. 处理照片方向（根据EXIF信息旋转图片）
            photo.fix_orientation()
            img = photo.img
            
            # 2. 计算新尺寸（在照片底部添加信息横条）
            frame_height = int(img.height * 0.08)  # 恢复信息横条高度为照片高度的8%
            new_width = img.width
            new_height = img.height + frame_height
            
            # 创建新图片（包含底部横条）
            # 使用用户选择的模板作为背景色，并进行中英文映射
            color_mapping = {"黑色底边": "black", "白色底边": "white"}
            background_color = color_mapping.get(self.frame_color_var.get(), "black")
            new_img = Image.new("RGB", (new_width, new_height), background_color)
            new_img.paste(img, (0, 0))  # 将照片粘贴在顶部
            
            # 4. 设置固定的EXIF参数列表
            selected_params = ["相机型号", "镜头型号", "焦距", "光圈", "快门速度", "ISO", "拍摄时间"]
            
            # 5. 添加EXIF信息
            if selected_params:
                draw = ImageDraw.Draw(new_img)
                
                # 按照照片高度的1%设置字体大小
                font_size = int(img.height * 0.01)  # 字体大小改为照片高度的1%
                # 保持最小字体限制以确保可读性
                min_font_size = 12  # 调整最小字体大小
                font_size = max(font_size, min_font_size)
                
                # 使用默认字体简化处理
                try:
                    # 使用更通用的字体
                    font = ImageFont.truetype("Arial", font_size)
                except:
                    # 如果没有Arial，使用默认字体
                    font = ImageFont.load_default()
                
                # 为左下角文本框创建不同大小的字体
                # 相机型号：照片高度的3%
                model_font_size = int(img.height * 0.03)
                min_model_font_size = 16  # 相机型号最小字体
                model_font_size = max(model_font_size, min_model_font_size)
                
                # 镜头型号：照片高度的2%
                lens_font_size = int(img.height * 0.02)
                min_lens_font_size = 12  # 镜头型号最小字体
                lens_font_size = max(lens_font_size, min_lens_font_size)
                
                # 尝试加载不同大小的字体
                try:
                    model_font = ImageFont.truetype("Arial", model_font_size)
                    lens_font = ImageFont.truetype("Arial", lens_font_size)
                    
                    # 为右下角第一行创建字体：照片高度的2%，加粗
                    right_first_line_font_size = int(img.height * 0.02)
                    # 直接使用Arial Bold字体，根据测试结果这是最可靠的方式
                    right_first_line_font = ImageFont.truetype("Arial Bold", right_first_line_font_size)
                    
                    # 为右下角第二行创建字体：照片高度的2%，不加粗
                    right_second_line_font_size = int(img.height * 0.02)
                    right_second_line_font = ImageFont.truetype("Arial", right_second_line_font_size)
                except Exception as e:
                    # 如果加载失败，使用默认字体并调整大小
                    print(f"字体加载失败: {e}")
                    model_font = ImageFont.load_default()
                    lens_font = ImageFont.load_default()
                    right_first_line_font = ImageFont.load_default()
                    right_second_line_font = ImageFont.load_default()
                
                # 收集并分组EXIF信息
                left_texts = []  # 左下角：相机型号、镜头型号
                right_first_line = []  # 右下角第一行：焦距、光圈、快门、ISO
                right_second_line = ""  # 右下角第二行：拍摄时间
                
                for param in selected_params:
                    # 将中文参数映射到EXIF标签
                    exif_tag = self.map_param_to_exif_tag(param)
                    if exif_tag in photo.exif_data:
                        value = photo.exif_data[exif_tag]
                        # 根据参数类型进行格式化
                        if param == "相机型号" or param == "镜头型号":
                            # 左下角文本框内容
                            left_texts.append(f"{value}")
                        elif param == "光圈" and value is not None:
                            # 光圈值增加F前缀
                            right_first_line.append(f"F{value}")
                        elif param == "快门速度" and value is not None:
                            # 快门速度折算成s
                            if isinstance(value, tuple):
                                # 分数形式 (numerator, denominator)
                                numerator, denominator = value
                                if denominator == 1:
                                    # 整数s
                                    right_first_line.append(f"{numerator}s")
                                elif numerator == 1:
                                    # 1/分母 形式
                                    right_first_line.append(f"1/{denominator}s")
                                else:
                                    # 分子/分母 形式
                                    right_first_line.append(f"{numerator}/{denominator}s")
                            else:
                                try:
                                    # 尝试将数值转换为浮点数
                                    decimal_value = float(value)
                                    # 使用小数转分数函数处理
                                    right_first_line.append(self.decimal_to_fraction(decimal_value))
                                except (ValueError, TypeError):
                                    # 如果转换失败，直接显示原始值
                                    right_first_line.append(f"{value}s")
                        elif param == "焦距" and value is not None:
                            # 焦距增加mm单位
                            if isinstance(value, tuple):
                                # 分数形式 (numerator, denominator)
                                numerator, denominator = value
                                focal_length = numerator / denominator
                                right_first_line.append(f"{focal_length:.1f}mm")
                            else:
                                # 直接数值
                                right_first_line.append(f"{value}mm")
                        elif param == "ISO" and value is not None:
                            # ISO保持简洁格式
                            right_first_line.append(f"ISO{value}")
                        elif param == "拍摄时间" and value is not None:
                            # 拍摄时间保持原有格式
                            right_second_line = f"{value}"
                        elif param == "曝光补偿" and value is not None:
                            # 曝光补偿增加EV单位
                            right_first_line.append(f"{value}EV")
                        else:
                            # 其他参数保持原有格式
                            right_first_line.append(f"{value}")
                
                # 根据相框颜色选择合适的字体颜色
                text_color = "black" if background_color == "white" else "white"
                
                # 检查相机品牌并加载对应的logo
                camera_brand = None
                model = photo.exif_data.get("Model", "").lower()
                
                # 获取logo文件夹中的所有品牌logo文件
                logo_files = [f for f in os.listdir("logo") if f.endswith(".png")]
                
                # 从文件名中提取品牌名称并检查是否匹配相机型号
                for logo_file in logo_files:
                    # 提取品牌名称（去掉"_Logo.png"后缀）
                    brand_name = logo_file.replace("_Logo.png", "").lower()
                    # 检查相机型号中是否包含品牌名称
                    if brand_name in model:
                        camera_brand = brand_name
                        break
                
                # 设置文字框宽度根据文本内容自适应，但最大不超过照片宽度的50%
                max_allowed_width = int(new_width * 0.5)
                
                # 计算第一行文本的宽度
                first_line_text = "  ".join(right_first_line)
                first_line_width = right_first_line_font.getbbox(first_line_text)[2] if right_first_line else 0
                
                # 计算第二行文本的宽度
                second_line_width = right_second_line_font.getbbox(right_second_line)[2] if right_second_line else 0
                
                # 取两行中最宽的作为文本框宽度
                text_box_width = max(first_line_width, second_line_width)
                
                # 确保文本框宽度不超过最大允许宽度，并添加一些边距
                text_box_width = min(text_box_width + 20, max_allowed_width)
                
                # 根据照片构图类型设置不同的边距
                if img.height > img.width or img.height == img.width:
                    # 竖版或正方形构图：边距为照片宽度的1%
                    margin = int(new_width * 0.01)
                else:
                    # 横版构图：边距为照片宽度的2%
                    margin = int(new_width * 0.02)
                
                # 1. 处理右下角文本框（焦距、光圈、快门、ISO、拍摄时间）
                # 设置文字框右对齐的起始位置
                text_box_x = new_width - text_box_width - margin
                
                # 调整文本框高度为整个横条的50%并垂直居中
                text_box_height = int(frame_height * 0.5)
                text_box_y = img.height + int((frame_height - text_box_height) / 2)
                
                # 如果检测到支持的相机品牌，加载并绘制对应的logo
                logo_width = 0
                if camera_brand:
                    try:
                        # 加载对应的相机品牌logo (PNG格式)
                        # 将品牌名称转换为标题格式（首字母大写）以匹配文件名
                        brand_title = camera_brand.title()
                        logo_path = os.path.join("logo", f"{brand_title}_Logo.png")
                        if os.path.exists(logo_path):
                            logo = Image.open(logo_path)
                            # 调整logo大小，高度与文本框高度匹配
                            logo_height = int(frame_height * 0.8)  # logo高度为信息横条高度的80%
                            logo_width = int(logo.width * (logo_height / logo.height))
                            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                            
                            # 按照片宽度的1%计算间距
                            spacing = int(new_width * 0.01)
                            
                            # 从右往左计算各元素位置：文本框 -> 间距 -> 竖线 -> 间距 -> logo
                            text_box_x = new_width - text_box_width - margin
                            
                            # 竖线位置：文本框左侧 + 间距
                            line_x = text_box_x - spacing
                            
                            # logo位置：竖线左侧 + 间距
                            logo_x = line_x - spacing - logo_width
                            
                            # 垂直居中位置
                            logo_y = img.height + int((frame_height - logo_height) / 2)
                            
                            # 将logo转换为RGBA（如果不是的话）
                            if logo.mode != 'RGBA':
                                logo_rgba = logo.convert("RGBA")
                            else:
                                logo_rgba = logo
                            
                            # 绘制logo
                            new_img.paste(logo_rgba, (logo_x, logo_y), logo_rgba)
                            
                            # 在logo和文本框之间添加竖线，颜色根据背景色决定
                            # 调整竖线UI：高度为整个横条的50%，宽度加粗
                            line_height = int(frame_height * 0.5)
                            line_width = 3  # 加粗竖线
                            line_color = "white" if background_color == "black" else "black"
                            
                            # 计算竖线垂直位置（居中）
                            line_center_y = img.height + frame_height // 2
                            line_y_top = line_center_y - line_height // 2
                            line_y_bottom = line_center_y + line_height // 2
                            
                            # 绘制竖线
                            draw.line([(line_x, line_y_top), (line_x, line_y_bottom)], fill=line_color, width=line_width)
                    except Exception as e:
                        print(f"绘制{camera_brand} logo失败: {e}")
                
                # 绘制右下角文本框的EXIF信息，内容右对齐
                y_offset = text_box_y
                
                # 第一行：焦距、光圈、快门、ISO，用空格分隔
                first_line_text = "  ".join(right_first_line)
                # 确保第一行文本不超过文字框宽度
                if right_first_line_font.getbbox(first_line_text)[2] <= text_box_width:
                    # 计算右对齐的x坐标
                    text_width = right_first_line_font.getbbox(first_line_text)[2]
                    right_aligned_x = text_box_x + text_box_width - text_width
                    draw.text((right_aligned_x, y_offset), first_line_text, fill=text_color, font=right_first_line_font)
                else:
                    # 如果文本太长，尝试截断
                    max_chars = int((text_box_width / right_first_line_font.getbbox("A")[2]) * 0.8)  # 保守估计可容纳的字符数
                    truncated_text = first_line_text[:max_chars] + "..."
                    # 计算截断后文本的右对齐x坐标
                    truncated_width = right_first_line_font.getbbox(truncated_text)[2]
                    right_aligned_x = text_box_x + text_box_width - truncated_width
                    draw.text((right_aligned_x, y_offset), truncated_text, fill=text_color, font=right_first_line_font)
                
                # 下移到下一行
                y_offset += right_first_line_font_size + 5  # 行间距为5像素
                
                # 第二行：拍摄时间
                if right_second_line:
                    # 确保第二行文本不超过文字框宽度
                    if right_second_line_font.getbbox(right_second_line)[2] <= text_box_width:
                        # 计算右对齐的x坐标
                        text_width = right_second_line_font.getbbox(right_second_line)[2]
                        right_aligned_x = text_box_x + text_box_width - text_width
                        draw.text((right_aligned_x, y_offset), right_second_line, fill=text_color, font=right_second_line_font)
                    else:
                        # 如果文本太长，尝试截断
                        max_chars = int((text_box_width / right_second_line_font.getbbox("A")[2]) * 0.8)  # 保守估计可容纳的字符数
                        truncated_text = right_second_line[:max_chars] + "..."
                        # 计算截断后文本的右对齐x坐标
                        truncated_width = right_second_line_font.getbbox(truncated_text)[2]
                        right_aligned_x = text_box_x + text_box_width - truncated_width
                        draw.text((right_aligned_x, y_offset), truncated_text, fill=text_color, font=right_second_line_font)
                
                # 2. 处理左下角文本框（相机型号、镜头型号）
                # 设置文字框左对齐的起始位置
                left_box_x = margin  # 使用照片宽度1%的边距
                
                # 计算左下角文本框高度为横条的62.5%
                left_text_box_height = int(frame_height * 0.625)
                
                # 计算文本框的起始y坐标，使其垂直居中
                left_box_y = img.height + (frame_height - left_text_box_height) // 2
                
                # 绘制左下角文本框的EXIF信息，内容左对齐
                # 计算文本垂直居中的起始y偏移
                total_text_height = 0
                for i, text in enumerate(left_texts):
                    if i == 0:  # 相机型号
                        total_text_height += model_font_size
                    else:  # 镜头型号及其他
                        total_text_height += lens_font_size
                    # 加上行间距（除了最后一行）
                    if i < len(left_texts) - 1:
                        total_text_height += 5
                
                # 计算垂直居中的起始y_offset
                y_offset = left_box_y + (left_text_box_height - total_text_height) // 2
                
                # 根据文本内容选择不同的字体大小
                for i, text in enumerate(left_texts):
                    # 确保文本不超过文字框宽度
                    if i == 0:  # 相机型号
                        current_font = model_font
                        current_font_size = model_font_size
                    else:  # 镜头型号及其他
                        current_font = lens_font
                        current_font_size = lens_font_size
                    
                    # 检查文本是否超过文字框宽度
                    if current_font.getbbox(text)[2] <= text_box_width:
                        draw.text((left_box_x, y_offset), text, fill=text_color, font=current_font)
                    else:
                        # 如果文本太长，尝试截断
                        truncated_text = text[:20] + "..."
                        draw.text((left_box_x, y_offset), truncated_text, fill=text_color, font=current_font)
                    
                    # 下移到下一行
                    y_offset += current_font_size + 5  # 行间距为5像素
            
            return new_img
        except Exception as e:
            messagebox.showerror("错误", f"处理图片失败: {e}")
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
                    # 保存新图片
                    filename = os.path.basename(file_path)
                    new_filename = f"framed_{filename}"
                    new_file_path = os.path.join(output_dir, new_filename)
                    
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
