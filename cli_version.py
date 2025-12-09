import os
import sys
import argparse
import glob
from PIL import Image, ImageDraw, ImageFont, ExifTags
from entity.photo import Photo

# 定义中文参数到EXIF标签的映射
EXIF_MAPPING = {
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

# 定义所有可用的EXIF参数
ALL_EXIF_PARAMS = list(EXIF_MAPPING.keys())

def get_exif_data(image_path):
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

def process_image(photo, output_dir, frame_color, frame_width, selected_params):
    """处理单张图片"""
    try:
        # 计算新尺寸（添加相框）
        new_width = photo.width + 2 * frame_width
        new_height = photo.height + 2 * frame_width
        
        # 创建新图片（包含相框）
        new_img = Image.new("RGB", (new_width, new_height), frame_color)
        new_img.paste(photo.img, (frame_width, frame_width))
        
        # 添加EXIF信息（如果有选中参数）
        if selected_params:
            draw = ImageDraw.Draw(new_img)
            # 使用默认字体
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            y_offset = frame_width + 10
            for param in selected_params:
                if param in EXIF_MAPPING:
                    exif_tag = EXIF_MAPPING[param]
                    if exif_tag in photo.exif_data:
                        value = photo.exif_data[exif_tag]
                        text = f"{param}: {value}"
                        draw.text((frame_width + 10, y_offset), text, fill="white", font=font)
                        y_offset += 20
        
        # 保存新图片
        filename = os.path.basename(photo.path)
        new_filename = f"framed_{filename}"
        new_file_path = os.path.join(output_dir, new_filename)
        
        new_img.save(new_file_path, "JPEG")
        return True, new_file_path
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="照片相框助手 - 命令行版本")
    
    # 添加参数
    parser.add_argument("--input", "-i", required=True, help="输入照片文件或目录路径")
    parser.add_argument("--output", "-o", required=True, help="输出目录路径")
    parser.add_argument("--frame-color", "-c", default="black", choices=["black", "white"], help="相框模板")
    parser.add_argument("--frame-width", "-w", type=int, default=20, help="相框宽度（像素）")
    parser.add_argument("--params", "-p", nargs="+", choices=ALL_EXIF_PARAMS, help="要显示的EXIF参数")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)
    
    # 收集照片文件
    photo_files = []
    if os.path.isfile(args.input):
        if args.input.lower().endswith((".jpg", ".jpeg")):
            photo_files.append(args.input)
    elif os.path.isdir(args.input):
        photo_files.extend(glob.glob(os.path.join(args.input, "*.jpg")))
        photo_files.extend(glob.glob(os.path.join(args.input, "*.jpeg")))
    else:
        print(f"输入路径不存在: {args.input}")
        return
    
    if not photo_files:
        print("没有找到JPG/JPEG文件")
        return
    
    print(f"找到 {len(photo_files)} 张照片")
    print(f"相框模板: {args.frame_color}")
    print(f"相框宽度: {args.frame_width} 像素")
    print(f"显示的EXIF参数: {', '.join(args.params) if args.params else '无'}")
    print(f"输出目录: {args.output}")
    print("\n开始处理照片...")
    
    success_count = 0
    for i, photo_path in enumerate(photo_files, 1):
        print(f"处理 {i}/{len(photo_files)}: {os.path.basename(photo_path)}")
        try:
            # 创建Photo对象封装照片信息
            photo = Photo(photo_path)
            success, result = process_image(photo, args.output, args.frame_color, args.frame_width, args.params)
        except Exception as e:
            success = False
            result = str(e)
            
        if success:
            print(f"  ✓ 成功: {result}")
            success_count += 1
        else:
            print(f"  ✗ 失败: {result}")
    
    print(f"\n处理完成! 成功: {success_count}, 失败: {len(photo_files) - success_count}")
    
    # 显示所有可用的EXIF参数
    print("\n可用的EXIF参数:")
    for param in ALL_EXIF_PARAMS:
        print(f"  - {param}")

if __name__ == "__main__":
    main()
