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

# 获取模板实现目录路径
TEMPLATE_IMPL_DIR = os.path.join(os.path.dirname(__file__), "impl")


def _load_template_classes() -> List[Type[FrameTemplate]]:
    """
    动态加载impl目录下的所有模板类
    
    返回:
        模板类列表
    """
    template_classes = []
    
    # 确保impl目录在Python路径中
    if TEMPLATE_IMPL_DIR not in sys.path:
        sys.path.append(TEMPLATE_IMPL_DIR)
    
    try:
        # 遍历impl目录下的所有.py文件
        for filename in os.listdir(TEMPLATE_IMPL_DIR):
            if filename.endswith(".py") and not filename.startswith("_"):
                # 获取模块名（去掉.py后缀）
                module_name = filename[:-3]
                
                try:
                    # 导入模块
                    module = importlib.import_module(module_name)
                    
                    # 遍历模块中的所有属性
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # 检查是否为类，是否继承自FrameTemplate，且不是FrameTemplate本身
                        if (
                            isinstance(attr, type) and 
                            issubclass(attr, FrameTemplate) and 
                            attr is not FrameTemplate and
                            not attr.__name__.startswith("_")  # 排除私有类
                        ):
                            template_classes.append(attr)
                except Exception as e:
                    print(f"加载模板模块 {module_name} 失败: {e}")
    except Exception as e:
        print(f"遍历模板实现目录失败: {e}")
    
    return template_classes


# 初始化模板上下文
_template_context = get_template_context()

# 加载并注册所有模板类
_template_classes = _load_template_classes()
for template_class in _template_classes:
    try:
        _template_context.register_template(template_class)
        print(f"已注册模板: {template_class.__name__}")
    except Exception as e:
        print(f"注册模板 {template_class.__name__} 失败: {e}")


# 导出常用的类和函数
from .frame_template import FrameTemplate
from .template_context import TemplateContext, get_template_context

__all__ = ["FrameTemplate", "TemplateContext", "get_template_context"]