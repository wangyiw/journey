"""
公共异常类
"""
from typing import Any
from fastapi import status as http_status


class CommonException(Exception):
    """
    自定义异常类
    用于统一处理业务异常
    """
    def __init__(self, success: bool = False, status: int = http_status.HTTP_500_INTERNAL_SERVER_ERROR, 
                 message: str = "服务器内部错误", data: Any = None):
        self.success = success
        self.status = status
        self.message = message
        self.data = data
        super().__init__(self.message)

