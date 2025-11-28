import re
import base64
from typing import Union, List, Tuple
from io import BytesIO
from pathlib import Path
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


def load_local_image_to_base64(file_path: Union[str, Path]) -> str:
    """
    从本地文件加载图片并转换为 Base64 编码
    
    Args:
        file_path: 图片文件路径
        
    Returns:
        str: Base64 编码的图片字符串（格式：data:image/<format>;base64,<base64_data>）
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的图片格式
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"图片文件不存在: {file_path}")
    
    # 读取文件
    with open(file_path, 'rb') as f:
        image_bytes = f.read()
    
    # Base64 编码
    base64_data = base64.b64encode(image_bytes).decode('utf-8')
    
    # 根据文件扩展名确定 MIME 类型
    ext = file_path.suffix.lower()
    if ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif ext == '.png':
        mime_type = 'image/png'
    else:
        raise ValueError(f"不支持的图片格式: {ext}，仅支持 .jpg, .jpeg, .png")
    
    return f"data:{mime_type};base64,{base64_data}"


def load_clothes_image(sex: int, upper_style_id: int = None, lower_style_id: int = None, dress_id: int = None) -> List[str]:
    """
    根据性别和样式ID加载服装图片
    
    Args:
        sex: 性别（0=男，1=女）
        upper_style_id: 上装样式ID（可选）
        lower_style_id: 下装样式ID（可选）
        dress_id: 连衣裙样式ID（可选，仅女性）
        
    Returns:
        List[str]: 服装图片Base64列表
        
    Raises:
        FileNotFoundError: 图片文件不存在
        ValueError: 参数错误
        
    Example:
        >>> # 男性上装+下装
        >>> load_clothes_image(sex=0, upper_style_id=101, lower_style_id=201)
        ['data:image/jpeg;base64,...', 'data:image/jpeg;base64,...']
        
        >>> # 女性连衣裙
        >>> load_clothes_image(sex=1, dress_id=301)
        ['data:image/jpeg;base64,...']
    """
    # 获取服装图片根目录
    clothes_dir = Path(__file__).parent / "pictures" / "clothes"
    
    # 根据性别确定子目录
    if sex == 0:  # 男性
        gender_dir = clothes_dir / "male"
        if dress_id is not None:
            raise ValueError("男性不能选择连衣裙")
        if upper_style_id is None or lower_style_id is None:
            raise ValueError("男性必须同时选择上装和下装")
    elif sex == 1:  # 女性
        gender_dir = clothes_dir / "male" / "female"  # 根据你的实际目录结构
        # 连衣裙和上下装二选一
        has_dress = dress_id is not None
        has_upper_lower = upper_style_id is not None or lower_style_id is not None
        if has_dress and has_upper_lower:
            raise ValueError("女性不能同时选择连衣裙和上装下装")
        if has_upper_lower and (upper_style_id is None or lower_style_id is None):
            raise ValueError("女性选择上装下装时，必须同时选择上装和下装")
    else:
        raise ValueError(f"无效的性别值: {sex}，必须是 0（男）或 1（女）")
    
    result = []
    
    # 加载连衣裙
    if dress_id is not None:
        dress_file = gender_dir / f"female_dress_{dress_id}.jpg"
        if not dress_file.exists():
            # 尝试其他可能的命名
            dress_file = gender_dir / f"dress_{dress_id}.jpg"
        result.append(load_local_image_to_base64(dress_file))
    
    # 加载上装+下装
    if upper_style_id is not None and lower_style_id is not None:
        # 根据性别确定文件前缀
        prefix = "male" if sex == 0 else "female"
        
        # 上装文件
        upper_file = gender_dir / f"{prefix}_clothes.jpg"
        if not upper_file.exists():
            upper_file = gender_dir / f"{prefix}_top_{upper_style_id}.jpg"
        
        # 下装文件
        lower_file = gender_dir / f"{prefix}_pants.jpg"
        if not lower_file.exists():
            lower_file = gender_dir / f"{prefix}_bottom_{lower_style_id}.jpg"
        
        result.append(load_local_image_to_base64(upper_file))
        result.append(load_local_image_to_base64(lower_file))
    
    return result


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
