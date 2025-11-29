from abc import ABC, abstractmethod
from typing import Dict, Any
from core.prompt import BASE_PROMPT_TEMPLATE, CITY_SCENES, CLOTHING_TEMPLATES
from core.enum import ModeEnum, StyleEnum, MaterialEnum, ColorEnum, TypeEnum, CityEnum
from model.createPictureReq import CreatePictureRequest


class PromptStrategy(ABC):
    """提示词生成策略基类"""
    
    @abstractmethod
    def generate_prompt(self, request_dto: CreatePictureRequest) -> str:
        """生成提示词"""
        pass
    
    def _get_city_scene_description(self, city: CityEnum) -> str:
        """获取城市场景描述"""
        city_name = city.name
        if city_name in CITY_SCENES:
            return CITY_SCENES[city_name]["scene_description"]
        return f"背景场景：{city_name}的标志性景点"


class EasyModePromptStrategy(PromptStrategy):
    """轻松模式提示词策略"""
    
    def generate_prompt(self, request_dto: CreatePictureRequest) -> str:
        """
        轻松模式：根据城市和服装生成提示词
        """
        scene_description = self._get_city_scene_description(request_dto.city)
        
        clothing_description = CLOTHING_TEMPLATES["easy_mode"]
        
        final_prompt = BASE_PROMPT_TEMPLATE.format(
            scene_description=scene_description,
            clothing_description=clothing_description
        )
        
        return final_prompt.strip()


class MasterModePromptStrategy(PromptStrategy):
    """大师模式提示词策略"""
    
    STYLE_MAPPING = {
        StyleEnum.FrenchElegant: "法式优雅",
        StyleEnum.JapaneseSimple: "日系简约",
        StyleEnum.FutureTech: "未来科技",
        StyleEnum.AIRandom: "AI随机匹配"
    }
    
    MATERIAL_MAPPING = {
        MaterialEnum.Denim: "牛仔",
        MaterialEnum.Silk: "丝绸",
        MaterialEnum.Cotton: "棉料",
        MaterialEnum.Metal: "金属",
        MaterialEnum.AIRandom: "AI随机匹配"
    }
    
    COLOR_MAPPING = {
        ColorEnum.Warm: "暖色调",
        ColorEnum.Cold: "冷色调",
        ColorEnum.Neutral: "中性色调",
        ColorEnum.AIRandom: "AI随机匹配"
    }
    
    TYPE_MAPPING = {
        TypeEnum.Suit: "套装",
        TypeEnum.Dress: "连衣裙",
        TypeEnum.Coat: "外套",
        TypeEnum.LocalCostume: "当地特色服饰",
        TypeEnum.AIRandom: "AI随机匹配"
    }
    
    def generate_prompt(self, request_dto: CreatePictureRequest) -> str:
        """
        大师模式：根据城市和标签生成提示词
        """
        scene_description = self._get_city_scene_description(request_dto.city)
        
        tags = request_dto.master_mode_tags
        if tags:
            style = self.STYLE_MAPPING.get(tags.style, "AI随机匹配") if tags.style else "AI随机匹配"
            material = self.MATERIAL_MAPPING.get(tags.material, "AI随机匹配") if tags.material else "AI随机匹配"
            color = self.COLOR_MAPPING.get(tags.color, "AI随机匹配") if tags.color else "AI随机匹配"
            type_ = self.TYPE_MAPPING.get(tags.type, "AI随机匹配") if tags.type else "AI随机匹配"
            
            clothing_description = CLOTHING_TEMPLATES["master_mode"].format(
                style=style,
                material=material,
                color=color,
                type=type_
            )
        else:
            clothing_description = "人物服装风格：AI随机匹配。"
        
        final_prompt = BASE_PROMPT_TEMPLATE.format(
            scene_description=scene_description,
            clothing_description=clothing_description
        )
        
        return final_prompt.strip()


class PromptStrategyFactory:
    """提示词策略工厂"""
    
    @staticmethod
    def get_strategy(mode: ModeEnum) -> PromptStrategy:
        """
        根据模式获取对应的策略
        """
        if mode == ModeEnum.Easy:
            return EasyModePromptStrategy()
        elif mode == ModeEnum.Master:
            return MasterModePromptStrategy()
        else:
            raise ValueError(f"不支持的模式: {mode}")


def generate_prompt_by_request(request_dto: CreatePictureRequest) -> str:
    """
    根据请求DTO生成提示词（对外统一接口）
    
    Args:
        request_dto: 请求DTO
        
    Returns:
        str: 生成的提示词
        
    Example:
        >>> from model.createPictureReq import CreatePictureRequest
        >>> from core.enum import CityEnum, ModeEnum, GenderEnum
        >>> 
        >>> request = CreatePictureRequest(
        ...     originPicUrl="https://example.com/image.jpg",
        ...     city=CityEnum.Tokyo,
        ...     sex=GenderEnum.Female,
        ...     mode=ModeEnum.Easy,
        ...     clothes={"items": [...]}
        ... )
        >>> prompt = generate_prompt_by_request(request)
        >>> print(prompt)
    """
    strategy = PromptStrategyFactory.get_strategy(request_dto.mode)
    return strategy.generate_prompt(request_dto)
