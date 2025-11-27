import re
import base64
from typing import Union, List, Tuple
from io import BytesIO
from PIL import Image


def is_valid_base64_image(data: str) -> bool:
    """
    验证是否为有效的Base64图片格式
    格式：data:image/<format>;base64,<base64_data>
    """
    base64_pattern = re.compile(
        r'^data:image/(png|jpg|jpeg);base64,([A-Za-z0-9+/=]+)$',
        re.IGNORECASE
    )
    return base64_pattern.match(data) is not None


def validate_image_format(image_input: str) -> Tuple[bool, str]:
    """
    验证图片格式（仅支持Base64）
    
    Args:
        image_input: 图片输入（Base64字符串）
        
    Returns:
        Tuple[bool, str]: (是否有效, 格式类型: 'base64'/'invalid')
    """
    if is_valid_base64_image(image_input):
        return True, 'base64'
    else:
        return False, 'invalid'


def normalize_image_input(image_input: str) -> str:
    """
    标准化图片输入格式（仅支持Base64）
    
    Args:
        image_input: 图片输入（Base64编码）
        
    Returns:
        str: 标准化后的图片输入
        
    Raises:
        ValueError: 格式不正确时抛出异常
    """
    is_valid, format_type = validate_image_format(image_input)
    
    if not is_valid:
        raise ValueError("图片格式不正确，请提供有效的Base64编码（格式：data:image/<format>;base64,<base64_data>）")
    
    # 验证图片格式是否为 jpeg 或 png
    match = re.match(r'^data:image/([a-z]+);base64,', image_input, re.IGNORECASE)
    if match:
        img_format = match.group(1).lower()
        if img_format not in ['png', 'jpg', 'jpeg']:
            raise ValueError(f"不支持的图片格式: {img_format}，仅支持: jpeg、png")
    
    return image_input


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    解码 Base64 字符串为 PIL Image 对象
    
    Args:
        base64_string: Base64 编码的图片字符串
        
    Returns:
        Image.Image: PIL Image 对象
        
    Raises:
        ValueError: 解码失败时抛出异常
    """
    try:
        # 提取 Base64 数据部分
        if base64_string.startswith('data:image'):
            base64_data = base64_string.split(',')[1]
        else:
            base64_data = base64_string
        
        # 解码 Base64
        image_bytes = base64.b64decode(base64_data)
        
        # 转换为 PIL Image
        image = Image.open(BytesIO(image_bytes))
        return image
    except Exception as e:
        raise ValueError(f"Base64 图片解码失败: {e}")


def validate_image_constraints(base64_string: str) -> Tuple[bool, str]:
    """
    验证图片是否满足所有约束条件
    
    约束条件：
    - 图片格式：jpeg、png
    - 宽高比（宽/高）范围：[1/3, 3]
    - 宽高长度（px） > 14
    - 大小：不超过 10MB
    - 总像素：不超过 6000×6000 px
    
    Args:
        base64_string: Base64 编码的图片字符串
        
    Returns:
        Tuple[bool, str]: (是否通过验证, 错误信息)
    """
    try:
        # 1. 检查文件大小（Base64 解码前）
        if base64_string.startswith('data:image'):
            base64_data = base64_string.split(',')[1]
        else:
            base64_data = base64_string
        
        # Base64 解码后的字节大小
        image_bytes = base64.b64decode(base64_data)
        file_size_mb = len(image_bytes) / (1024 * 1024)
        
        if file_size_mb > 10:
            return False, f"图片大小超过限制，当前大小: {file_size_mb:.2f}MB，最大允许: 10MB"
        
        # 2. 解码图片
        image = Image.open(BytesIO(image_bytes))
        
        # 3. 检查图片格式
        image_format = image.format.lower() if image.format else ''
        if image_format not in ['jpeg', 'jpg', 'png']:
            return False, f"图片格式不支持，当前格式: {image_format}，仅支持: jpeg、png"
        
        # 4. 获取图片尺寸
        width, height = image.size
        
        # 5. 检查宽高长度
        if width <= 14 or height <= 14:
            return False, f"图片宽高必须大于14px，当前尺寸: {width}x{height}px"
        
        # 6. 检查总像素
        total_pixels = width * height
        max_pixels = 6000 * 6000
        if total_pixels > max_pixels:
            return False, f"图片总像素超过限制，当前: {total_pixels}px，最大允许: {max_pixels}px"
        
        # 7. 检查宽高比
        aspect_ratio = width / height
        if aspect_ratio < 1/3 or aspect_ratio > 3:
            return False, f"图片宽高比超出范围，当前: {aspect_ratio:.2f}，允许范围: [0.33, 3.00]"
        
        return True, "验证通过"
        
    except Exception as e:
        return False, f"图片验证失败: {str(e)}"


def prepare_image_list_for_api(image_inputs: List[str]) -> Union[str, List[str]]:
    """
    准备图片列表用于API调用
    - 单图：返回字符串
    - 多图：返回列表
    
    Args:
        image_inputs: 图片输入列表（Base64编码）
        
    Returns:
        Union[str, List[str]]: 单图返回字符串，多图返回列表
        
    Raises:
        ValueError: 图片格式不正确时抛出异常
    """
    if not image_inputs:
        raise ValueError("图片列表不能为空")
    
    normalized_images = [normalize_image_input(img) for img in image_inputs]
    
    if len(normalized_images) == 1:
        return normalized_images[0]
    else:
        return normalized_images
