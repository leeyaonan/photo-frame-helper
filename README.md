# 照片相框助手 (Photo Frame Helper)

一个功能强大的照片处理工具，支持批量为照片添加相框和EXIF信息，提供GUI和CLI两种操作模式。

## 🎯 功能特点

- **批量处理**：支持批量为多张照片添加相框和EXIF信息
- **相框模板**：提供多种预定义相框模板和自定义选项
- **EXIF信息**：自动提取并显示照片的拍摄参数（相机型号、光圈、快门速度、ISO等）
- **品牌支持**：内置多种相机品牌Logo（Canon、Nikon、Sony、Fujifilm等）
- **双模式操作**：
  - GUI模式：直观的图形界面，易于使用
  - CLI模式：命令行操作，适合自动化脚本
- **实时预览**：处理后照片实时预览功能
- **灵活输出**：自定义输出目录和文件名

## 📦 安装说明

### 环境要求
- Python 3.8+
- Pillow (PIL)
- tkinter (Python标准库)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/leeyaonan/photo-frame-helper.git
   cd photo-frame-helper
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

   或手动安装：
   ```bash
   pip install Pillow
   ```

## 🚀 使用指南

### GUI模式（推荐）

1. **启动应用**
   ```bash
   python photo_frame_helper.py
   ```

2. **使用步骤**
   - 点击「选择照片」添加要处理的照片
   - 选择相框模板或自定义相框设置
   - 选择输出目录
   - 点击「批量处理」开始处理
   - 在处理结果列表中点击照片进行预览或打开

### CLI模式

```bash
python cli_version.py --input <照片目录> --output <输出目录> --frame-color <颜色> --frame-width <宽度> --params <参数1> <参数2>...
```

**参数说明**：
- `--input`：输入照片目录路径
- `--output`：输出照片目录路径
- `--frame-color`：相框颜色（如black、white等）
- `--frame-width`：相框宽度（像素）
- `--params`：要显示的EXIF参数（如"相机型号"、"光圈"、"快门速度"、"ISO"等）

**示例**：
```bash
python cli_version.py --input test_photos --output test_output --frame-color black --frame-width 20 --params "相机型号" "光圈" "快门速度" "ISO"
```

## 📁 项目结构

```
photo-frame-helper/
├── entity/              # 实体类目录
│   └── photo.py        # Photo类，封装照片信息
├── logo/               # 相机品牌Logo图片
├── release_notes/      # 版本发布说明
├── template/           # 相框模板目录
├── test/               # 测试目录
│   ├── test_output/    # 测试输出目录
│   └── test_photos/    # 测试照片目录
├── .gitignore          # Git忽略文件配置
├── cli_version.py      # 命令行版本主程序
├── photo_frame_helper.py # GUI版本主程序
├── requirements.txt    # 项目依赖
├── simple_gui.py       # 简单GUI版本（备用）
└── README.md           # 项目说明文档
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- GitHub Issue：[项目Issues页面](https://github.com/leeyaonan/photo-frame-helper/issues)

## 📋 更新日志

### v1.0.0 (2025-12-09)
- ✨ 初始版本发布
- 🎨 支持GUI和CLI两种操作模式
- 📷 内置11种相机品牌Logo
- 🖼️ 多种相框模板和自定义选项
- 📊 EXIF信息自动提取和显示
- 🔄 批量照片处理功能

---

**Enjoy using Photo Frame Helper! 📸**