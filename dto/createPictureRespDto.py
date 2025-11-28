from pydantic import BaseModel, Field
from typing import List


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


class CreatePictureRespDto(BaseModel):
    """
    图片生成接口返回参数
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