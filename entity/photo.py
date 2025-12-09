import os
from PIL import Image, ExifTags

class Photo:
    """
    照片信息封装类
    封装照片的路径、图片对象、EXIF数据等信息
    """
    
    def __init__(self, image_path):
        """
        初始化Photo对象
        
        Args:
            image_path: 照片文件路径
        """
        self.image_path = image_path
        self.filename = os.path.basename(image_path)
        self.img = None
        self.exif_data = {}
        self.orientation = 1
        
        # 初始化时加载照片和EXIF数据
        self._load_photo()
        self._load_exif_data()
    
    def _load_photo(self):
        """加载照片"""
        try:
            self.img = Image.open(self.image_path)
        except Exception as e:
            raise Exception(f"加载照片失败: {e}")
    
    def _load_exif_data(self):
        """加载EXIF数据"""
        try:
            exif = self.img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    self.exif_data[tag] = value
            
            # 获取照片方向信息
            self.orientation = self.exif_data.get('Orientation', 1)
        except Exception as e:
            print(f"读取EXIF数据失败: {e}")
    
    def fix_orientation(self):
        """根据EXIF信息修复照片方向"""
        if self.orientation == 2:
            self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
        elif self.orientation == 3:
            self.img = self.img.transpose(Image.ROTATE_180)
        elif self.orientation == 4:
            self.img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        elif self.orientation == 5:
            self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
        elif self.orientation == 6:
            self.img = self.img.transpose(Image.ROTATE_270)
        elif self.orientation == 7:
            self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif self.orientation == 8:
            self.img = self.img.transpose(Image.ROTATE_90)
        
        # 更新方向为正常方向（1），防止重复旋转
        self.orientation = 1
        
        return self.img
    
    @property
    def width(self):
        """获取照片宽度"""
        return self.img.width if self.img else 0
    
    @property
    def height(self):
        """获取照片高度"""
        return self.img.height if self.img else 0
    
    def get_exif_value(self, param_name, mapping=None):
        """
        根据参数名获取EXIF值
        
        Args:
            param_name: 中文参数名
            mapping: 参数名到EXIF标签的映射
            
        Returns:
            EXIF值
        """
        if mapping and param_name in mapping:
            exif_tag = mapping[param_name]
            return self.exif_data.get(exif_tag, "")
        return ""