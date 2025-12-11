import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from template.frame_template import FrameTemplate
from entity.photo import Photo
from typing import Optional

class BlackBottomTemplate(FrameTemplate):
    @property
    def name(self):
        return "黑色底边"
    
    @property
    def description(self):
        return "在照片底部添加黑色信息横条，显示相机参数和拍摄信息"
    
    def create_frame(self, photo: Photo, frame_width: int = None, frame_color: str = None, **kwargs) -> Image.Image:
        try:
            # 获取已经处理好方向的图片
            img = photo.img
            
            # 2. 计算新尺寸（在照片底部添加信息横条）
            frame_height = int(img.height * 0.08)  # 信息横条高度为照片高度的8%
            new_width = img.width
            new_height = img.height + frame_height
            
            # 创建新图片（包含底部横条）
            background_color = "black"
            new_img = Image.new("RGB", (new_width, new_height), background_color)
            new_img.paste(img, (0, 0))  # 将照片粘贴在顶部
            
            # 3. 设置固定的EXIF参数列表
            selected_params = ["相机型号", "镜头型号", "焦距", "光圈", "快门速度", "ISO", "拍摄时间"]
            
            # 4. 添加EXIF信息
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
                # 直接使用Arial Bold字体
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
                exif_tag = self._map_param_to_exif_tag(param)
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
                                right_first_line.append(self._decimal_to_fraction(decimal_value))
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
            text_color = "white"
            
            # 检查相机品牌并加载对应的logo
            camera_brand = self._detect_camera_brand(photo)
            
            # 设置文字框宽度根据文本内容自适应，但最大不超过照片宽度的50%
            max_allowed_width = int(new_width * 0.5)
            
            # 计算第一行文本的宽度
            first_line_text = "  ".join(right_first_line)
            try:
                if right_first_line:
                    # 使用更兼容的getsize()方法获取文本尺寸
                    first_line_width = right_first_line_font.getsize(first_line_text)[0]
                else:
                    first_line_width = 0
            except Exception as e:
                print(f"获取第一行文本宽度失败: {e}")
                first_line_width = 0
            
            # 计算第二行文本的宽度
            try:
                if right_second_line:
                    # 使用更兼容的getsize()方法获取文本尺寸
                    second_line_width = right_second_line_font.getsize(right_second_line)[0]
                else:
                    second_line_width = 0
            except Exception as e:
                print(f"获取第二行文本宽度失败: {e}")
                second_line_width = 0
            
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
                    logo = self.get_camera_logo(camera_brand, background_color)
                    
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
                    line_color = "white"
                    
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
            print(f"处理图片失败: {e}")
            raise
    
    def add_watermark(self, image: Image.Image, watermark_image: Image.Image, 
                     position: str = "bottom_right", opacity: float = 1.0, **kwargs) -> Image.Image:
        # 默认实现，可根据需要自定义
        try:
            # 简单的水印实现
            watermark = self.adjust_watermark_opacity(watermark_image, opacity)
            
            # 如果有缩放比例参数，调整水印大小
            if "scale" in kwargs:
                watermark = self.resize_watermark(watermark, scale=kwargs["scale"])
            
            # 获取水印位置
            watermark_position = self.get_watermark_position(
                image.size, 
                watermark.size, 
                position, 
                kwargs.get("margin", 20)
            )
            
            # 添加水印
            image.paste(watermark, watermark_position, watermark)
            return image
        except Exception as e:
            print(f"添加水印失败: {e}")
            return image
    
    def _map_param_to_exif_tag(self, param):
        """
        将中文参数映射到EXIF标签
        """
        param_mapping = {
            "相机型号": "Model",
            "镜头型号": "LensModel",
            "焦距": "FocalLength",
            "光圈": "FNumber",
            "快门速度": "ExposureTime",
            "ISO": "ISOSpeedRatings",
            "拍摄时间": "DateTimeOriginal",
            "曝光补偿": "ExposureBiasValue"
        }
        return param_mapping.get(param, param)
    
    def _decimal_to_fraction(self, decimal):
        """
        将小数转换为分数形式
        """
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
    
    def _detect_camera_brand(self, photo):
        """
        检测相机品牌
        """
        camera_brand = None
        model = photo.exif_data.get("Model", "").lower()
        
        # 获取logo文件夹中的所有品牌logo文件
        logo_files = [f for f in os.listdir(FrameTemplate.get_resource_path("logo")) if f.endswith(".png")]
        
        # 从文件名中提取品牌名称并检查是否匹配相机型号
        for logo_file in logo_files:
            # 提取品牌名称（去掉"_Logo.png"后缀）
            brand_name = logo_file.replace("_Logo.png", "").lower()
            # 检查相机型号中是否包含品牌名称
            if brand_name in model:
                camera_brand = brand_name
                break
        
        return camera_brand
    
    def get_camera_logo(self, camera_brand: str, background_color: str, **kwargs) -> Optional[Image.Image]:
        """
        获取相机品牌的logo图像，支持根据背景色自动调整logo样式
        
        Args:
            camera_brand: 相机品牌名称（如"sony", "canon", "nikon"等）
            background_color: 背景颜色，用于根据背景色调整logo样式
            **kwargs: 额外参数（如logo大小、透明度等）
            
        Returns:
            Optional[Image.Image]: 处理后的logo图像，如果不支持该品牌则返回None
        """
        try:
            # 首先尝试加载带_black后缀的logo文件
            black_logo_filename = f"{camera_brand}_Logo_black.png"
            black_logo_path = FrameTemplate.get_resource_path(os.path.join("logo", black_logo_filename))
            
            # 如果存在黑色logo文件，则使用它
            if os.path.exists(black_logo_path):
                logo_path = black_logo_path
                is_black_logo = True
            else:
                # 否则使用普通logo文件
                logo_filename = f"{camera_brand}_Logo.png"
                logo_path = FrameTemplate.get_resource_path(os.path.join("logo", logo_filename))
                is_black_logo = False
            
            # 检查logo文件是否存在
            if not os.path.exists(logo_path):
                print(f"相机品牌 {camera_brand} 的logo文件不存在: {logo_path}")
                return None
            
            # 加载logo图像
            logo = Image.open(logo_path)
            
            # 根据背景色调整logo颜色
            if background_color.lower() in ["black", "#000000", "#000"]:
                # 如果背景是黑色，且是黑色logo，则调整logo颜色
                logo = self.adjust_logo_color_for_background(logo, background_color, is_black_logo=is_black_logo)
            
            # 如果有大小参数，调整logo大小
            if "size" in kwargs:
                logo = self.resize_logo(logo, size=kwargs["size"])
            elif "scale" in kwargs:
                logo = self.resize_logo(logo, scale=kwargs["scale"])
            
            return logo
        except Exception as e:
            print(f"获取相机品牌 {camera_brand} 的logo失败: {e}")
            return None