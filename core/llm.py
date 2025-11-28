from collections.abc import AsyncGenerator
import json
from typing import Union
import time
import logging
import os
from typing import Optional, List
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel
from utils.image_utils import prepare_image_list_for_api
from setting import settings
from core.exceptions import (
    ErrorCode, 
    LLMException, 
    NetworkException, 
    TimeoutException, 
    AuthException,
    ParamException
) 


logger = logging.getLogger(__name__)

class LLMConf(BaseModel):
    """
    大模型配置
    """
    url: Optional[str] = None
    api_key: Optional[str] = None
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

    async def createPictureBySeedReam(self, InputImageList: List[str], SystemPrompt: str):
        """
        调用豆包生图接口，stream 图生图（使用 OpenAI SDK）
        input：
            InputImageList: 输入图片列表（Base64编码）
            SystemPrompt: 系统提示词
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
            model_id = settings.LLM_SCENE_ID or os.getenv('LLM_SCENE_ID')
            
            if not base_url or not api_key:
                error_msg = "LLM_URL 和 LLM_API_KEY 必须配置"
                logger.error(error_msg)
                logger.error(f"当前 LLM_URL: {base_url}, LLM_API_KEY: {'已配置' if api_key else '未配置'}")
                raise ParamException(
                    message=error_msg,
                    error_code=ErrorCode.PARAM_MISSING
                )
            
            if not model_id:
                error_msg = "LLM_SCENE_ID 必须配置（模型接入点ID）"
                logger.error(error_msg)
                raise ParamException(
                    message=error_msg,
                    error_code=ErrorCode.PARAM_MISSING
                )
            
            logger.info(f"  Base URL: {base_url}")
            logger.info(f"  API Key: {'已配置' if api_key else '未配置'}")
            logger.info(f"  Model ID: {model_id}")
            
            # 创建 OpenAI 客户端
            try:
                client = OpenAI(
                    base_url=base_url, 
                    api_key=api_key,
                    timeout=120.0,  # 图片生成可能需要较长时间
                )
                logger.info(" OpenAI 客户端创建成功")
            except Exception as e:
                logger.error(f"创建 OpenAI 客户端失败: {e}")
                raise 
        
            # 使用 OpenAI SDK 的 images.generate 接口
            # 豆包特有参数通过 extra_body 传递
            stream = client.images.generate(
                model=model_id,
                prompt=SystemPrompt,
                size="2K",
                response_format="b64_json",  # 使用 b64_json 格式接收 Base64 数据
                stream=True,
                extra_body={
                    "image": prepared_images,  # 输入图片
                    "watermark": False,
                    "sequential_image_generation": "auto",
                    "sequential_image_generation_options": {
                        "max_images": 4
                    }
                }
            )
            
            # 流式返回图片数据 - 直接 yield，不再收集到列表
            logger.info("开始接收流式响应...")
            event_count = 0
            for event in stream:
                event_count += 1
                if event is None:
                    logger.debug(f"Event {event_count}: None")
                    continue
                
                # 打印事件的完整结构用于调试
                logger.info(f"Event {event_count}: type={type(event).__name__}")
                logger.debug(f"Event {event_count} attributes: {dir(event)}")
                
                # OpenAI SDK 的流式响应结构
                event_type = getattr(event, 'type', None)
                logger.info(f"Event {event_count}: event_type={event_type}")
                
                if event_type == "image_generation.partial_failed":
                    error = getattr(event, 'error', None)
                    logger.error(f"Stream generate images error: {error}")
                    if error and getattr(error, 'code', None) == "InternalServiceError":
                        break
                        
                elif event_type == "image_generation.partial_succeeded":
                    # 图片生成成功，立即 yield
                    if hasattr(event, 'b64_json') and event.b64_json:
                        base64_data = event.b64_json
                        if not base64_data.startswith('data:image'):
                            base64_data = f"data:image/png;base64,{base64_data}"
                        logger.info(f"收到一张图片，size={len(base64_data)}")
                        # 直接返回一张
                        yield base64_data
                    elif hasattr(event, 'url') and event.url:
                        # URL 模式
                        size = getattr(event, 'size', 'unknown')
                        logger.info(f"recv.Size: {size}, recv.Url: {event.url}")
                        
                elif event_type == "image_generation.completed":
                    # 生成完成
                    logger.info("Final completed event")
                    if hasattr(event, 'usage'):
                        logger.info(f"recv.Usage: {event.usage}")
                else:
                    # 未知事件类型，尝试直接获取图片数据
                    logger.warning(f"Unknown event type: {event_type}")
                    if hasattr(event, 'b64_json') and event.b64_json:
                        base64_data = event.b64_json
                        if not base64_data.startswith('data:image'):
                            base64_data = f"data:image/png;base64,{base64_data}"
                        logger.info(f"Found b64_json in unknown event, yield it, size={len(base64_data)}")
                        yield base64_data
                    elif hasattr(event, 'data'):
                        logger.info(f"Found data in event: {type(event.data)}")
            
            logger.info(f"流式响应结束，共收到 {event_count} 个事件")
            
        except (ParamException, AuthException, LLMException, NetworkException, TimeoutException) as e:
            # 已经是自定义异常，直接抛出
            raise
        # 捕获其他异常
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"调用豆包生图接口失败")
            logger.error(f"  错误类型: {error_type}")
            logger.error(f"  错误信息: {error_msg}")
            
            # 根据错误类型抛出对应的自定义异常
            if "Connection" in error_type or "connection" in error_msg.lower():
                logger.error("  诊断: 网络连接错误")
                raise NetworkException(
                    message=f"网络连接失败: {error_msg}",
                    error_code=ErrorCode.NETWORK_ERROR
                )
            elif "401" in error_msg or "Unauthorized" in error_msg:
                logger.error("  诊断: 认证失败，请检查 API Key")
                raise AuthException(
                    message=f"API Key认证失败: {error_msg}",
                    error_code=ErrorCode.LLM_API_KEY_INVALID
                )
            elif "403" in error_msg or "Forbidden" in error_msg:
                logger.error("  诊断: 权限不足")
                raise AuthException(
                    message=f"权限不足: {error_msg}",
                    error_code=ErrorCode.AUTH_FORBIDDEN
                )
            elif "404" in error_msg or "Not Found" in error_msg:
                logger.error("  诊断: 模型不存在")
                raise LLMException(
                    message=f"模型不存在: {error_msg}",
                    error_code=ErrorCode.LLM_MODEL_NOT_FOUND
                )
            elif "timeout" in error_msg.lower():
                logger.error("  诊断: 请求超时")
                raise TimeoutException(
                    message=f"请求超时: {error_msg}",
                    error_code=ErrorCode.TIMEOUT_ERROR
                )
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                logger.error("  诊断: 配额已用尽")
                raise LLMException(
                    message=f"配额已用尽: {error_msg}",
                    error_code=ErrorCode.LLM_QUOTA_EXCEEDED
                )
            else:
                # 其他未知错误
                raise LLMException(
                    message=f"AI模型调用失败: {error_msg}",
                    error_code=ErrorCode.LLM_ERROR
                )
            

    async def close(self):
        """
        关闭客户端连接
        """
        await self.client.close()
