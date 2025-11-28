# 自定义异常使用指南

## 异常类型体系

### 1. 错误码枚举 (ErrorCode)

所有异常都关联一个错误码，便于前端识别和处理。

```python
from core.exceptions import ErrorCode

# 系统错误 (10000-10999)
ErrorCode.SYSTEM_ERROR          # 10000 系统错误
ErrorCode.NETWORK_ERROR         # 10001 网络错误
ErrorCode.TIMEOUT_ERROR         # 10002 请求超时

# 参数错误 (20000-20999)
ErrorCode.PARAM_ERROR           # 20000 参数错误
ErrorCode.PARAM_MISSING         # 20001 缺少必要参数
ErrorCode.PARAM_INVALID         # 20002 参数格式不正确

# 认证错误 (30000-30999)
ErrorCode.AUTH_ERROR            # 30000 认证失败
ErrorCode.AUTH_UNAUTHORIZED     # 30001 未授权访问
ErrorCode.AUTH_FORBIDDEN        # 30003 权限不足
ErrorCode.AUTH_TOKEN_EXPIRED    # 30004 Token已过期

# AI模型错误 (40000-40999)
ErrorCode.LLM_ERROR             # 40000 AI模型调用失败
ErrorCode.LLM_API_KEY_INVALID   # 40001 API Key无效
ErrorCode.LLM_MODEL_NOT_FOUND   # 40002 模型不存在
ErrorCode.LLM_QUOTA_EXCEEDED    # 40003 配额已用尽
ErrorCode.LLM_CONTENT_FILTER    # 40004 内容被过滤
ErrorCode.LLM_GENERATION_FAILED # 40005 图片生成失败
ErrorCode.LLM_STREAM_ERROR      # 40006 流式响应错误

# 图片处理错误 (50000-50999)
ErrorCode.IMAGE_ERROR           # 50000 图片处理错误
ErrorCode.IMAGE_FORMAT_ERROR    # 50001 图片格式不支持
ErrorCode.IMAGE_SIZE_ERROR      # 50002 图片尺寸超限
ErrorCode.IMAGE_DECODE_ERROR    # 50003 图片解码失败
ErrorCode.IMAGE_ENCODE_ERROR    # 50004 图片编码失败

# 业务逻辑错误 (60000-60999)
ErrorCode.BUSINESS_ERROR        # 60000 业务逻辑错误
ErrorCode.RESOURCE_NOT_FOUND    # 60001 资源不存在
ErrorCode.RESOURCE_ALREADY_EXISTS # 60002 资源已存在
ErrorCode.OPERATION_NOT_ALLOWED # 60003 操作不允许
```

### 2. 异常类

#### 基类异常
```python
from core.exceptions import CommonException, ErrorCode

# 通用异常（不推荐直接使用，应使用具体的子类）
raise CommonException(
    success=False,
    status=500,
    message="错误信息",
    data={"detail": "额外数据"},
    error_code=ErrorCode.SYSTEM_ERROR
)
```

#### 参数异常 (ParamException)
```python
from core.exceptions import ParamException, ErrorCode

# 基本用法
raise ParamException(message="用户名不能为空")

# 指定错误码
raise ParamException(
    message="邮箱格式不正确",
    error_code=ErrorCode.PARAM_INVALID
)

# 携带额外数据
raise ParamException(
    message="参数验证失败",
    data={"field": "email", "value": "invalid@"},
    error_code=ErrorCode.PARAM_INVALID
)
```

#### 认证异常 (AuthException)
```python
from core.exceptions import AuthException, ErrorCode

# API Key 无效
raise AuthException(
    message="API Key认证失败",
    error_code=ErrorCode.LLM_API_KEY_INVALID
)

# Token 过期
raise AuthException(
    message="登录已过期，请重新登录",
    error_code=ErrorCode.AUTH_TOKEN_EXPIRED
)
```

#### 权限异常 (ForbiddenException)
```python
from core.exceptions import ForbiddenException, ErrorCode

raise ForbiddenException(
    message="您没有权限访问此资源",
    error_code=ErrorCode.AUTH_FORBIDDEN
)
```

#### AI模型异常 (LLMException)
```python
from core.exceptions import LLMException, ErrorCode

# 模型调用失败
raise LLMException(
    message="图片生成失败",
    error_code=ErrorCode.LLM_GENERATION_FAILED
)

# 配额用尽
raise LLMException(
    message="今日配额已用尽，请明天再试",
    error_code=ErrorCode.LLM_QUOTA_EXCEEDED
)

# 模型不存在
raise LLMException(
    message=f"模型 {model_id} 不存在",
    error_code=ErrorCode.LLM_MODEL_NOT_FOUND
)
```

#### 图片处理异常 (ImageException)
```python
from core.exceptions import ImageException, ErrorCode

# 图片格式错误
raise ImageException(
    message="仅支持 JPEG 和 PNG 格式",
    error_code=ErrorCode.IMAGE_FORMAT_ERROR
)

# 图片尺寸超限
raise ImageException(
    message="图片大小不能超过 10MB",
    error_code=ErrorCode.IMAGE_SIZE_ERROR,
    data={"max_size": "10MB", "actual_size": "15MB"}
)
```

#### 业务逻辑异常 (BusinessException)
```python
from core.exceptions import BusinessException, ErrorCode

# 资源不存在
raise BusinessException(
    message="订单不存在",
    error_code=ErrorCode.RESOURCE_NOT_FOUND
)

# 操作不允许
raise BusinessException(
    message="订单已完成，无法取消",
    error_code=ErrorCode.OPERATION_NOT_ALLOWED
)
```

#### 网络异常 (NetworkException)
```python
from core.exceptions import NetworkException, ErrorCode

raise NetworkException(
    message="网络连接失败，请检查网络设置",
    error_code=ErrorCode.NETWORK_ERROR
)
```

#### 超时异常 (TimeoutException)
```python
from core.exceptions import TimeoutException, ErrorCode

raise TimeoutException(
    message="请求超时，请稍后重试",
    error_code=ErrorCode.TIMEOUT_ERROR
)
```

#### 资源不存在异常 (ResourceNotFoundException)
```python
from core.exceptions import ResourceNotFoundException, ErrorCode

raise ResourceNotFoundException(
    message=f"用户 {user_id} 不存在",
    error_code=ErrorCode.RESOURCE_NOT_FOUND
)
```

## 使用场景示例

### 1. 在 API 路由中使用
```python
from fastapi import APIRouter
from core.exceptions import ParamException, LLMException, ErrorCode

router = APIRouter()

@router.post("/generate")
async def generate_image(request: CreatePictureRequest):
    # 参数验证
    if not request.prompt:
        raise ParamException(
            message="提示词不能为空",
            error_code=ErrorCode.PARAM_MISSING
        )
    
    # 调用 AI 模型
    try:
        result = await llm_model.createPictureBySeedReam(...)
    except Exception as e:
        # 模型调用失败
        raise LLMException(
            message=f"图片生成失败: {str(e)}",
            error_code=ErrorCode.LLM_GENERATION_FAILED
        )
    
    return result
```

### 2. 在服务层使用
```python
from core.exceptions import ImageException, ErrorCode
import base64

def validate_image(image_base64: str):
    """验证图片"""
    try:
        # 解码 Base64
        image_data = base64.b64decode(image_base64)
    except Exception:
        raise ImageException(
            message="图片解码失败，请检查图片格式",
            error_code=ErrorCode.IMAGE_DECODE_ERROR
        )
    
    # 检查文件大小
    max_size = 10 * 1024 * 1024  # 10MB
    if len(image_data) > max_size:
        raise ImageException(
            message="图片大小超过限制",
            error_code=ErrorCode.IMAGE_SIZE_ERROR,
            data={
                "max_size": "10MB",
                "actual_size": f"{len(image_data) / 1024 / 1024:.2f}MB"
            }
        )
```

### 3. 在异常处理器中使用
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exceptions import CommonException

app = FastAPI()

@app.exception_handler(CommonException)
async def common_exception_handler(request: Request, exc: CommonException):
    """统一异常处理"""
    return JSONResponse(
        status_code=exc.status,
        content={
            "success": exc.success,
            "code": exc.error_code.code,
            "message": exc.message,
            "data": exc.data
        }
    )
```

## 异常属性说明

所有自定义异常都包含以下属性：

- `success`: bool - 是否成功（通常为 False）
- `status`: int - HTTP 状态码
- `message`: str - 错误信息
- `data`: Any - 额外数据（可选）
- `error_code`: ErrorCode - 错误码枚举

## 最佳实践

1. **优先使用具体的异常类**，而不是通用的 `CommonException`
2. **为每个异常指定合适的 ErrorCode**，便于前端识别和处理
3. **在 data 字段中提供额外的上下文信息**，帮助调试和用户理解
4. **在捕获异常时，优先捕获具体的异常类型**
5. **在 API 层统一处理异常**，返回标准的 JSON 响应格式

## 前端响应格式

```json
{
  "success": false,
  "code": 40001,
  "message": "API Key认证失败",
  "data": {
    "detail": "提供的 API Key 无效或已过期"
  }
}
```
