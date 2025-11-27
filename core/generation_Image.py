
from typing import List
from core.llm import LLMModel
from dto.createPictureReqDto import CreatePictureReqDto
from dto.createPictureRespDto import CreatePictureRespDto
from core.enum import CityEnum, ModeEnum, SexEnum
from core.exceptions import CommonException
from core.prompt_strategy import generate_prompt_by_request
from utils.image_utils import validate_image_format, validate_image_constraints



class doubao_images(LLMModel):
    """
    在这里完成图生图接口的逻辑
    """
    async def verifyInputImage(self, inputImageBase64: str):
        """
        校验输入图片格式和约束条件
        
        约束条件：
        - 图片格式：jpeg、png
        - 宽高比（宽/高）范围：[1/3, 3]
        - 宽高长度（px） > 14
        - 大小：不超过 10MB
        - 总像素：不超过 6000×6000 px
        
        Args:
            inputImageBase64: 输入图片Base64编码
            
        Raises:
            CommonException: 图片验证失败时抛出异常
        """
        # 1. 验证 Base64 格式
        is_valid, format_type = validate_image_format(inputImageBase64)
        
        if not is_valid:
            raise CommonException(message="输入图片格式不正确，请提供有效的Base64编码（格式：data:image/<format>;base64,<base64_data>），仅支持 jpeg、png 格式")
        
        # 2. 验证图片约束条件
        is_valid_constraints, error_message = validate_image_constraints(inputImageBase64)
        
        if not is_valid_constraints:
            raise CommonException(message=f"输入图片不符合要求：{error_message}")
        
        return True
    
    async def verifyImageQuality(self, outputImageBase64List: List[str]):
        """
        校验生成图片质量
        
        Args:
            outputImageBase64List: 生成的图片 Base64 列表
            
        Returns:
            bool: 校验通过返回 True
        """
        # TODO: 实现图片质量校验逻辑
        # 例如：检查图片是否为空、尺寸是否符合要求等
        if not outputImageBase64List:
            raise CommonException(message="生成的图片列表为空")
        
        if len(outputImageBase64List) != 4:
            raise CommonException(message=f"期望生成4张图片，实际生成{len(outputImageBase64List)}张")
        
        return True


    async def createPicture(self, requestDto: CreatePictureReqDto)->CreatePictureRespDto:
        """
        图生图主逻辑
        """
        # 添加更多入参校验逻辑
        if requestDto.city not in CityEnum:
            raise CommonException(message="城市不存在")
        if requestDto.mode not in ModeEnum:
            raise CommonException(message="mode参数错误")
        if requestDto.sex not in SexEnum:
            raise CommonException(message="sex参数错误")
        if requestDto.mode == ModeEnum.EASY and requestDto.clothes is None:
            raise CommonException(message="轻松模式下必须提供服装参数")
        if requestDto.mode == ModeEnum.MASTER and requestDto.master_mode_tags is None:
            raise CommonException(message="大师模式下必须提供标签参数")

        # 2.验证输入图片格式
        await self.verifyInputImage(requestDto.originPicBase64)
        
        # 3.拼装提示词（使用策略模式）
        createPicturePrompt = generate_prompt_by_request(requestDto)
        
        # 4.调用火山豆包生图接口
        createPictureInputBase64List = []
        createPictureInputBase64List.append(requestDto.originPicBase64)
        outputImageBase64List = await self.createPictureBySeedReam(createPictureInputBase64List, createPicturePrompt)
        
        # 5.校验生成图片质量
        await self.verifyImageQuality(outputImageBase64List)

        # 6.封装dto响应体返回
        createPictureRespDto = CreatePictureRespDto()
        createPictureRespDto.images = outputImageBase64List
        createPictureRespDto.city = requestDto.city
        createPictureRespDto.mode = requestDto.mode
        return createPictureRespDto



        
