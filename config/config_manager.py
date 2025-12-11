import yaml
import os
import sys
from pathlib import Path


class ConfigManager:
    """
    配置管理器，用于加载和解析application.yml配置文件
    """
    
    def __init__(self, config_file=None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        if config_file is None:
            # 获取资源文件的路径，支持PyInstaller打包后的情况
            def get_resource_path(relative_path):
                # 检查是否是PyInstaller打包后的环境
                if hasattr(sys, '_MEIPASS'):
                    return os.path.join(sys._MEIPASS, relative_path)
                # 如果是开发环境，直接返回相对路径
                return os.path.join(os.path.abspath(""), relative_path)
            
            # 默认配置文件路径
            config_file = get_resource_path("application.yml")
        
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 解析后的配置字典
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告：配置文件 {self.config_file} 不存在，将使用默认配置")
            return self.get_default_config()
        except yaml.YAMLError as e:
            print(f"错误：解析配置文件失败 - {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """
        获取默认配置
        
        Returns:
            dict: 默认配置字典
        """
        return {
            'application': {
                'name': 'PhotoFrame Helper',
                'version': '1.0.0',
                'description': '一个简单易用的照片相框生成工具',
                'window': {
                    'title': 'PhotoFrame Helper - 照片相框生成工具',
                    'width': 800,
                    'height': 600
                },
                'logo': {
                    'path': 'photo_frame_helper_logo.png',
                    'directory': 'logo'
                }
            },
            'output': {
                'default_directory': 'output',
                'default_naming_pattern': '{original_name}_frame'
            },
            'template': {
                'default_template': 'black_bottom',
                'directory': 'template/impl',
                'templates': ['black_bottom_template', 'white_bottom_template']
            },
            'logging': {
                'level': 'INFO',
                'file': 'photo_frame_helper.log'
            }
        }
    
    def get_config(self, key=None, default=None):
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分隔符（如 "application.name"）
            default: 默认值
        
        Returns:
            配置值
        """
        if key is None:
            return self.config
        
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_application_name(self):
        """
        获取应用程序名称
        
        Returns:
            str: 应用程序名称
        """
        return self.get_config('application.name')
    
    def get_application_version(self):
        """
        获取应用程序版本
        
        Returns:
            str: 应用程序版本
        """
        return self.get_config('application.version')
    
    def get_window_title(self):
        """
        获取窗口标题
        
        Returns:
            str: 窗口标题
        """
        return self.get_config('application.window.title')
    
    def get_window_size(self):
        """
        获取窗口大小
        
        Returns:
            tuple: (宽度, 高度)
        """
        width = self.get_config('application.window.width')
        height = self.get_config('application.window.height')
        return (width, height)
    
    def get_logo_path(self):
        """
        获取Logo文件路径
        
        Returns:
            str: Logo文件路径
        """
        return self.get_config('application.logo.path')
    
    def get_logo_directory(self):
        """
        获取Logo目录
        
        Returns:
            str: Logo目录
        """
        return self.get_config('application.logo.directory')
    
    def get_default_output_directory(self):
        """
        获取默认输出目录
        
        Returns:
            str: 默认输出目录
        """
        return self.get_config('output.default_directory')
    
    def get_default_naming_pattern(self):
        """
        获取默认文件命名模式
        
        Returns:
            str: 默认文件命名模式
        """
        return self.get_config('output.default_naming_pattern')
    
    def get_default_template(self):
        """
        获取默认模板
        
        Returns:
            str: 默认模板名称
        """
        return self.get_config('template.default_template')
    
    def get_template_directory(self):
        """
        获取模板目录
        
        Returns:
            str: 模板目录
        """
        return self.get_config('template.directory')
    
    def get_templates(self):
        """
        获取要加载的模板列表
        
        Returns:
            list: 模板文件名列表（不含.py后缀）
        """
        return self.get_config('template.templates')
    
    def get_logging_level(self):
        """
        获取日志级别
        
        Returns:
            str: 日志级别
        """
        return self.get_config('logging.level')
    
    def get_logging_file(self):
        """
        获取日志文件路径
        
        Returns:
            str: 日志文件路径
        """
        return self.get_config('logging.file')


# 创建全局配置实例
config_manager = ConfigManager()
