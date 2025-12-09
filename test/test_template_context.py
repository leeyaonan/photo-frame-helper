#!/usr/bin/env python3
"""
模板上下文管理器的单元测试
测试模板的注册、获取和使用功能
"""

import os
import sys
import unittest
from PIL import Image

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))

from template.template_context import get_template_context
from entity.photo import Photo


class TestTemplateContext(unittest.TestCase):
    """
    测试模板上下文管理器的功能
    """
    
    def setUp(self):
        """
        设置测试环境
        """
        self.template_context = get_template_context()
        self.test_photos_dir = os.path.join(os.path.dirname(__file__), "test_photos")
        self.test_output_dir = os.path.join(os.path.dirname(__file__), "test_output")
        
        # 确保测试输出目录存在
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
        
        # 获取测试照片路径
        self.test_photo_path1 = os.path.join(self.test_photos_dir, "DSC_0268.JPG")
        self.test_photo_path2 = os.path.join(self.test_photos_dir, "DSC_0269.JPG")
    
    def test_get_template_context(self):
        """
        测试获取模板上下文实例
        """
        self.assertIsNotNone(self.template_context)
    
    def test_get_default_template(self):
        """
        测试获取默认模板
        """
        default_template = self.template_context.get_default_template()
        self.assertIsNotNone(default_template)
        self.assertEqual(default_template.name, "黑色底边")
    
    def test_get_all_template_names(self):
        """
        测试获取所有模板名称
        """
        template_names = self.template_context.get_all_template_names()
        self.assertEqual(len(template_names), 2)
        self.assertIn("黑色底边", template_names)
        self.assertIn("白色底边", template_names)
    
    def test_get_template(self):
        """
        测试获取指定模板
        """
        # 测试获取黑色底边模板
        black_template = self.template_context.get_template("黑色底边")
        self.assertIsNotNone(black_template)
        self.assertEqual(black_template.name, "黑色底边")
        
        # 测试获取白色底边模板
        white_template = self.template_context.get_template("白色底边")
        self.assertIsNotNone(white_template)
        self.assertEqual(white_template.name, "白色底边")
        
        # 测试获取不存在的模板
        nonexistent_template = self.template_context.get_template("不存在的模板")
        self.assertIsNone(nonexistent_template)
    
    def test_generate_black_bottom_frame(self):
        """
        测试使用黑色底边模板生成带框照片
        """
        print("\n=== 开始测试黑色底边模板 ===")
        if not os.path.exists(self.test_photo_path1):
            self.skipTest(f"测试照片不存在: {self.test_photo_path1}")
        
        # 获取黑色底边模板
        black_template = self.template_context.get_template("黑色底边")
        self.assertIsNotNone(black_template)
        
        # 加载测试照片
        photo = Photo(self.test_photo_path1)
        self.assertIsNotNone(photo)
        
        # 使用模板生成带框照片
        try:
            framed_image = black_template.create_frame(photo)
            self.assertIsNotNone(framed_image)
            self.assertIsInstance(framed_image, Image.Image)
            
            # 保存生成的照片
            output_path = os.path.join(self.test_output_dir, "DSC_0268_black_frame.jpg")
            framed_image.save(output_path)
            self.assertTrue(os.path.exists(output_path))
            print(f"黑色底边模板测试成功，生成的照片已保存到: {output_path}")
        except Exception as e:
            self.fail(f"使用黑色底边模板生成照片失败: {e}")
    
    def test_generate_white_bottom_frame(self):
        """
        测试使用白色底边模板生成带框照片
        """
        print("\n=== 开始测试白色底边模板 ===")
        if not os.path.exists(self.test_photo_path2):
            self.skipTest(f"测试照片不存在: {self.test_photo_path2}")
        
        # 获取白色底边模板
        white_template = self.template_context.get_template("白色底边")
        self.assertIsNotNone(white_template)
        
        # 加载测试照片
        photo = Photo(self.test_photo_path2)
        self.assertIsNotNone(photo)
        
        # 使用模板生成带框照片
        try:
            framed_image = white_template.create_frame(photo)
            self.assertIsNotNone(framed_image)
            self.assertIsInstance(framed_image, Image.Image)
            
            # 保存生成的照片
            output_path = os.path.join(self.test_output_dir, "DSC_0269_white_frame.jpg")
            framed_image.save(output_path)
            self.assertTrue(os.path.exists(output_path))
            print(f"白色底边模板测试成功，生成的照片已保存到: {output_path}")
        except Exception as e:
            self.fail(f"使用白色底边模板生成照片失败: {e}")
    
    def test_both_templates(self):
        """
        测试同时使用两个模板处理同一张照片
        """
        print("\n=== 开始测试同时使用两个模板 ===")
        if not os.path.exists(self.test_photo_path1):
            self.skipTest(f"测试照片不存在: {self.test_photo_path1}")
        
        # 加载测试照片
        photo = Photo(self.test_photo_path1)
        self.assertIsNotNone(photo)
        
        # 使用黑色底边模板
        black_template = self.template_context.get_template("黑色底边")
        self.assertIsNotNone(black_template)
        
        # 使用白色底边模板
        white_template = self.template_context.get_template("白色底边")
        self.assertIsNotNone(white_template)
        
        try:
            # 使用黑色底边模板生成带框照片
            black_framed = black_template.create_frame(photo)
            self.assertIsNotNone(black_framed)
            
            # 使用白色底边模板生成带框照片
            white_framed = white_template.create_frame(photo)
            self.assertIsNotNone(white_framed)
            
            # 保存生成的照片
            black_output = os.path.join(self.test_output_dir, "DSC_0268_both_black.jpg")
            white_output = os.path.join(self.test_output_dir, "DSC_0268_both_white.jpg")
            
            black_framed.save(black_output)
            white_framed.save(white_output)
            
            self.assertTrue(os.path.exists(black_output))
            self.assertTrue(os.path.exists(white_output))
            
            print(f"同时使用两个模板测试成功，生成的照片已保存到: {black_output} 和 {white_output}")
        except Exception as e:
            self.fail(f"同时使用两个模板生成照片失败: {e}")


if __name__ == "__main__":
    print("=== 开始测试模板上下文管理器 ===")
    unittest.main(verbosity=2)