from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ImageItem(BaseModel):
    """单张图片信息"""
    
    id: int = Field(
        ...,
        description="图片索引ID（0-3）"
    )
    
    base64: str = Field(
        ..., 
        description="图片Base64编码（格式：data:image/jpeg;base64,...）"
    )


class CreatePictureResponse(BaseModel):
    """
    图片生成接口返回参数【同步】
    返回4张生成的图片Base64列表
    """
    
    images: List[ImageItem] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="生成的4张图片列表，每张图片包含索引ID和Base64编码"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "images": [
                        {
                            "id": 0,
                            "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
                        },
                        {
                            "id": 1,
                            "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
                        },
                        {
                            "id": 2,
                            "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
                        },
                        {
                            "id": 3,
                            "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
                        }
                    ]
                }
            ]
        }


# ==================== 流式响应相关 ====================

class StreamStatusEnum(str, Enum):
    """流式推送状态枚举"""
    GENERATING = "generating"  # 正在生成中（携带图片数据）
    COMPLETED = "completed"    # 全部完成
    FAILED = "failed"          # 发生错误


class ImageStreamEvent(BaseModel):
    """流式响应单项 DTO"""
    
    status: StreamStatusEnum = Field(
        ..., 
        description="当前推送状态：generating/completed/failed"
    )
    
    index: Optional[int] = Field(
        None, 
        description="图片索引(0-3)，仅 generating 状态有效"
    )
    
    base64: Optional[str] = Field(
        None, 
        description="图片Base64数据，仅 generating 状态有效"
    )
    
    message: Optional[str] = Field(
        None, 
        description="提示信息或错误信息"
    )
    
    def to_event_data(self) -> str:
        """
        转换为 SSE 事件数据格式
        exclude_none=True 去掉 null 字段，减少网络传输量
        """
        import json
        return f"data: {json.dumps(self.model_dump(mode='json', exclude_none=True))}\n\n"
    
    class Config:
        json_schema_extra = {
            "description": "流式推送的单个事件数据，通过 SSE 格式返回",
            "examples": [
                {
                    "description": "生成中 - 第1张图片",
                    "value": {
                        "status": "generating",
                        "index": 0,
                        "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "message": "success"
                    }
                },
                {
                    "description": "生成中 - 第2张图片",
                    "value": {
                        "status": "generating",
                        "index": 1,
                        "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "message": "success"
                    }
                },
                {
                    "description": "全部完成",
                    "value": {
                        "status": "completed",
                        "message": "生成流程结束，共生成 4 张图片"
                    }
                },
                {
                    "description": "生成失败",
                    "value": {
                        "status": "failed",
                        "message": "生成失败：参数验证错误"
                    }
                }
            ]
        }