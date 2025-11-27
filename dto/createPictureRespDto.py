from pydantic import BaseModel, Field
from typing import List, Optional


class GeneratedImage(BaseModel):
    """单张生成的图片信息"""
    
    task_id: str = Field(
        required=True,
        description="任务ID"
    )
    
    image_index: int = Field(
        required=True,
        description="图片索引，1-4"
    )
    
    image_url: str = Field(
        required=True, 
        description="生成的图片URL（无水印）"
    )
    
    image_id: Optional[str] = Field(
        None,
        description="图片唯一标识ID"
    )
    
    thumbnail_url: Optional[str] = Field(
        None,
        description="缩略图URL"
    )
    
    width: Optional[int] = Field(
        None,
        description="图片宽度（像素）"
    )
    
    height: Optional[int] = Field(
        None,
        description="图片高度（像素）"
    )
    
    file_size: Optional[int] = Field(
        None,
        description="图片文件大小（字节）"
    )
    
    generation_time: Optional[float] = Field(
        None,
        description="该图片生成耗时（秒）"
    )
    
    status: str = Field(
        default="success",
        description="生成状态：success/failed"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="错误信息（如果失败）"
    )


class StreamImageResponse(BaseModel):
    """
    流式返回的单张图片响应
    每生成一张图片就返回一次
    """
    
    event_type: str = Field(
        required=True,
        description="事件类型：task_start/image_generated/task_complete/error"
    )
    
    data: Optional[GeneratedImage] = Field(
        None,
        description="图片数据（event_type=image_generated时有值）"
    )
    
    message: Optional[str] = Field(
        None,
        description="消息说明"
    )


class TaskStartResponse(BaseModel):
    """任务开始响应"""
    
    task_id: str = Field(
        required=True,
        description="任务ID"
    )
    
    total_images: int = Field(
        default=4,
        description="总共需要生成的图片数量"
    )
    
    city: str = Field(
        required=True,
        description="城市"
    )
    
    mode: int = Field(
        required=True,
        description="模式"
    )
    
    created_at: str = Field(
        required=True,
        description="任务创建时间"
    )


class CreatePictureRespDto(BaseModel):
    """
    图片生图返回给前端的参数（批量返回模式，兼容旧接口）
    四张无水印图片
    """
    
    task_id: str = Field(
        required=True,
        description="任务ID，用于追踪生成任务"
    )
    
    images: List[str] = Field(
        required=True,
        min_length=4,
        max_length=4,
        description="生成的四张无水印图片列表"
    )
    
    city: str = Field(
        required=True,
        description="生成图片对应的城市"
    )
    
    mode: int = Field(
        required=True,
        description="使用的模式：0-轻松模式、1-大师模式"
    )
    
    total_generation_time: Optional[float] = Field(
        None,
        description="总生成耗时（秒）"
    )
    
    created_at: Optional[str] = Field(
        None,
        description="创建时间"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "task_id": "task_20231127_abc123",
                    "images": [
                        {
                            "task_id": "task_20231127_abc123",
                            "image_index": 1,
                            "image_url": "https://cdn.example.com/generated/image1.jpg",
                            "image_id": "img_001",
                            "thumbnail_url": "https://cdn.example.com/generated/thumb1.jpg",
                            "generation_time": 3.2,
                            "status": "success"
                        },
                        {
                            "task_id": "task_20231127_abc123",
                            "image_index": 2,
                            "image_url": "https://cdn.example.com/generated/image2.jpg",
                            "image_id": "img_002",
                            "thumbnail_url": "https://cdn.example.com/generated/thumb2.jpg",
                            "generation_time": 2.8,
                            "status": "success"
                        },
                        {
                            "task_id": "task_20231127_abc123",
                            "image_index": 3,
                            "image_url": "https://cdn.example.com/generated/image3.jpg",
                            "image_id": "img_003",
                            "thumbnail_url": "https://cdn.example.com/generated/thumb3.jpg",
                            "generation_time": 3.5,
                            "status": "success"
                        },
                        {
                            "task_id": "task_20231127_abc123",
                            "image_index": 4,
                            "image_url": "https://cdn.example.com/generated/image4.jpg",
                            "image_id": "img_004",
                            "thumbnail_url": "https://cdn.example.com/generated/thumb4.jpg",
                            "generation_time": 3.1,
                            "status": "success"
                        }
                    ],
                    "city": "巴黎",
                    "mode": 0,
                    "total_generation_time": 12.6,
                    "created_at": "2023-11-27 15:23:45"
                }
            ]
        }