from typing import Dict, Type, Optional
from .frame_template import FrameTemplate

class TemplateContext:
    """
    模板策略管理类，用于统一注册、管理和使用各种相框模板策略
    采用策略模式实现，提供模板的注册、获取和管理功能
    """
    
    def __init__(self):
        # 存储注册的模板类，键为模板名称，值为模板类
        self._templates: Dict[str, Type[FrameTemplate]] = {}
        # 默认模板名称
        self._default_template_name: Optional[str] = None
    
    def register_template(self, template_class: Type[FrameTemplate]) -> None:
        """
        注册一个新的模板策略类
        
        参数:
            template_class: 继承自FrameTemplate的模板策略类
        """
        if not issubclass(template_class, FrameTemplate):
            raise TypeError(f"模板类必须继承自FrameTemplate: {template_class.__name__}")
        
        # 创建模板实例以获取名称
        template_instance = template_class()
        template_name = template_instance.name
        
        # 注册模板
        self._templates[template_name] = template_class
        
        # 如果这是第一个注册的模板，将其设为默认模板
        if self._default_template_name is None:
            self._default_template_name = template_name
    
    def get_template(self, template_name: str) -> Optional[FrameTemplate]:
        """
        根据名称获取模板实例
        
        参数:
            template_name: 模板名称
            
        返回:
            模板实例，如果找不到则返回None
        """
        if template_name not in self._templates:
            return None
        
        # 创建并返回模板实例
        return self._templates[template_name]()
    
    def get_all_templates(self) -> Dict[str, Type[FrameTemplate]]:
        """
        获取所有注册的模板类
        
        返回:
            所有注册的模板类字典，键为模板名称，值为模板类
        """
        return self._templates.copy()
    
    def get_all_template_names(self) -> list:
        """
        获取所有注册的模板名称列表
        
        返回:
            模板名称列表
        """
        return list(self._templates.keys())
    
    def get_default_template(self) -> Optional[FrameTemplate]:
        """
        获取默认模板实例
        
        返回:
            默认模板实例，如果没有设置则返回None
        """
        if self._default_template_name is None:
            return None
        
        return self.get_template(self._default_template_name)
    
    def set_default_template(self, template_name: str) -> bool:
        """
        设置默认模板
        
        参数:
            template_name: 模板名称
            
        返回:
            设置成功返回True，失败返回False
        """
        if template_name in self._templates:
            self._default_template_name = template_name
            return True
        return False
    
    def unregister_template(self, template_name: str) -> bool:
        """
        注销一个模板
        
        参数:
            template_name: 模板名称
            
        返回:
            注销成功返回True，失败返回False
        """
        if template_name in self._templates:
            del self._templates[template_name]
            
            # 如果注销的是默认模板，重新设置默认模板
            if self._default_template_name == template_name:
                self._default_template_name = next(iter(self._templates.keys()), None)
            
            return True
        return False
    
    def clear_templates(self) -> None:
        """
        清除所有注册的模板
        """
        self._templates.clear()
        self._default_template_name = None

# 创建全局模板上下文实例
# 这样可以在应用程序的任何地方使用同一个模板上下文
# 方便统一管理所有模板
_template_context = TemplateContext()

def get_template_context() -> TemplateContext:
    """
    获取全局模板上下文实例
    
    返回:
        全局模板上下文实例
    """
    return _template_context