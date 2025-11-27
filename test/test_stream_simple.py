"""
简单测试流式图片生成功能（固定 prompt 和 image）
"""
import asyncio
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env.dev')

from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions


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
    
    # 3. 调用豆包 API
    print("3. 调用豆包生图 API")
    print(f"   - Base URL: {os.getenv('LLM_URL')}")
    print(f"   - API Key: {'已设置' if os.getenv('LLM_API_KEY') else '未设置'}")
    print(f"   - 模型: doubao-seedream-4-0-250828")
    print(f"   - 生成数量: 4 张")
    print(f"   - 响应格式: b64_json")
    print(f"   - 流式: True\n")

    MODEL_ENDPOINT_ID = "ep-m-20251127211119-7fbfh"
    
    try:
        client = Ark(
            base_url=os.getenv('LLM_URL'),
            api_key=os.getenv('LLM_API_KEY'),
        )
        
        # 流式生成
        stream = client.images.generate(
            model=MODEL_ENDPOINT_ID,
            prompt=test_prompt,
            image=image_base64,  # 单图输入
            size="2K",
            sequential_image_generation="auto",
            sequential_image_generation_options=SequentialImageGenerationOptions(max_images=4),
            response_format="b64_json",
            stream=True,
            watermark=False
        )
        
        # 收集流式响应
        print("4. 接收流式响应（SSE格式）:")
        print("=" * 60)
        images_base64_list = []
        partial_images = {}
        
        import json
        
        for event in stream:
            if event is None:
                continue
            
            # 打印 SSE 格式的输出
            event_type = event.type
            print(f"event: {event_type}")
            
            # 构建数据对象
            event_data = {
                "type": event_type,
                "model": getattr(event, 'model', MODEL_ENDPOINT_ID),
                "created": getattr(event, 'created', None),
            }
            
            # 根据事件类型添加特定字段
            if event_type in ["image_generation.partial_succeeded", "image_generation.succeeded"]:
                # 获取图片索引
                image_index = getattr(event, 'image_index', getattr(event, 'index', None))
                if image_index is not None:
                    event_data["image_index"] = image_index
                
                # URL 模式
                if hasattr(event, 'url') and event.url:
                    event_data["url"] = event.url
                    if hasattr(event, 'size'):
                        event_data["size"] = event.size
                    print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                    print()  # 空行分隔
                
                # Base64 模式
                elif hasattr(event, 'b64_json') and event.b64_json:
                    # Base64 数据太长，只显示元数据，不显示完整 base64
                    event_data["image_index"] = image_index if image_index is not None else len(images_base64_list)
                    event_data["b64_json"] = f"[Base64数据，长度: {len(event.b64_json)}]"
                    if hasattr(event, 'size'):
                        event_data["size"] = event.size
                    print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                    print()  # 空行分隔
                    
                    # 保存 Base64 数据
                    images_base64_list.append(event.b64_json)
            
            elif event_type == "image_generation.partial_image":
                # 部分图片数据
                if hasattr(event, 'b64_json') and event.b64_json:
                    index = getattr(event, 'partial_image_index', getattr(event, 'image_index', None))
                    event_data["image_index"] = index
                    event_data["b64_json"] = f"[Base64数据，长度: {len(event.b64_json)}]"
                    print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                    print()  # 空行分隔
                    partial_images[index] = event.b64_json
            
            elif event_type == "image_generation.completed":
                # 完成事件
                if hasattr(event, 'usage'):
                    event_data["usage"] = {
                        "generated_images": getattr(event.usage, 'generated_images', None),
                        "output_tokens": getattr(event.usage, 'output_tokens', None),
                        "total_tokens": getattr(event.usage, 'total_tokens', None),
                    }
                print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                print()  # 空行分隔
            
            elif event_type in ["image_generation.failed", "image_generation.partial_failed"]:
                # 失败事件
                if hasattr(event, 'error') and event.error:
                    event_data["error"] = {
                        "code": getattr(event.error, 'code', None),
                        "message": getattr(event.error, 'message', str(event.error)),
                    }
                print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                print()  # 空行分隔
            
            else:
                # 其他事件类型
                print(f"data: {json.dumps(event_data, ensure_ascii=False)}")
                print()  # 空行分隔
        
        # 打印结束标记
        print("data: [DONE]")
        print("=" * 60)
        
        # 如果 partial_images 里有数据，合并到主列表
        if partial_images and not images_base64_list:
            for i in sorted(partial_images.keys()):
                images_base64_list.append(partial_images[i])
        
        print(f"\n总计生成: {len(images_base64_list)} 张图片")
        
        # 6. 保存图片
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
                print(f"  图片 {i} 已保存: {output_path} ({size_mb:.2f}MB)")
        
        print("\n" + "=" * 60)
        print("测试成功完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple())
