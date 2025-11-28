"""
公共异常类
"""
from typing import Any, Optional
from enum import Enum
from fastapi import status as http_status


class ErrorCode(Enum):
    """错误码枚举"""
    SUCCESS = (0, "成功")
    
    SYSTEM_ERROR = (10000, "系统错误")
    NETWORK_ERROR = (10001, "网络错误")
    TIMEOUT_ERROR = (10002, "请求超时")
    
    PARAM_ERROR = (20000, "参数错误")
    PARAM_MISSING = (20001, "缺少必要参数")
    PARAM_INVALID = (20002, "参数格式不正确")
    
    AUTH_ERROR = (30000, "认证失败")
    AUTH_UNAUTHORIZED = (30001, "未授权访问")
    AUTH_FORBIDDEN = (30003, "权限不足")
    AUTH_TOKEN_EXPIRED = (30004, "Token已过期")
    
    LLM_ERROR = (40000, "AI模型调用失败")
    LLM_API_KEY_INVALID = (40001, "API Key无效")
    LLM_MODEL_NOT_FOUND = (40002, "模型不存在")
    LLM_QUOTA_EXCEEDED = (40003, "配额已用尽")
    LLM_CONTENT_FILTER = (40004, "内容被过滤")
    LLM_GENERATION_FAILED = (40005, "图片生成失败")
    LLM_STREAM_ERROR = (40006, "流式响应错误")
    
    IMAGE_ERROR = (50000, "图片处理错误")
    IMAGE_FORMAT_ERROR = (50001, "图片格式不支持")
    IMAGE_SIZE_ERROR = (50002, "图片尺寸超限")
    IMAGE_DECODE_ERROR = (50003, "图片解码失败")
    IMAGE_ENCODE_ERROR = (50004, "图片编码失败")
    
    BUSINESS_ERROR = (60000, "业务逻辑错误")
    RESOURCE_NOT_FOUND = (60001, "资源不存在")
    RESOURCE_ALREADY_EXISTS = (60002, "资源已存在")
    OPERATION_NOT_ALLOWED = (60003, "操作不允许")
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class CommonException(Exception):
    """
    自定义异常基类
    用于统一处理业务异常
    """
    def __init__(
        self, 
        success: bool = False, 
        status: int = http_status.HTTP_500_INTERNAL_SERVER_ERROR, 
        message: str = "服务器内部错误", 
        data: Any = None,
        error_code: Optional[ErrorCode] = None
    ):
        self.success = success
        self.status = status
        self.message = message
        self.data = data
        self.error_code = error_code or ErrorCode.SYSTEM_ERROR
        super().__init__(self.message)


class ParamException(CommonException):
    """参数异常"""
    def __init__(self, message: str = "参数错误", data: Any = None, error_code: ErrorCode = ErrorCode.PARAM_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data,
            error_code=error_code
        )


class AuthException(CommonException):
    """认证异常"""
    def __init__(self, message: str = "认证失败", data: Any = None, error_code: ErrorCode = ErrorCode.AUTH_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_401_UNAUTHORIZED,
            message=message,
            data=data,
            error_code=error_code
        )


class ForbiddenException(CommonException):
    """权限异常"""
    def __init__(self, message: str = "权限不足", data: Any = None, error_code: ErrorCode = ErrorCode.AUTH_FORBIDDEN):
        super().__init__(
            success=False,
            status=http_status.HTTP_403_FORBIDDEN,
            message=message,
            data=data,
            error_code=error_code
        )


class LLMException(CommonException):
    """AI模型调用异常"""
    def __init__(self, message: str = "AI模型调用失败", data: Any = None, error_code: ErrorCode = ErrorCode.LLM_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            data=data,
            error_code=error_code
        )


class ImageException(CommonException):
    """图片处理异常"""
    def __init__(self, message: str = "图片处理错误", data: Any = None, error_code: ErrorCode = ErrorCode.IMAGE_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data,
            error_code=error_code
        )


class BusinessException(CommonException):
    """业务逻辑异常"""
    def __init__(self, message: str = "业务逻辑错误", data: Any = None, error_code: ErrorCode = ErrorCode.BUSINESS_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_400_BAD_REQUEST,
            message=message,
            data=data,
            error_code=error_code
        )


class NetworkException(CommonException):
    """网络异常"""
    def __init__(self, message: str = "网络错误", data: Any = None, error_code: ErrorCode = ErrorCode.NETWORK_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            data=data,
            error_code=error_code
        )


class TimeoutException(CommonException):
    """超时异常"""
    def __init__(self, message: str = "请求超时", data: Any = None, error_code: ErrorCode = ErrorCode.TIMEOUT_ERROR):
        super().__init__(
            success=False,
            status=http_status.HTTP_504_GATEWAY_TIMEOUT,
            message=message,
            data=data,
            error_code=error_code
        )


class ResourceNotFoundException(CommonException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在", data: Any = None, error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND):
        super().__init__(
            success=False,
            status=http_status.HTTP_404_NOT_FOUND,
            message=message,
            data=data,
            error_code=error_code
        )

