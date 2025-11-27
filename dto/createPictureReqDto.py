from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union, List
from core.enum import (
    SexEnum,
    CityEnum,
    ModeEnum,
    StyleEnum,
    MaterialEnum,
    ColorEnum,
    TypeEnum,
    ClothesCategory
)


class ClothesItem(BaseModel):
    """服装单品"""
    category: ClothesCategory = Field(..., description="服装类别：0-男上装、1-男下装、2-女上装、3-女下装、4-连衣裙")
    style_file_name: str = Field(..., description="样式文件名，对应 utils/pictures 下的文件名（不含扩展名）")
    style_name: Optional[str] = Field(None, description="样式显示名称")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "category": 0,
                    "style_file_name": "male_clothes",
                    "style_name": "男士上装款式1"
                },
                {
                    "category": 1,
                    "style_file_name": "male_pants",
                    "style_name": "男士裤装款式1"
                },
                {
                    "category": 2,
                    "style_file_name": "female_clothes",
                    "style_name": "女士上装款式1"
                },
                {
                    "category": 3,
                    "style_file_name": "female_pants",
                    "style_name": "女士裤装款式1"
                },
                {
                    "category": 4,
                    "style_file_name": "female_dress",
                    "style_name": "女士连衣裙款式1"
                }
            ]
        }


class Clothes(BaseModel):
    """
    服装配置（轻松模式使用）
    根据性别选择对应的上装和下装，或连衣裙
    style_file_name 对应 utils/pictures 目录下的文件名
    """
    items: List[ClothesItem] = Field(
        required=True, 
        min_length=1,
        max_length=3,
        description="服装列表，可包含上装、下装或连衣裙"
    )
    
    @field_validator('items')
    def validate_clothes_combination(cls, v):
        """验证服装组合的合法性"""
        if not v:
            raise ValueError("至少需要选择一件服装")
        
        categories = [item.category for item in v]
        
        # 检查是否有连衣裙
        has_dress = ClothesCategory.DRESS in categories
        has_male_top = ClothesCategory.MALE_TOP in categories
        has_male_bottom = ClothesCategory.MALE_BOTTOM in categories
        has_female_top = ClothesCategory.FEMALE_TOP in categories
        has_female_bottom = ClothesCategory.FEMALE_BOTTOM in categories
        
        # 连衣裙与上装下装互斥
        if has_dress and (has_male_top or has_male_bottom or has_female_top or has_female_bottom):
            raise ValueError("连衣裙不能与上装或下装同时选择")
        
        # 男装和女装不能混搭
        if (has_male_top or has_male_bottom) and (has_female_top or has_female_bottom):
            raise ValueError("男装和女装不能混搭")
        
        # 如果不是连衣裙，必须同时有上装和下装
        if not has_dress:
            if has_male_top and not has_male_bottom:
                raise ValueError("选择男上装必须同时选择男下装")
            if has_male_bottom and not has_male_top:
                raise ValueError("选择男下装必须同时选择男上装")
            if has_female_top and not has_female_bottom:
                raise ValueError("选择女上装必须同时选择女下装")
            if has_female_bottom and not has_female_top:
                raise ValueError("选择女下装必须同时选择女上装")
            if not (has_male_top or has_female_top):
                raise ValueError("非连衣裙模式下必须选择上装和下装")
        
        # 检查是否有重复的类别
        if len(categories) != len(set(categories)):
            raise ValueError("不能选择重复的服装类别")
        
        return v


class MasterModeTags(BaseModel):
    """大师模式标签配置"""
    style: Optional[StyleEnum] = Field(None, description="风格：0-法式优雅、1-日系简约、2-未来科技、3-AI随机匹配")
    material: Optional[MaterialEnum] = Field(None, description="材质：0-牛仔、1-丝绸、2-棉料、3-金属、4-AI随机匹配")
    color: Optional[ColorEnum] = Field(None, description="色调：0-暖色调、1-冷色调、2-中性色调、3-AI随机匹配")
    type: Optional[TypeEnum] = Field(None, description="类型：0-套装、1-连衣裙、2-外套、3-当地特色服饰、4-AI随机匹配")


class CreatePictureReqDto(BaseModel):
    """
    图片生图前端传的入参
    """
    
    originPicBase64: str = Field(
        required=True, 
        description="用户输入的原图Base64编码。格式：data:image/<format>;base64,<base64_data>，仅支持 jpeg、png 格式"
    )
    
    city: CityEnum = Field(
        required=True, 
        description="城市名称",
        examples=["巴黎", "东京", "纽约"]
    )
    
    sex: SexEnum = Field(
        required=True, 
        description="性别：0-男、1-女"
    )
    
    mode: ModeEnum = Field(
        required=True, 
        description="模式：0-轻松模式、1-大师模式"
    )
    
    clothes: Optional[Clothes] = Field(
        None,
        description="服装配置（轻松模式下必传，大师模式下忽略）"
    )
    
    master_mode_tags: Optional[MasterModeTags] = Field(
        None,
        description="大师模式标签配置（大师模式下可选，轻松模式下忽略）"
    )
    
    @field_validator('clothes')
    def validate_clothes_for_easy_mode(cls, v, info):
        """验证轻松模式下必须提供服装配置"""
        mode = info.data.get('mode')
        if mode == ModeEnum.EASY and v is None:
            raise ValueError("轻松模式下必须提供服装配置")
        return v
    @field_validator('master_mode_tags')
    def validate_master_mode_tags_for_master_mode(cls, v, info):
        """验证大师模式下必须提供标签配置"""
        mode = info.data.get('mode')
        if mode == ModeEnum.MASTER and v is None:
            raise ValueError("大师模式下必须提供标签配置")
        return v
    
    @model_validator(mode='after')
    def validate_sex_and_clothes(self):
        """验证性别和服装类别的匹配"""
        if self.mode == ModeEnum.EASY and self.clothes:
            categories = [item.category for item in self.clothes.items]
            
            # 男性只能选择男装
            if self.sex == SexEnum.MALE:
                has_female_clothes = any(
                    cat in [ClothesCategory.FEMALE_TOP, ClothesCategory.FEMALE_BOTTOM, ClothesCategory.DRESS] 
                    for cat in categories
                )
                if has_female_clothes:
                    raise ValueError("男性只能选择男上装和男下装")
            
            # 女性只能选择女装或连衣裙
            if self.sex == SexEnum.FEMALE:
                has_male_clothes = any(
                    cat in [ClothesCategory.MALE_TOP, ClothesCategory.MALE_BOTTOM] 
                    for cat in categories
                )
                if has_male_clothes:
                    raise ValueError("女性只能选择女上装、女下装或连衣裙")
        
        return self
        
    # 示范入参格式
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "originPicBase64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                    "city": 1,
                    "sex": 1,
                    "mode": 0,
                    "clothes": {
                        "items": [
                            {
                                "category": 2,
                                "style_file_name": "female_clothes",
                                "style_name": "女士法式上装"
                            },
                            {
                                "category": 3,
                                "style_file_name": "female_pants",
                                "style_name": "女士高腰阔腿裤"
                            }
                        ]
                    }
                },
                {
                    "originPicBase64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA...",
                    "city": 3,
                    "sex": 0,
                    "mode": 0,
                    "clothes": {
                        "items": [
                            {
                                "category": 0,
                                "style_file_name": "male_clothes",
                                "style_name": "男士上装"
                            },
                            {
                                "category": 1,
                                "style_file_name": "male_pants",
                                "style_name": "男士裤装"
                            }
                        ]
                    }
                }
            ]
        }
