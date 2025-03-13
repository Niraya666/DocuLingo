from bs4 import BeautifulSoup, Tag
import re
from PIL import Image
import os
import base64
import io
from collections import namedtuple

ImageInfo = namedtuple('ImageInfo', ['bbox', 'index'])

def crop_image(image_path, bbox, output_path=None, output_format='PNG'):
    """
    根据bbox从原图中截取图像并保存
    
    Args:
        image_path: 原始图像的路径
        bbox: 边界框 [x1, y1, x2, y2]
        output_path: 输出图像的路径，如果为None则不保存
        output_format: 输出图像的格式，默认为PNG
        
    Returns:
        PIL.Image对象，截取后的图像
    """
    try:
        # 打开原始图像
        img = Image.open(image_path)
        
        # 截取指定区域
        cropped_img = img.crop(bbox)
        
        # 如果指定了输出路径，保存图像
        if output_path:
            directory = os.path.dirname(output_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            cropped_img.save(output_path, format=output_format)
            
        return cropped_img
    except Exception as e:
        print(f"Error cropping image: {e}")
        return None

def image_to_base64(image, format='PNG'):
    """
    将图像转换为base64编码的字符串
    
    Args:
        image: PIL.Image对象或图像文件路径
        format: 图像格式，默认为PNG
    
    Returns:
        base64编码的字符串
    """
    if isinstance(image, str):
        # 如果输入是文件路径，打开图像
        image = Image.open(image)
    
    # 将图像转换为字节流
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    
    # 获取base64编码
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return f"data:image/{format.lower()};base64,{img_str}"

def process_html_content(html_str, original_image_path, output_dir="images", embed_base64=False, start_index=1, page_num=None):
    """
    处理单个HTML内容
    
    Args:
        html_str: 包含HTML内容的字符串
        original_image_path: 原始图像的路径
        output_dir: 图片保存目录
        embed_base64: 是否将图像转换为base64格式嵌入HTML
        start_index: 图像索引的起始值
        page_num: 当前处理的页码
    
    Returns:
        tuple: (formatted_html, image_bboxes, image_paths, next_index)
            - formatted_html: 格式化后的HTML字符串（只包含body内容）
            - image_bboxes: 包含图像bbox信息的列表
            - image_paths: 保存的图像路径列表（绝对路径）
            - next_index: 下一页图像应该使用的起始索引
    """
    os.makedirs(output_dir, exist_ok=True)
    
    soup = BeautifulSoup(html_str, 'html.parser')
    image_bboxes = []
    image_paths = []
    image_index = start_index
    
    for div in soup.find_all('div', class_='image'):
        bbox_str = div.get('data-bbox')
        if bbox_str:
            bbox = [int(x) for x in bbox_str.split()]
            image_bboxes.append(ImageInfo(bbox=bbox, index=image_index, page=page_num))
            
            # 设置图像文件名和路径
            image_filename = f"image_{image_index}.png"
            image_path = os.path.join(output_dir, image_filename)
            image_paths.append(os.path.abspath(image_path))
            
            # 截取并保存图像
            cropped_img = crop_image(original_image_path, bbox, image_path)
            
            # 更新div和img标签
            div['id'] = f'image_{image_index}'
            if 'data-bbox' in div.attrs:
                del div['data-bbox']
            
            img_tag = div.find('img') or soup.new_tag('img')
            if 'data-bbox' in img_tag.attrs:
                del img_tag['data-bbox']
            
            # 更新图片源
            if embed_base64 and cropped_img:
                img_tag['src'] = image_to_base64(cropped_img)
            else:
                img_tag['src'] = os.path.join(output_dir, image_filename)
            
            if img_tag.parent is None:
                div.append(img_tag)
            
            image_index += 1
    
    # 清理和格式化HTML
    # 移除不需要的属性
    for tag in soup.find_all(True):
        attrs_to_remove = ['data-polygon', 'data-bbox']
        for attr in attrs_to_remove:
            if attr in tag.attrs:
                del tag[attr]
    
    # 使用原始clean_and_format_html函数的逻辑
    color_pattern = re.compile(r'\bcolor:[^;]+;?')
    
    for tag in soup.find_all(style=True):
        original_style = tag.get('style', '')
        new_style = color_pattern.sub('', original_style)
        if not new_style.strip():
            del tag['style']
        else:
            new_style = new_style.rstrip(';')
            tag['style'] = new_style
    
    classes_to_update = ['formula.machine_printed', 'formula.handwritten']
    for tag in soup.find_all(class_=True):
        if isinstance(tag, Tag) and 'class' in tag.attrs:
            new_classes = [cls if cls not in classes_to_update else 'formula' for cls in tag.get('class', [])]
            tag['class'] = list(dict.fromkeys(new_classes))
    
    for div in soup.find_all('div', class_='image caption'):
        div.clear()
        div['class'] = ['image']
    
    classes_to_clean = ['music sheet', 'chemical formula', 'chart']
    for class_name in classes_to_clean:
        for tag in soup.find_all(class_=class_name):
            if isinstance(tag, Tag):
                tag.clear()
                if 'format' in tag.attrs:
                    del tag['format']
    
    # 提取body内容
    body_content = soup.body.decode_contents() if soup.body else ""
    
    return body_content.strip(), image_bboxes, image_paths, image_index


