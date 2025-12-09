from abc import ABC, abstractmethod
from PIL import Image
from entity.photo import Photo
from typing import Dict, Any, Optional, List, Tuple, Union


class FrameTemplate(ABC):
    """
    相框模板策略接口
    定义所有具体相框模板必须实现的方法
    策略模式的核心接口类
    """
    
    # 模板元数据常量
    VERSION = "1.0"
    AUTHOR = ""
    COMPATIBILITY = {"python": ">=3.8", "pillow": ">=9.0"}
    
    @abstractmethod
    def create_frame(self, photo: Photo, frame_width: int, frame_color: str, **kwargs) -> Image.Image:
        """
        创建相框的抽象方法
        
        Args:
            photo: Photo对象,包含照片的所有信息
            frame_width: 相框宽度（像素）
            frame_color: 相框颜色
            **kwargs: 模板特定的额外参数
            
        Returns:
            Image.Image: 添加相框后的图片对象
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        获取模板名称
        
        Returns:
            str: 模板名称
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        获取模板描述
        
        Returns:
            str: 模板描述
        """
        pass
    
    @property
    def version(self) -> str:
        """
        获取模板版本号
        
        Returns:
            str: 模板版本号
        """
        return self.VERSION
    
    @property
    def author(self) -> str:
        """
        获取模板作者
        
        Returns:
            str: 模板作者
        """
        return self.AUTHOR
    
    @property
    def compatibility(self) -> Dict[str, str]:
        """
        获取模板兼容性信息
        
        Returns:
            Dict[str, str]: 兼容性信息字典
        """
        return self.COMPATIBILITY
    
    def validate_frame_params(self, frame_width: int, frame_color: str, **kwargs) -> Tuple[bool, str]:
        """
        验证相框参数是否有效
        
        Args:
            frame_width: 相框宽度（像素）
            frame_color: 相框颜色
            **kwargs: 模板特定的额外参数
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 默认实现，检查基本参数
        if frame_width <= 0:
            return False, "相框宽度必须大于0"
        
        return True, ""
    
    def validate_photo(self, photo: Photo) -> Tuple[bool, str]:
        """
        验证照片是否适合该模板
        
        Args:
            photo: Photo对象
            
        Returns:
            Tuple[bool, str]: (是否适合, 错误信息)
        """
        # 默认实现，检查照片是否有效
        if not photo or not photo.img:
            return False, "无效的照片对象"
        
        if photo.width <= 0 or photo.height <= 0:
            return False, "照片尺寸无效"
        
        return True, ""
    
    def get_default_params(self) -> Dict[str, Any]:
        """
        获取模板的默认参数
        
        Returns:
            Dict[str, Any]: 默认参数字典
        """
        return {
            "frame_width": 20,
            "frame_color": "black"
        }
    
    def get_supported_params(self) -> List[str]:
        """
        获取模板支持的所有参数
        
        Returns:
            List[str]: 参数名称列表
        """
        return ["frame_width", "frame_color"]
    
    def get_param_description(self, param_name: str) -> Optional[str]:
        """
        获取参数的描述信息
        
        Args:
            param_name: 参数名称
            
        Returns:
            Optional[str]: 参数描述信息
        """
        param_descriptions = {
            "frame_width": "相框宽度（像素）",
            "frame_color": "相框颜色"
        }
        
        return param_descriptions.get(param_name)
    
    def generate_preview(self, preview_size: Tuple[int, int] = (200, 200)) -> Image.Image:
        """
        生成模板的预览图像（不需要实际照片）
        
        Args:
            preview_size: 预览图像的大小 (宽度, 高度)
            
        Returns:
            Image.Image: 预览图像
        """
        # 默认实现，生成一个简单的预览
        preview = Image.new("RGB", preview_size, color="white")
        draw = ImageDraw.Draw(preview)
        
        # 绘制一个简单的相框预览
        inner_width = preview_size[0] - 40
        inner_height = preview_size[1] - 40
        draw.rectangle([20, 20, 20 + inner_width, 20 + inner_height], outline="black", width=5)
        
        # 绘制模板名称
        try:
            font = ImageFont.load_default()
            draw.text((20, 5), self.name, fill="black", font=font)
        except Exception:
            pass
        
        return preview
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取模板的所有元数据
        
        Returns:
            Dict[str, Any]: 元数据字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "compatibility": self.compatibility,
            "supported_params": self.get_supported_params(),
            "default_params": self.get_default_params()
        }
    
    def before_create_frame(self, photo: Photo, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建相框前的钩子方法
        
        Args:
            photo: Photo对象
            params: 相框参数
            
        Returns:
            Dict[str, Any]: 更新后的参数
        """
        return params
    
    def after_create_frame(self, photo: Photo, framed_image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """
        创建相框后的钩子方法
        
        Args:
            photo: Photo对象
            framed_image: 创建好的相框图像
            params: 使用的参数
            
        Returns:
            Image.Image: 处理后的相框图像
        """
        return framed_image
    
    @abstractmethod
    def get_camera_logo(self, camera_brand: str, background_color: str, **kwargs) -> Optional[Image.Image]:
        """
        获取相机品牌的logo图像，支持根据背景色自动调整logo样式
        
        Args:
            camera_brand: 相机品牌名称（如"sony", "canon", "nikon"等）
            background_color: 背景颜色，用于根据背景色调整logo样式（如白色背景用黑色logo，黑色背景用白色logo）
            **kwargs: 额外参数（如logo大小、透明度等）
            
        Returns:
            Optional[Image.Image]: 处理后的logo图像，如果不支持该品牌则返回None
        """
        pass
    
    def get_supported_camera_brands(self) -> List[str]:
        """
        获取模板支持的相机品牌列表
        
        Returns:
            List[str]: 支持的相机品牌列表
        """
        # 默认实现，返回常见相机品牌
        return ["sony", "canon", "nikon", "fujifilm", "panasonic", "olympus"]
    
    def adjust_logo_color_for_background(self, logo: Image.Image, background_color: str, is_black_logo: bool = False) -> Image.Image:
        """
        根据背景颜色调整logo颜色（如黑白反转）
        
        Args:
            logo: 原始logo图像
            background_color: 背景颜色
            is_black_logo: 是否为黑色logo（文件名带_black后缀的logo）
            
        Returns:
            Image.Image: 调整后的logo图像
        """
        # 默认实现，简单的黑白反转逻辑
        # 可根据实际需求扩展为更复杂的颜色调整算法
        if not logo:
            return logo
            
        try:
            # 只有当logo是黑色logo（文件名带_black后缀）时才进行颜色调整
            if not is_black_logo:
                return logo
                
            # 检查背景是否为深色
            is_dark_background = self._is_dark_color(background_color)
            
            if is_dark_background:
                # 如果背景是深色，将logo转换为白色（简单实现）
                inverted_logo = Image.new(logo.mode, logo.size)
                for x in range(logo.width):
                    for y in range(logo.height):
                        pixel = logo.getpixel((x, y))
                        if isinstance(pixel, tuple):
                            # RGB/RGBA图像
                            if len(pixel) == 4:  # RGBA
                                r, g, b, a = pixel
                                if a > 0:  # 不透明像素
                                    inverted_logo.putpixel((x, y), (255 - r, 255 - g, 255 - b, a))
                                else:
                                    inverted_logo.putpixel((x, y), pixel)
                            else:  # RGB
                                r, g, b = pixel
                                inverted_logo.putpixel((x, y), (255 - r, 255 - g, 255 - b))
                        else:
                            # 灰度图像
                            inverted_logo.putpixel((x, y), 255 - pixel)
                return inverted_logo
            else:
                # 如果背景是浅色，将logo转换为黑色（简单实现）
                inverted_logo = Image.new(logo.mode, logo.size)
                for x in range(logo.width):
                    for y in range(logo.height):
                        pixel = logo.getpixel((x, y))
                        if isinstance(pixel, tuple):
                            # RGB/RGBA图像
                            if len(pixel) == 4:  # RGBA
                                r, g, b, a = pixel
                                if a > 0:  # 不透明像素
                                    inverted_logo.putpixel((x, y), (255 - r, 255 - g, 255 - b, a))
                                else:
                                    inverted_logo.putpixel((x, y), pixel)
                            else:  # RGB
                                r, g, b = pixel
                                inverted_logo.putpixel((x, y), (255 - r, 255 - g, 255 - b))
                        else:
                            # 灰度图像
                            inverted_logo.putpixel((x, y), 255 - pixel)
                return inverted_logo
        except Exception:
            # 如果处理失败，返回原始logo
            return logo
    
    def resize_logo(self, logo: Image.Image, target_size: Union[Tuple[int, int], int]) -> Image.Image:
        """
        调整logo的大小
        
        Args:
            logo: 原始logo图像
            target_size: 目标大小，可以是(width, height)元组或单个整数（保持比例）
            
        Returns:
            Image.Image: 调整大小后的logo图像
        """
        if not logo:
            return logo
            
        try:
            if isinstance(target_size, tuple):
                # 指定宽度和高度
                return logo.resize(target_size, Image.LANCZOS)
            else:
                # 保持比例，指定最长边
                width, height = logo.size
                if width > height:
                    new_width = target_size
                    new_height = int((target_size / width) * height)
                else:
                    new_height = target_size
                    new_width = int((target_size / height) * width)
                return logo.resize((new_width, new_height), Image.LANCZOS)
        except Exception:
            # 如果处理失败，返回原始logo
            return logo
    
    def _is_dark_color(self, color: str) -> bool:
        """
        判断颜色是否为深色
        
        Args:
            color: 颜色字符串（如"black", "#000000", "rgb(0,0,0)"等）
            
        Returns:
            bool: 是否为深色
        """
        # 简单实现，可根据实际需求扩展
        dark_colors = ["black", "dark", "#000000", "#333333", "#666666"]
        return color.lower() in dark_colors
    
    @abstractmethod
    def add_watermark(self, image: Image.Image, watermark_image: Image.Image, 
                     position: str = "bottom_right", opacity: float = 1.0, **kwargs) -> Image.Image:
        """
        添加水印图片到目标图像
        
        Args:
            image: 目标图像
            watermark_image: 水印图像
            position: 水印位置，可选值：
                - "top_left": 左上角
                - "top_center": 顶部中央
                - "top_right": 右上角
                - "middle_left": 中间左侧
                - "middle_center": 中间中央
                - "middle_right": 中间右侧
                - "bottom_left": 左下角
                - "bottom_center": 底部中央
                - "bottom_right": 右下角
                - (x, y): 自定义坐标（像素）
            opacity: 水印透明度，范围0.0-1.0
            **kwargs: 额外参数（如缩放比例、边距等）
            
        Returns:
            Image.Image: 添加水印后的图像
        """
        pass
    
    def get_watermark_position(self, image_size: Tuple[int, int], watermark_size: Tuple[int, int], 
                              position: str, margin: int = 20) -> Tuple[int, int]:
        """
        根据位置名称计算水印的实际坐标
        
        Args:
            image_size: 目标图像尺寸 (width, height)
            watermark_size: 水印图像尺寸 (width, height)
            position: 水印位置名称
            margin: 边距（像素）
            
        Returns:
            Tuple[int, int]: 水印左上角坐标 (x, y)
        """
        image_width, image_height = image_size
        watermark_width, watermark_height = watermark_size
        
        position_map = {
            "top_left": (margin, margin),
            "top_center": ((image_width - watermark_width) // 2, margin),
            "top_right": (image_width - watermark_width - margin, margin),
            "middle_left": (margin, (image_height - watermark_height) // 2),
            "middle_center": ((image_width - watermark_width) // 2, (image_height - watermark_height) // 2),
            "middle_right": (image_width - watermark_width - margin, (image_height - watermark_height) // 2),
            "bottom_left": (margin, image_height - watermark_height - margin),
            "bottom_center": ((image_width - watermark_width) // 2, image_height - watermark_height - margin),
            "bottom_right": (image_width - watermark_width - margin, image_height - watermark_height - margin)
        }
        
        if isinstance(position, tuple):
            # 自定义坐标
            return position
        elif position in position_map:
            return position_map[position]
        else:
            # 默认位置
            return position_map["bottom_right"]
    
    def adjust_watermark_opacity(self, watermark: Image.Image, opacity: float) -> Image.Image:
        """
        调整水印图像的透明度
        
        Args:
            watermark: 水印图像
            opacity: 透明度，范围0.0-1.0
            
        Returns:
            Image.Image: 调整透明度后的水印图像
        """
        if not watermark:
            return watermark
            
        if opacity >= 1.0:
            return watermark
            
        if opacity <= 0.0:
            # 创建一个完全透明的图像
            transparent = Image.new("RGBA", watermark.size, (0, 0, 0, 0))
            return transparent
            
        try:
            # 确保水印是RGBA格式
            if watermark.mode != "RGBA":
                watermark = watermark.convert("RGBA")
                
            # 分离通道
            r, g, b, a = watermark.split()
            
            # 调整Alpha通道
            a = a.point(lambda p: int(p * opacity))
            
            # 合并通道
            return Image.merge("RGBA", (r, g, b, a))
        except Exception:
            # 如果处理失败，返回原始水印
            return watermark
    
    def resize_watermark(self, watermark: Image.Image, target_width: Optional[int] = None, 
                        target_height: Optional[int] = None, scale: Optional[float] = None) -> Image.Image:
        """
        调整水印大小
        
        Args:
            watermark: 水印图像
            target_width: 目标宽度（像素）
            target_height: 目标高度（像素）
            scale: 缩放比例（0.0-1.0），优先级高于固定尺寸
            
        Returns:
            Image.Image: 调整大小后的水印图像
        """
        if not watermark:
            return watermark
            
        try:
            width, height = watermark.size
            
            if scale is not None:
                # 使用缩放比例
                new_width = int(width * scale)
                new_height = int(height * scale)
            elif target_width is not None and target_height is not None:
                # 使用固定尺寸
                new_width = target_width
                new_height = target_height
            elif target_width is not None:
                # 仅指定宽度，保持比例
                new_width = target_width
                new_height = int((target_width / width) * height)
            elif target_height is not None:
                # 仅指定高度，保持比例
                new_height = target_height
                new_width = int((target_height / height) * width)
            else:
                # 不调整大小
                return watermark
                
            return watermark.resize((new_width, new_height), Image.LANCZOS)
        except Exception:
            # 如果处理失败，返回原始水印
            return watermark