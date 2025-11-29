
from typing import List
import base64
from fastapi import UploadFile
from core.llm import LLMModel
from model.createPictureReq import CreatePictureRequest
from model.createPictureResp import CreatePictureResponse
from core.enum import CityEnum, ModeEnum, GenderEnum
from core.exceptions import CommonException, ParamException, ErrorCode
from core.prompt_strategy import generate_prompt_by_request
from model.createPictureResp import ImageItem
from model.createPictureResp import ImageStreamEvent, StreamStatusEnum
from core.image_utils import validate_image_format, validate_image_constraints, load_clothes_image
from utils.logger import logger
import logging
import json
import traceback
    
logger = logging.getLogger(__name__)


class DoubaoImages(LLMModel):
    """
    生图相关方法
    """
    @staticmethod
    async def verify_input_data(file: UploadFile, data: str) -> CreatePictureRequest:
        """
        校验前端传的json和图片，并返回 CreatePictureRequest 对象
        """
        # 1. 解析参数和处理图片
        try:
            # 解析 JSON
            req_dict = json.loads(data)
            request_model = CreatePictureRequest(**req_dict)
            
            # 处理图片
            image_bytes = await file.read()
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            content_type = file.content_type or "image/jpeg"
            image_format = "png" if "png" in content_type.lower() else "jpeg"
            request_model.originPicBase64 = f"data:image/{image_format};base64,{base64_str}"
            

            
            logger.info(f"流式接口接收请求: city={request_model.city}, mode={request_model.mode}")
            return request_model
            
        except Exception as e:
            logger.error(f"参数解析失败: {e}")
            # 对于流式接口前的参数错误，直接返回错误响应可能更好，但为了保持 SSE 格式，也可以在流中返回错误
            # 这里选择直接抛出 HTTP 异常，由中间件处理
            raise CommonException(message=f"参数解析失败: {str(e)}")
    
    async def translate_image_type(self,inputImage:bytes)->str:
        """
        TODO 转换前端输入的图片类型，暂不实现---后端处理前端传入的图片，转成 JPEG 并压缩
        create_picture_stream 接口一开始，收到 file 后，不要直接 read 后就转 Base64，而是先用 PIL 压缩一下
        不一定用：但是要有这个方法备用
        输入：图片二进制 bytes
        输出：Base64编码的图片 str
        """
        try:
            # 1. 打开图片
            img = Image.open(io.BytesIO(inputImage))
            
            # 2. 兼容性处理：如果是 RGBA (PNG透明底)，转为 RGB
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            # 3. 压缩保存到内存中
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='JPEG', quality=85)
            
            # 4. 转 Base64
            compressed_bytes = output_buffer.getvalue()
            base64_str = base64.b64encode(compressed_bytes).decode('utf-8')
            
            # 日志记录压缩效果
            original_mb = len(image_bytes) / 1024 / 1024
            new_mb = len(compressed_bytes) / 1024 / 1024
            logger.info(f"图片处理: {original_mb:.2f}MB -> {new_mb:.2f}MB (JPEG)")
            
            return f"data:image/jpeg;base64,{base64_str}"
            
        except Exception as e:
            logger.warning(f"图片压缩失败，降级使用原始数据: {e}")
            # 兜底：直接转 Base64
            base64_str = base64.b64encode(inputImage).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_str}"
    

    def verify_input_image(self, inputImageBase64: str):
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
    
    def verify_image_quality(self, outputImageBase64List: List[str]):
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



    async def create_picture(self, ImageStreamRequest: CreatePictureRequest)->CreatePictureResponse:
        """
        图生图主逻辑
        """
        # 1.请求参数校验已经在pytanic中实现了，这里不需要重复校验
        # 2.验证输入图片格式
        self.verify_input_image(ImageStreamRequest.originPicBase64)
        
        # 3.拼装提示词（使用策略模式）
        createPicturePrompt = generate_prompt_by_request(ImageStreamRequest)
        logger.info(f"拼装提示词：{createPicturePrompt}")
        
        # 4.准备输入图片列表
        # 图片来源说明：
        # - 人物原图：前端传入的 Base64（ImageStreamRequest.originPicBase64）
        # - 服装图片：后端根据性别和样式ID从本地文件加载（使用 ClothesLoader）
        createPictureInputBase64List = []
        
        # 4.1 添加人物原图（前端传入）
        createPictureInputBase64List.append(ImageStreamRequest.originPicBase64)
        logger.info(f"添加人物原图: 来源=前端上传")
        
        # 4.2 轻松模式：根据性别和样式ID自动加载服装图片（后端本地文件）
        if ImageStreamRequest.mode == ModeEnum.Easy and ImageStreamRequest.clothes:
            try:
                # 服装图片加载
                clothes_images = load_clothes_image(
                    sex=ImageStreamRequest.gender.value,
                    upper_style_id=ImageStreamRequest.clothes.upperStyle,
                    lower_style_id=ImageStreamRequest.clothes.lowerStyle,
                    dress_id=ImageStreamRequest.clothes.dress
                )
                
                # 添加服装图片到输入列表
                createPictureInputBase64List.extend(clothes_images)
                
                # 日志记录
                if ImageStreamRequest.clothes.dress is not None:
                    logger.info(f"添加连衣裙: 性别={ImageStreamRequest.gender.name}, 样式ID={ImageStreamRequest.clothes.dress}, 来源=本地文件")
                else:
                    logger.info(f"添加服装图片: 性别={ImageStreamRequest.gender.name}, 上装ID={ImageStreamRequest.clothes.upperStyle}, 下装ID={ImageStreamRequest.clothes.lowerStyle}, 来源=本地文件")
                
            except ValueError as e:
                logger.error(f"加载服装图片失败: {e}")
                raise ParamException(
                    message=str(e),
                    error_code=ErrorCode.PARAM_INVALID
                )
            except FileNotFoundError as e:
                logger.error(f"服装图片文件不存在: {e}")
                raise ParamException(
                    message="服装图片文件不存在，请联系管理员",
                    error_code=ErrorCode.RESOURCE_NOT_FOUND
                )
        
        logger.info(f"输入图片总数: {len(createPictureInputBase64List)} 张（1张人物 + {len(createPictureInputBase64List)-1}张服装）")
        
        # 5.调用火山豆包生图接口（流式生成器）
        outputImageBase64List = []
        async for base64_image in self.create_picture_by_seed_ream(createPictureInputBase64List, createPicturePrompt):
            # 单张图片质量校验（可选）
            # await self.verifySingleImageQuality(base64_image)
            outputImageBase64List.append(base64_image)
        
        # 5.校验生成图片质量（批量校验）
        self.verify_image_quality(outputImageBase64List)

        # 6.封装dto响应体返回
        images = [
            ImageItem(id=idx, base64=img_base64)
            for idx, img_base64 in enumerate(outputImageBase64List)
        ]
        
        return CreatePictureResponse(images=images)
    
    async def create_picture_stream(self, ImageStreamRequest: CreatePictureRequest):
        """
        流式图生图 - 生成器方法，用于 SSE 推送
        每生成一张图片就立即推送，最后发送完成或失败状态
        """
        try:


            # 验证输入图片
            self.verify_input_image(ImageStreamRequest.originPicBase64)
            
            # 生成提示词
            createPicturePrompt = generate_prompt_by_request(ImageStreamRequest)
            logger.info(f"流式生成 - 提示词：{createPicturePrompt}")
            
            # 准备输入图片列表
            createPictureInputBase64List = [ImageStreamRequest.originPicBase64]
            
            # 轻松模式：加载服装图片
            if ImageStreamRequest.mode == ModeEnum.Easy and ImageStreamRequest.clothes:
                try:
                    clothes_images = load_clothes_image(
                        sex=ImageStreamRequest.gender.value,
                        upper_style_id=ImageStreamRequest.clothes.upperStyle,
                        lower_style_id=ImageStreamRequest.clothes.lowerStyle,
                        dress_id=ImageStreamRequest.clothes.dress
                    )
                    createPictureInputBase64List.extend(clothes_images)
                except ValueError as e:
                    logger.error(f"加载服装图片失败: {e}")
                    raise ParamException(message=str(e), error_code=ErrorCode.PARAM_INVALID)
                except FileNotFoundError as e:
                    logger.error(f"服装图片文件不存在: {e}")
                    raise ParamException(message="服装图片文件不存在，请联系管理员", error_code=ErrorCode.RESOURCE_NOT_FOUND)
            
            logger.info(f"流式生成 - 输入图片总数: {len(createPictureInputBase64List)} 张")
            
            # 调用底层生成器，逐张推送图片
            image_count = 0
            async for base64_image in self.create_picture_by_seed_ream(createPictureInputBase64List, createPicturePrompt):
                # 封装成功生成的消息
                resp = ImageStreamEvent(
                    status=StreamStatusEnum.Generating,
                    index=image_count,
                    base64=base64_image,
                    message="success"
                )
                image_count += 1
                logger.info(f"流式推送图片 index={image_count-1}")
                yield resp.to_event_data()
            
            # 发送完成信号
            logger.info(f"流式生成完成，共生成 {image_count} 张图片")
            end_resp = ImageStreamEvent(
                status=StreamStatusEnum.Completed,
                message=f"生成流程结束，共生成 {image_count} 张图片"
            )
            yield end_resp.to_event_data()
            
        except Exception as e:
            # 发送错误信号
            logger.error(f"流式生成异常: {e}")
            error_detail = traceback.format_exc()
            logger.error(f"异常详情: {error_detail}")
            error_resp = ImageStreamEvent(
                status=StreamStatusEnum.Failed,
                message=str(e)
            )
            yield error_resp.to_event_data()



        
