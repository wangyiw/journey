"""
简单测试流式图片生成功能
使用 LLMModel.createPictureBySeedReam 方法
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


def load_image_as_base64(image_path: str) -> str:
    """加载本地图片并转换为 Base64 编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    base64_data = base64.b64encode(image_data).decode('utf-8')
    ext = Path(image_path).suffix.lower()
    format_type = 'jpeg' if ext in ['.jpg', '.jpeg'] else 'png'
    
    return f"data:image/{format_type};base64,{base64_data}"


async def test_simple():
    """简单测试"""
    print("=" * 60)
    print("简单测试流式图片生成")
    print("=" * 60)
    
    # 1. 固定的测试提示词
    test_prompt = """
一位亚洲男性，自然美颜，真实质感。
背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑（随机生成四种不同场景），使人物与背景自然融合：光影一致、色彩统一、景深协调，整体呈现照片级超写实风格。

人物服装：提供的服饰图片。

人物姿势可根据场景做自然变化，但必须保持合理的人体结构和正常比例。
整体风格：超写实、高清、自然色调、真实空气感、柔和氛围光。
一次性生成四张不同构图和场景的高清照片，供选择。
"""
    
    print(f"\n1. 测试提示词:\n{test_prompt}\n")
    
    # 2. 加载测试图片
    # 使用相对路径，基于项目根目录
    project_root = Path(__file__).parent.parent
    image_path = project_root / "utils" / "pictures" / "input_demo.jpeg"
    print(f"2. 加载测试图片: {image_path}")
    
    try:
        image_base64 = load_image_as_base64(image_path)
        image_size_mb = len(image_base64) / (1024 * 1024)
        print(f"   图片加载成功，大小: {image_size_mb:.2f}MB\n")
    except Exception as e:
        print(f"   图片加载失败: {e}")
        return
    
    # 3. 调用 LLMModel 的 createPictureBySeedReam 方法
    print("3. 调用 LLMModel.createPictureBySeedReam 方法")
    print(f"   - Base URL: {os.getenv('LLM_URL')}")
    print(f"   - API Key: {'已设置' if os.getenv('LLM_API_KEY') else '未设置'}")
    print(f"   - Model ID: {os.getenv('LLM_SCENE_ID')}")
    print(f"   - 生成数量: 4 张")
    print(f"   - 响应格式: b64_json")
    print(f"   - 流式: True\n")
    
    try:
        # 创建 LLMModel 实例（使用空配置，从环境变量读取）
        llm_conf = LLMConf()
        llm_model = LLMModel(llm_conf)
        
        # 调用生图方法
        print("4. 调用生图接口...")
        images_base64_list = await llm_model.createPictureBySeedReam(
            InputImageList=[image_base64],
            prompt=test_prompt
        )
        
        print(f"\n✓ 生成完成，总计生成: {len(images_base64_list)} 张图片")
        
        # 5. 保存图片
        if images_base64_list:
            print("\n5. 保存生成的图片:")
            project_root = Path(__file__).parent.parent
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
                output_path = output_dir / f"test_output_{i}.png"
                
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
    asyncio.run(test_simple())
