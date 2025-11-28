# 提供 fastapi接口
from fastapi import FastAPI, HTTPException, Request, status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uvicorn
import asyncio
import json
from setting import settings, ENV
from core.llm import LLMModel
from core.llm import LLMConf
from model.createPictureReq import CreatePictureRequest
from model.createPictureResp import CreatePictureResponse
from service.generation_Image import DoubaoImages
from model.createPictureResp import ImageStreamEvent, StreamStatusEnum
from core.exceptions import CommonException

# 初始化日志
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI应用生命周期管理器
    替代旧的startup和shutdown事件处理器
    """
    # Startup逻辑
    logger.info("Journey Poster 服务正在启动...")
    
    try:
        logger.info(f"Journey Poster 服务启动 - 环境: {ENV}")
        
        # 验证关键配置
        logger.info(f"LLM_URL: {settings.LLM_URL}")
        logger.info(f"LLM_API_KEY: {'已配置' if settings.LLM_API_KEY else '未配置'}")
        logger.info(f"LLM_SCENE_ID: {settings.LLM_SCENE_ID}")
        
        # 初始化图片生成服务
        if settings.LLM_API_KEY and settings.LLM_URL:
            logger.info("火山豆包初始化成功")
        else:
            logger.warning("火山豆包配置不完整，请检查环境变量")
        
        logger.info("Journey Poster 服务启动完成")
        
        # 运行应用
        yield
        
    finally:
        # Shutdown逻辑
        logger.info("Journey Poster 服务正在关闭")
        
        try:
            # 清理资源
            logger.info("清理服务资源")
            
            # 这里可以添加需要清理的资源，比如关闭数据库连接、清理缓存等
            
            logger.info("Journey Poster 服务关闭完成")
        except Exception as e:
            logger.error(f"服务关闭时出错: {e}")

# 主应用程序
app = FastAPI(
    title="journey poster",
    description="年会AI-环球之旅",
    version="1.0.0",
    lifespan=lifespan  # 使用lifespan上下文管理器
)

# 统一响应处理函数
async def process_response(data: Dict[str, Any], status: int = 200, success: bool = True, message: Optional[str] = None) -> JSONResponse:
    """
    统一处理API响应
    
    Args:
        data: 待处理的响应数据
        status: HTTP状态码
        success: 响应是否成功
        message: 响应消息
        
    Returns:
        JSONResponse对象
    """
    return JSONResponse(
        status_code=status,
        content={
            "success": success,
            "status": status,
            "message": message or ("成功" if success else "失败"),
            "data": data
        }
    )

# CommonException 已移至 core.exceptions 模块，避免循环导入

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)

# 异常处理中间件
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except RequestValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })
        logger.error(f"参数验证错误: {str(e)}")
        return JSONResponse(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status": http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "参数验证失败",
                "data": {"detail": error_details}
            }
        )
    except HTTPException as e:
        logger.error(f"HTTP异常: {e.status_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "status": e.status_code,
                "message": e.detail,
                "data": None
            }
        )
    except CommonException as e:
        logger.error(f"自定义异常: {e.status} - {e.message}")
        return JSONResponse(
            status_code=e.status,
            content={
                "success": e.success,
                "status": e.status,
                "message": e.message,
                "data": e.data
            }
        )
    except Exception as e:
        logger.error(f"请求异常: {type(e).__name__}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "status": 500, "message": "服务器内部错误", "data": None}
        )



@app.get("/")
async def root():
    data = {"service": "journey poster service", "version": "1.0.0"}
    return await process_response(data, message="journey poster service 运行正常")


@app.get("/health", tags=["Health"])
async def health_check():
    logger.debug("Health check requested")
    data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    return await process_response(data, message="healthy")

@app.post("/createPicture", tags=["图生图接口"])
async def create_picture(CreatePictureRequest: CreatePictureRequest) -> CreatePictureResponse:
    """
    图片生图接口
    
    基于用户上传的原图和选择的参数，生成4张不同场景的图片。
    
    **参数说明：**
    - `originPicBase64`: 用户上传的原图，Base64编码格式（data:image/jpeg;base64,... 或 data:image/png;base64,...）
    - `city`: 城市枚举值（0-19，如0=东京、1=巴黎等）
    - `gender`: 性别（0=男、1=女）
    - `mode`: 模式（0=轻松模式、1=大师模式）
    - `clothes`: 轻松模式下必填，包含服装配置
    - `master_mode_tags`: 大师模式下必填，包含风格、材质、色调等标签
    
    **返回：**
    - 成功时返回4张生成的图片（Base64编码列表）
    - 失败时返回错误信息
    """
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # 1. 创建 LLM 配置并实例化
            llm_conf = LLMConf()
            return await DoubaoImages(llm_conf).create_picture(CreatePictureRequest)
            
        except Exception as e:
            logger.error(f"图生图接口异常, 第 {attempt + 1} 次尝试失败: {e}")
            if attempt == max_retries - 1:
                # 最后一次也没成功，抛出异常
                raise CommonException(message="图生图接口异常: " + str(e))
            
            # 等待一秒后重试
            await asyncio.sleep(1)
        
@app.post("/createPictureStream", tags=["图生图接口"])
async def create_picture_stream(CreatePictureRequest: CreatePictureRequest):
    """
    流式图片生成接口
    
    实时返回生成的图片，每生成一张就立即推送到前端。
    使用 Server-Sent Events (SSE) 格式返回。
    
    **入参：**
    - 与 /createPicture 接口相同
    
    **返回格式：**
    - Content-Type: text/event-stream
    - 每张图片作为一个 SSE 事件返回
    - 事件格式: 
      ```json
      // 生成中
      {"status": "generating", "index": 0, "base64": "data:image/...", "message": "success"}
      // 完成
      {"status": "completed", "message": "生成流程结束，共生成 4 张图片"}
      // 失败
      {"status": "failed", "message": "错误信息"}
      ```
    """
    async def generateImageStream():
        max_retries = 2
        for attempt in range(max_retries):
            try:
                llm_conf = LLMConf()
                # service 层已经封装了完整的状态推送（generating/completed/failed）
                async for chunk in DoubaoImages(llm_conf).create_picture_stream(CreatePictureRequest):
                    yield chunk
                return
            except Exception as e:
                logger.error(f"图生图SSE接口异常, 第 {attempt + 1} 次尝试失败: {e}")
                if attempt == max_retries - 1:
                    # 最后一次失败，发送 failed 状态
                    error_resp = ImageStreamEvent(
                        status=StreamStatusEnum.FAILED,
                        message=f"接口调用失败: {str(e)}"
                    )
                    yield error_resp.to_event_data()
                else:
                    await asyncio.sleep(1)
    
    return StreamingResponse(
        generateImageStream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    
    uvicorn.run(
        "journey_poster:app",
        host="localhost",
        port=8123,
        reload=False,  # 开发模式下启用热重载
        log_level="info"
    )
# uv run python journey_poster.py