from collections.abc import AsyncGenerator
import json
from typing import Union
import time
import logging
import os
from typing import Optional, List
from openai import AsyncOpenAI
from pydantic import BaseModel
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions
from utils.image_utils import prepare_image_list_for_api
from setting import settings 


logger = logging.getLogger(__name__)

class LLMConf(BaseModel):
    """
    大模型配置
    """

    scene_id: Optional[str] = None
    stream_timeout: Optional[int] = None
    post_timeout: Optional[int] = None

class LLMModel:
    """
    LLM 模型调用类，基于 OpenAI 实现
    """

    def __init__(self, conf: LLMConf):
        """
        初始化 LLM 模型

        Args:
            conf: LLM 配置

        Raises:
            ValueError: 当 api_key 无效且环境变量也未设置时抛出
        """
        self.conf = conf
        # 构建默认 headers
        headers = {"Content-Type": "application/json"}
        # 如果有 scene_id，添加到 headers 中
        if conf.scene_id:
            headers["sceneId"] = conf.scene_id

        # 确保 api_key 有效：优先使用配置中的 api_key，如果为 None 或空字符串则尝试从环境变量获取
        api_key = (conf.api_key or "").strip() or os.getenv("OPENAI_API_KEY", "").strip()


        self.client = AsyncOpenAI(base_url=conf.url, api_key=api_key, timeout=30.0, default_headers=headers)

    async def generate(
        self, prompt: str, model_name: str, stream: bool = False, **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        生成文本

        Args:
            prompt: 提示词
            model_name: 大模型名称
            stream: 是否使用流式输出
            **kwargs: 其他参数

        Returns:
            str 或 AsyncGenerator[str, None]: 生成的文本或文本流

        Raises:
            Exception: 调用失败时抛出
        """
        start_time = time.time()
        logger.info(f"开始调用 LLM 生成接口, 模型: {model_name}, 流式: {stream}, Prompt长度: {len(prompt)}")
        try:
            messages = [{"role": "user", "content": prompt}]

            response = await self.client.chat.completions.create(
                model=model_name, messages=messages, stream=stream, **kwargs
            )

            if stream:

                async def stream_generator():
                    async for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content

                logger.info(f"LLM 生成接口返回流式响应")
                return stream_generator()
            else:
                elapsed_time = time.time() - start_time
                usage = response.usage
                logger.info(
                    f"LLM 生成成功, 模型: {model_name}, "
                    f"耗时: {elapsed_time:.2f}s, "
                    f"Tokens: 提示词={usage.prompt_tokens}, "
                    f"生成={usage.completion_tokens}, "
                    f"总计={usage.total_tokens}"
                )
                return response.choices[0].message.content
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"LLM 生成失败, 模型: {model_name}, 耗时: {elapsed_time:.2f}s, 错误: {str(e)}"
            logger.error(error_msg)
            logger.error(e, error_msg)
            raise

    async def chat(
        self, messages: list[dict[str, str]], model_name: str, stream: bool = False, **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        对话生成

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model_name: 大模型名称
            stream: 是否使用流式输出
            **kwargs: 其他参数

        Returns:
            str 或 AsyncGenerator[str, None]: 生成的回复或回复流

        Raises:
            Exception: 调用失败时抛出
        """
        start_time = time.time()
        logger.info(f"开始调用 LLM 对话接口, 模型: {model_name}, 流式: {stream}, 消息数: {len(messages)}")
        try:
            response = await self.client.chat.completions.create(
                model=model_name, messages=messages, stream=stream, **kwargs
            )

            if stream:

                async def stream_generator():
                    async for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content

                logger.info(f"LLM 对话接口返回流式响应")
                return stream_generator()
            else:
                elapsed_time = time.time() - start_time
                usage = response.usage
                logger.info(
                    f"LLM 对话成功, 模型: {model_name}, "
                    f"耗时: {elapsed_time:.2f}s, "
                    f"Tokens: 提示词={usage.prompt_tokens}, "
                    f"生成={usage.completion_tokens}, "
                    f"总计={usage.total_tokens}"
                )
                return response.choices[0].message.content

        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"LLM 对话失败, 模型: {model_name}, 耗时: {elapsed_time:.2f}s, 错误: {str(e)}"
            logger.error(error_msg)
            logger.error(e, error_msg)
            raise

    async def createPictureBySeedReam(self, InputImageList: List[str], prompt: str) -> List[str]:
        """
        调用豆包生图接口，stream 图生图
        input：
            InputImageList: 输入图片列表（Base64编码）
            prompt: 提示词
        output:
            List[str]: 生成的四张图片 Base64 编码列表
            
        图片格式要求：
            - Base64格式：data:image/<format>;base64,<base64_data>
            - 仅支持 jpeg、png 格式
            - 支持单图或多图输入（多图融合）
        """
        try:
            # 准备图片输入（单图返回字符串，多图返回列表）
            prepared_images = prepare_image_list_for_api(InputImageList)
            
            # 使用 settings 配置，如果没有则从环境变量读取（兼容测试文件）
            base_url = settings.LLM_URL or os.getenv('LLM_URL')
            api_key = settings.LLM_API_KEY or os.getenv('LLM_API_KEY')
            
            if not base_url or not api_key:
                error_msg = "LLM_URL 和 LLM_API_KEY 必须配置"
                logger.error(error_msg)
                logger.error(f"当前 LLM_URL: {base_url}, LLM_API_KEY: {'已配置' if api_key else '未配置'}")
                raise ValueError(error_msg)
            
            # 验证 Base URL 格式
            if 'api.deepseek.com' in base_url:
                logger.warning(f"⚠️  检测到 DeepSeek URL，豆包 API 应该是: https://ark.{{region}}.volces.com/api/v3")
            
            logger.info(f"调用豆包生图接口")
            logger.info(f"  Base URL: {base_url}")
            logger.info(f"  API Key: {'已配置 (长度: ' + str(len(api_key)) + ')' if api_key else '未配置'}")
            
            # 创建 Ark 客户端，添加超时配置
            try:
                client = Ark(
                    base_url=base_url, 
                    api_key=api_key,
                    timeout=120.0,  # 图片生成可能需要较长时间
                )
                logger.info("✓ Ark 客户端创建成功")
            except Exception as e:
                logger.error(f"✗ 创建 Ark 客户端失败: {e}")
                raise 
        
            # 使用 b64_json 格式接收 Base64 数据
            stream = client.images.generate( 
                model="doubao-seedream-4-0-250828", 
                prompt=prompt,
                image=prepared_images,
                size="2K",
                sequential_image_generation="auto",
                sequential_image_generation_options=SequentialImageGenerationOptions(max_images=4),
                response_format="b64_json",  # 使用 b64_json 格式接收 Base64 数据
                stream=True,
                watermark=False
            )
            
            # 收集流式返回的图片数据
            images_base64_list = []
            partial_images = {}  # 用于存储部分图片数据 {index: base64_data}
            
            # 遍历流式响应
            for event in stream:
                if event is None:
                    continue
                    
                if event.type == "image_generation.partial_failed":
                    logger.error(f"Stream generate images error: {event.error}")
                    if event.error is not None and event.error.code == "InternalServiceError":
                        break
                        
                elif event.type == "image_generation.partial_succeeded":
                    # 图片生成成功（URL 模式）
                    if event.error is None and hasattr(event, 'url') and event.url:
                        logger.info(f"recv.Size: {event.size}, recv.Url: {event.url}")
                        
                elif event.type == "image_generation.partial_image":
                    # 接收部分图片的 Base64 数据
                    if hasattr(event, 'b64_json') and event.b64_json:
                        index = event.partial_image_index
                        logger.info(f"Partial image index={index}, size={len(event.b64_json)}")
                        partial_images[index] = event.b64_json
                        
                elif event.type == "image_generation.completed":
                    # 生成完成
                    if event.error is None:
                        logger.info("Final completed event")
                        if hasattr(event, 'usage'):
                            logger.info(f"recv.Usage: {event.usage}")
            
            # 按索引顺序整理图片数据
            if partial_images:
                # 从流式响应中收集的 Base64 数据
                for i in sorted(partial_images.keys()):
                    base64_data = partial_images[i]
                    # 确保格式为 data:image/png;base64,<data>
                    if not base64_data.startswith('data:image'):
                        base64_data = f"data:image/png;base64,{base64_data}"
                    images_base64_list.append(base64_data)
            else:
                # 如果流式响应没有数据，尝试从 stream.data 获取
                if hasattr(stream, 'data') and stream.data:
                    for image in stream.data:
                        if hasattr(image, 'b64_json') and image.b64_json:
                            base64_data = image.b64_json
                            if not base64_data.startswith('data:image'):
                                base64_data = f"data:image/png;base64,{base64_data}"
                            images_base64_list.append(base64_data)
                            logger.info(f"Image size: {len(base64_data)}")
            
            if len(images_base64_list) != 4:
                logger.warning(f"期望生成4张图片，实际生成{len(images_base64_list)}张")
            
            return images_base64_list
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"调用豆包生图接口失败")
            logger.error(f"  错误类型: {error_type}")
            logger.error(f"  错误信息: {error_msg}")
            
            # 提供更详细的错误诊断
            if "Connection" in error_type or "connection" in error_msg.lower():
                logger.error("  诊断: 连接错误，可能原因：")
                logger.error("    1. Base URL 配置错误（应该是 https://ark.{region}.volces.com/api/v3）")
                logger.error("    2. 网络不通或需要代理")
                logger.error("    3. API Key 无效")
                logger.error("    4. 防火墙阻止")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                logger.error("  诊断: 认证失败，请检查 API Key 是否正确")
            elif "403" in error_msg or "Forbidden" in error_msg:
                logger.error("  诊断: 权限不足，请检查 API Key 是否有调用权限")
            elif "timeout" in error_msg.lower():
                logger.error("  诊断: 请求超时，可能需要增加超时时间或检查网络")
            
            raise Exception(f"调用豆包生图接口失败: {error_type}: {error_msg}")
            

    async def close(self):
        """
        关闭客户端连接
        """
        await self.client.close()
