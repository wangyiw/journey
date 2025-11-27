"""
测试流式图片生成功能
"""
import asyncio
import base64
import os
from pathlib import Path
from core.llm import LLMModel
from core.prompt import BASE_PROMPT_TEMPLATE, CITY_SCENES, CLOTHING_TEMPLATES


def load_image_as_base64(image_path: str) -> str:
    """
    加载本地图片并转换为 Base64 编码
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        str: Base64 编码的图片字符串
    """
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    base64_data = base64.b64encode(image_data).decode('utf-8')
    
    # 根据文件扩展名确定图片格式
    ext = Path(image_path).suffix.lower()
    if ext in ['.jpg', '.jpeg']:
        format_type = 'jpeg'
    elif ext == '.png':
        format_type = 'png'
    else:
        format_type = 'jpeg'
    
    return f"data:image/{format_type};base64,{base64_data}"


def build_test_prompt() -> str:
    """
    构建测试用的提示词
    
    Returns:
        str: 完整的提示词
    """
    # 使用东京场景
    tokyo_scene = CITY_SCENES["Tokyo"]
    scene_description = tokyo_scene["scene_description"]
    
    # 使用轻松模式的服装描述
    clothing_description = CLOTHING_TEMPLATES["easy_mode"]
    
    # 拼接完整提示词
    prompt = BASE_PROMPT_TEMPLATE.format(
        scene_description=scene_description,
        clothing_description=clothing_description
    )
    
    return prompt


async def test_stream_image_generation():
    """
    测试流式图片生成
    """
    print("=" * 60)
    print("开始测试流式图片生成功能")
    print("=" * 60)
    
    # 1. 加载测试图片
    image_path = r"d:\didaCode\journey\utils\pictures\input_demo.jpeg"
    print(f"\n1. 加载测试图片: {image_path}")
    
    try:
        image_base64 = load_image_as_base64(image_path)
        image_size_mb = len(image_base64) / (1024 * 1024)
        print(f"   ✓ 图片加载成功，Base64 大小: {image_size_mb:.2f}MB")
    except Exception as e:
        print(f"   ✗ 图片加载失败: {e}")
        return
    
    # 2. 构建测试提示词
    print("\n2. 构建测试提示词")
    test_prompt = build_test_prompt()
    print(f"   ✓ 提示词长度: {len(test_prompt)} 字符")
    print(f"   提示词预览（前200字符）:\n   {test_prompt[:200]}...")
    
    # 3. 调用流式生成接口
    print("\n3. 调用流式图片生成接口")
    print("   请求参数:")
    print(f"   - 模型: doubao-seedream-4-0-250828")
    print(f"   - 图片数量: 4")
    print(f"   - 响应格式: b64_json")
    print(f"   - 流式: True")
    
    try:
        llm_model = LLMModel()
        
        # 调用流式生成方法
        print("\n   开始生成图片...")
        result_images = await llm_model.createPictureBySeedReam(
            InputImageList=[image_base64],
            prompt=test_prompt
        )
        
        # 4. 输出结果
        print("\n4. 生成结果")
        print(f"   ✓ 成功生成 {len(result_images)} 张图片")
        
        for i, img_base64 in enumerate(result_images, 1):
            img_size_mb = len(img_base64) / (1024 * 1024)
            print(f"   图片 {i}: Base64 大小 {img_size_mb:.2f}MB")
            print(f"   前缀: {img_base64[:50]}...")
        
        # 5. 保存生成的图片（可选）
        print("\n5. 保存生成的图片")
        output_dir = Path(r"d:\didaCode\journey\utils\pictures\output")
        output_dir.mkdir(exist_ok=True)
        
        for i, img_base64 in enumerate(result_images, 1):
            # 提取 Base64 数据
            if img_base64.startswith('data:image'):
                base64_data = img_base64.split(',')[1]
            else:
                base64_data = img_base64
            
            # 解码并保存
            image_bytes = base64.b64decode(base64_data)
            output_path = output_dir / f"generated_{i}.png"
            
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"   ✓ 图片 {i} 已保存: {output_path}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n   ✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_stream_image_generation())
