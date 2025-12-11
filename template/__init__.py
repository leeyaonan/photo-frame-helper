"""
相框模板模块初始化文件
用于自动注册所有模板类到模板上下文管理器
"""

import os
import sys
import importlib
from typing import List, Type

from .frame_template import FrameTemplate
from .template_context import get_template_context
from config.config_manager import config_manager

# 获取资源文件的路径，支持PyInstaller打包后的情况
def get_resource_path(relative_path):
    # 检查是否是PyInstaller打包后的环境
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # 如果是开发环境，直接返回相对路径
    return os.path.join(os.path.abspath(""), relative_path)

# 获取模板实现目录路径
# 在开发环境中使用相对路径，在PyInstaller打包后的环境中使用资源路径
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的环境
    TEMPLATE_IMPL_DIR = os.path.join(sys._MEIPASS, "template", "impl")
else:
    # 开发环境
    TEMPLATE_IMPL_DIR = os.path.join(os.path.dirname(__file__), "impl")

# 初始化模板上下文
_template_context = get_template_context()

# 直接导入模板模块，确保在PyInstaller打包后的环境中也能正确加载
try:
    # 导入黑底模板
    from .impl.black_bottom_template import BlackBottomTemplate
    _template_context.register_template(BlackBottomTemplate)
    print("已注册模板: BlackBottomTemplate")

except Exception as e:
    print(f"注册黑底模板失败: {e}")
    import traceback
    traceback.print_exc()

try:
    # 导入白底模板
    from .impl.white_bottom_template import WhiteBottomTemplate
    _template_context.register_template(WhiteBottomTemplate)
    print("已注册模板: WhiteBottomTemplate")
except Exception as e:
    print(f"注册白底模板失败: {e}")
    import traceback
    traceback.print_exc()


# 导出常用的类和函数
from .frame_template import FrameTemplate
from .template_context import TemplateContext, get_template_context

__all__ = ["FrameTemplate", "TemplateContext", "get_template_context"]