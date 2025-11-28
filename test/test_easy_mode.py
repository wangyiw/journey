"""
测试轻松模式图片生成
使用多张输入图片，流式生成4张图片
"""
import asyncio
import base64
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
load_dotenv('.env.dev')

from core.llm import LLMModel, LLMConf
from core.prompt_strategy import generate_prompt_by_request
from core.enum import CityEnum, ModeEnum, GenderEnum, ClothesCategory
from dto.createPictureReqDto import (
    CreatePictureReqDto,
    ClothesItem,
    Clothes
)


def load_image_to_base64(image_path: str) -> str:
    """加载图片并转换为 Base64"""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"


async def test_easy_mode():
    """测试轻松模式"""
    print("=" * 60)
    print("测试轻松模式图片生成（多图输入）")
    print("=" * 60)
    
    # 1. 准备测试图片（可以使用多张图片）
    project_root = Path(__file__).parent.parent
    
    # 输入图片路径列表（可以添加多张图片）
    input_image_paths = [
        project_root / "utils" / "pictures" / "input_demo.jpeg",
        # 如果有第二张图片，可以添加：
        # project_root / "utils" / "pictures" / "input_demo2.jpeg",
    ]
    
    print("\n1. 加载输入图片:")
    image_base64_list = []
    for i, img_path in enumerate(input_image_paths, 1):
        if img_path.exists():
            image_base64 = load_image_to_base64(str(img_path))
            image_base64_list.append(image_base64)
            size_mb = len(image_base64) / (1024 * 1024)
            print(f"   图片 {i}: {img_path}")
            print(f"   大小: {size_mb:.2f}MB")
        else:
            print(f"   警告: 图片不存在 - {img_path}")
    
    if not image_base64_list:
        print("\n错误: 没有找到输入图片")
        return
    
    # 2. 构建轻松模式请求（使用新的 upperStyle 和 lowerStyle）
    print("\n2. 构建轻松模式请求:")
    
    # 准备服装数据（只需传入样式ID，后端自动加载图片）
    upper_style = 101  # 上装样式101
    lower_style = 201  # 下装样式201
    
    clothes = Clothes(
        upperStyle=upper_style,
        lowerStyle=lower_style,
        dress=None  # 男性不传连衣裙
    )
    
    print(f"   上装样式ID: {upper_style}")
    print(f"   下装样式ID: {lower_style}")
    print(f"   说明: 后端会根据性别({GenderEnum.MALE.name})和样式ID自动加载对应的服装图片")
    
    request = CreatePictureReqDto(
        originPicBase64=image_base64_list[0],  # 使用第一张图片作为原图
        mode=ModeEnum.EASY,
        city=CityEnum.Tokyo,
        sex=GenderEnum.MALE,
        clothes=clothes
    )
    
    print(f"   模式: {request.mode.value}")
    print(f"   城市: {request.city.value}")
    print(f"   性别: {request.sex.value}")
    print(f"   输入图片数量: {len(image_base64_list)}")
    print(f"   服装: 上装{upper_style} + 下装{lower_style}")
    
    # 3. 生成提示词
    print("\n3. 生成提示词:")
    prompt = generate_prompt_by_request(request)
    print(f"\n{prompt}\n")
    
    # 4. 使用服务层（会自动加载服装图片）
    print("4. 调用服务层生成图片:")
    print(f"   说明: 服务层会自动根据性别和样式ID加载服装图片")
    print(f"   Base URL: {os.getenv('LLM_URL')}")
    print(f"   API Key: {'已设置' if os.getenv('LLM_API_KEY') else '未设置'}")
    print(f"   Model ID: {os.getenv('LLM_SCENE_ID')}")
    print(f"   生成数量: 4 张")
    print(f"   响应格式: b64_json")
    print(f"   流式: True\n")
    
    try:
        # 使用服务层（推荐）
        from service.generation_Image import doubao_images
        
        print("5. 开始生成图片...")
        result = await doubao_images().createPicture(request)
        images_base64_list = result.images
        
        print(f"\n 生成完成，总计生成: {len(images_base64_list)} 张图片")
        
        # 6. 保存生成的图片
        if images_base64_list:
            print("\n6. 保存生成的图片:")
            output_dir = project_root / "utils" / "pictures" / "output"
            output_dir.mkdir(exist_ok=True)
            
            for i, img_base64 in enumerate(images_base64_list, 1):
                # 提取 Base64 数据
                if img_base64.startswith('data:image'):
                    base64_data = img_base64.split(',')[1]
                else:
                    base64_data = img_base64
                
                # 解码并保存
                image_bytes = base64.b64decode(base64_data)
                output_path = output_dir / f"easy_mode_output_{i}.png"
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                size_mb = len(image_bytes) / (1024 * 1024)
                print(f"   ✓ 图片 {i} 已保存: {output_path} ({size_mb:.2f}MB)")
        
        print("\n" + "=" * 60)
        print("✓ 测试成功完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_easy_mode_custom_prompt():
    """测试轻松模式（自定义提示词）"""
    print("=" * 60)
    print("测试轻松模式图片生成（自定义提示词）")
    print("=" * 60)
    
    # 1. 准备测试图片
    project_root = Path(__file__).parent.parent
    input_image_paths = [
        project_root / "utils" / "pictures" / "input_demo.jpeg",
    ]
    
    print("\n1. 加载输入图片:")
    image_base64_list = []
    for i, img_path in enumerate(input_image_paths, 1):
        if img_path.exists():
            image_base64 = load_image_to_base64(str(img_path))
            image_base64_list.append(image_base64)
            size_mb = len(image_base64) / (1024 * 1024)
            print(f"   图片 {i}: {img_path} ({size_mb:.2f}MB)")
    
    # 2. 自定义提示词
    custom_prompt = """
将用户人物从原图中进行干净、精细的抠图，保持人物五官特征、脸型轮廓、发型、肤色和整体形象高度一致。
增强脸部一致性，确保与原图相同的面部特征、比例与辨识度。
进行适度去除皮肤瑕疵，自然美颜但不过度，保持真实质感。

背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑（随机生成四种不同场景），使人物与背景自然融合：光影一致、色彩统一、景深协调，整体呈现照片级超写实风格。

人物服装：提供的服饰图片。

人物姿势可根据场景做自然变化，但必须保持合理的人体结构和正常比例。
整体风格：超写实、高清、自然色调、真实空气感、柔和氛围光。
一次性生成四张不同构图和场景的高清照片，供选择。
"""
    
    print("\n2. 使用自定义提示词:")
    print(custom_prompt)
    
    # 3. 调用 LLM
    print("\n3. 调用 LLM 生成图片...")
    try:
        llm_conf = LLMConf()
        llm_model = LLMModel(llm_conf)
        
        images_base64_list = await llm_model.createPictureBySeedReam(
            InputImageList=image_base64_list,
            prompt=custom_prompt
        )
        
        print(f"\n✓ 生成完成，总计生成: {len(images_base64_list)} 张图片")
        
        # 4. 保存图片
        if images_base64_list:
            print("\n4. 保存生成的图片:")
            output_dir = project_root / "utils" / "pictures" / "output"
            output_dir.mkdir(exist_ok=True)
            
            for i, img_base64 in enumerate(images_base64_list, 1):
                if img_base64.startswith('data:image'):
                    base64_data = img_base64.split(',')[1]
                else:
                    base64_data = img_base64
                
                image_bytes = base64.b64decode(base64_data)
                output_path = output_dir / f"easy_mode_custom_{i}.png"
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                size_mb = len(image_bytes) / (1024 * 1024)
                print(f"   ✓ 图片 {i} 已保存: {output_path} ({size_mb:.2f}MB)")
        
        print("\n" + "=" * 60)
        print("✓ 测试成功完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n请选择测试模式:")
    print("1. 使用策略生成提示词（推荐）")
    print("2. 使用自定义提示词")
    
    choice = input("\n请输入选项 (1/2，默认为1): ").strip() or "1"
    
    if choice == "1":
        asyncio.run(test_easy_mode())
    elif choice == "2":
        asyncio.run(test_easy_mode_custom_prompt())
    else:
        print("无效的选项")
