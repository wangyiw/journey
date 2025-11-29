from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union, List
from core.enum import (
    GenderEnum,
    CityEnum,
    ModeEnum,
    StyleEnum,
    MaterialEnum,
    ColorEnum,
    TypeEnum,
    ClothesCategory
)


class Clothes(BaseModel):
    """
    服装参数配置（轻松模式下必传,大师模式下忽略）
    参数说明：
    - upperStyle: 上装样式字符串标识（如 male_upper_01, female_upper_01），前端显示为【男上装】或【女上装】标签
    - lowerStyle: 下装样式字符串标识（如 male_lower_01, female_lower_01），前端显示为【男下装】或【女下装】标签
    - dress: 连衣裙样式字符串标识（如 female_dress_01），前端显示为【连衣裙】标签（仅女性）
    
    使用规则：
    - 男性：必须同时传 upperStyle 和 lowerStyle，不能传 dress
    - 女性：可以传 upperStyle + lowerStyle，或只传 dress（二选一）
    
    示例：
    - 男性选择【男上装】样式1 + 【男下装】样式1：{"upperStyle": "male_upper_01", "lowerStyle": "male_lower_01", "dress": null}
    - 女性选择【女上装】样式2 + 【女下装】样式2：{"upperStyle": "female_upper_01", "lowerStyle": "female_lower_01", "dress": null}
    - 女性选择【连衣裙】样式1：{"upperStyle": null, "lowerStyle": null, "dress": "female_dress_01"}
    """
    upperStyle: Optional[str] = Field(
        None,
        description="上装样式字符串标识（如 male_upper_01, female_upper_01），对应后端服装图片"
    )
    lowerStyle: Optional[str] = Field(
        None,
        description="下装样式字符串标识（如 male_lower_01, female_lower_01），对应后端服装图片"
    )
    dress: Optional[str] = Field(
        None,
        description="连衣裙样式字符串标识（如 female_dress_01），对应后端服装图片，仅女性可用"
    )
    
    @model_validator(mode='after')
    def validate_clothes_combination(self):
        """验证服装组合的合法性"""
        has_upper = self.upperStyle is not None
        has_lower = self.lowerStyle is not None
        has_dress = self.dress is not None
        
        # 必须至少选择一种
        if not (has_upper or has_lower or has_dress):
            raise ValueError("至少需要选择一种服装（上装、下装或连衣裙）")
        
        # 连衣裙与上装下装互斥
        if has_dress and (has_upper or has_lower):
            raise ValueError("连衣裙不能与上装或下装同时选择")
        
        # 非连衣裙模式下，必须同时有上装和下装
        if not has_dress:
            if has_upper and not has_lower:
                raise ValueError("选择上装必须同时选择下装")
            if has_lower and not has_upper:
                raise ValueError("选择下装必须同时选择上装")
        
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "upperStyle": "male_upper_01",
                    "lowerStyle": "male_lower_01",
                    "dress": None
                },
                {
                    "upperStyle": None,
                    "lowerStyle": None,
                    "dress": "female_dress_01"
                }
            ]
        }


class MasterModeTags(BaseModel):
    """大师模式标签配置"""  
    style: Optional[StyleEnum] = Field(None, description="风格：FrenchElegant-法式优雅、JapaneseSimple-日系简约、FutureTech-未来科技、AIRandom-AI随机匹配")
    material: Optional[MaterialEnum] = Field(None, description="材质：Cotton-牛仔、Silk-丝绸、Cotton-棉料、Metal-金属、AIRandom-AI随机匹配")
    color: Optional[ColorEnum] = Field(None, description="色调：WarmTone-暖色调、ColdTone-冷色调、NeutralTone-中性色调、AIRandom-AI随机匹配")
    type: Optional[TypeEnum] = Field(None, description="类型：Set-套装、Dress-连衣裙、Coat-外套、Local-当地特色服饰、AIRandom-AI随机匹配")


class CreatePictureRequest(BaseModel):
    """
    图片生图前端传的模式标签入参
    """
    
    # 设置为可选，后端 Controller 接到 File 手动注入进去。
    originPicBase64: Optional[str] = Field(
        None,
        description="后端内部使用：从上传文件转换来的Base64，前端无需传递"
    )
    
    city: CityEnum = Field(
        ..., 
        description="城市名称",
        examples=["巴黎", "东京", "纽约"]
    )
    
    gender: GenderEnum = Field(
        ..., 
        description="性别：0-男、1-女"
    )
    
    mode: ModeEnum = Field(
        ..., 
        description="模式：0-轻松模式、1-大师模式"
    )
    
    clothes: Optional[Clothes] = Field(
        None,
        description="服装配置（轻松模式下必传，大师模式下忽略） "
    )
    
    master_mode_tags: Optional[MasterModeTags] = Field(
        None,
        description="大师模式标签配置（大师模式下可选，轻松模式下忽略）"
    )
    
    @field_validator('clothes')
    def validate_clothes_for_easy_mode(cls, v, info):
        """验证轻松模式下必须提供服装配置"""
        mode = info.data.get('mode')
        if mode == ModeEnum.Easy and v is None:
            raise ValueError("轻松模式下必须提供服装配置")
        return v
    @field_validator('master_mode_tags')
    def validate_master_mode_tags_for_master_mode(cls, v, info):
        """验证大师模式下必须提供标签配置"""
        mode = info.data.get('mode')
        if mode == ModeEnum.Master and v is None:
            raise ValueError("大师模式下必须提供标签配置")
        return v
    
    @model_validator(mode='after')
    def validate_gender_and_clothes(self):
        """验证性别和服装类别的匹配"""
        if self.mode == ModeEnum.Easy and self.clothes:
            # 男性：只能选择上装+下装
            if self.gender == GenderEnum.Male:
                if self.clothes.dress is not None:
                    raise ValueError("男性不能选择连衣裙")
                if self.clothes.upperStyle is None or self.clothes.lowerStyle is None:
                    raise ValueError("男性必须同时选择上装和下装")
                # 男性不能选择连衣裙类型
                if self.master_mode_tags.type == TypeEnum.Dress:
                    raise ValueError("男性不能选择连衣裙类型")
            
            # 女性：可以选择上装+下装 或 连衣裙（二选一）
            if self.gender == GenderEnum.Female:
                has_dress = self.clothes.dress is not None
                has_upper_lower = self.clothes.upperStyle is not None or self.clothes.lowerStyle is not None
                
                # 连衣裙和上装下装不能同时选择
                if has_dress and has_upper_lower:
                    raise ValueError("女性不能同时选择连衣裙和上装下装")
                
                # 如果选择上装下装，必须同时选择
                if has_upper_lower and not has_dress:
                    if self.clothes.upperStyle is None or self.clothes.lowerStyle is None:
                        raise ValueError("女性选择上装下装时，必须同时选择上装和下装")
        
        return self
        
    # 示范入参格式
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "city": "Tokyo",
                    "gender": "Male",
                    "mode": "Easy",
                    "clothes": {
                        "upperStyle": "male_upper_01",
                        "lowerStyle": "male_lower_01",
                        "dress": None
                    }
                },
                {
                    "city": "Paris",
                    "gender": "Female",
                    "mode": "Easy",
                    "clothes": {
                        "upperStyle": "female_upper_01",
                        "lowerStyle": "female_lower_01",
                        "dress": None
                    }
                },
                {
                    "city": "Paris",
                    "gender": "Female",
                    "mode": "Master",
                    "master_mode_tags": {
                        "style": "FrenchElegant",
                        "material": "Silk",
                        "color": "Neutral",
                        "type": "Suit"
                    }
                }
            ]
        }
