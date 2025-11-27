# 将 FastAPI 接口文档导入 Apifox 指南

## 方法一：通过 OpenAPI/Swagger JSON 导入（推荐）

### 步骤 1：启动 FastAPI 服务

```bash
# 启动服务
uv run python journey_poster.py
```

服务启动后，FastAPI 会自动生成 OpenAPI 文档，访问：
- Swagger UI: `http://localhost:8123/docs`
- ReDoc: `http://localhost:8123/redoc`
- OpenAPI JSON: `http://localhost:8123/openapi.json`

### 步骤 2：在 Apifox 中导入

1. **打开 Apifox**
   - 创建新项目或选择现有项目

2. **导入接口**
   - 点击左侧菜单的 **"导入"** 或 **"+"** 按钮
   - 选择 **"OpenAPI/Swagger"**
   - 选择导入方式：
     - **方式 A：URL 导入（推荐）**
       - 输入 URL: `http://localhost:8123/openapi.json`
       - 点击"导入"
     - **方式 B：文件导入**
       - 先访问 `http://localhost:8123/openapi.json`
       - 保存 JSON 文件
       - 在 Apifox 中选择"文件导入"，上传该 JSON 文件

3. **配置环境变量**
   - 导入后，在 Apifox 中设置环境变量（如果需要）
   - 例如：`base_url = http://localhost:8123`

### 步骤 3：验证导入

导入成功后，你应该能看到：
- `/` - 根路径
- `/health` - 健康检查
- `/createPicture` - 图片生成接口

## 方法二：手动配置（如果自动导入失败）

### 1. 创建接口

在 Apifox 中手动创建接口：

**接口 1：健康检查**
- 方法：`GET`
- URL：`{{base_url}}/health`
- 响应示例：
```json
{
  "success": true,
  "status": 200,
  "message": "healthy",
  "data": {
    "timestamp": "2025-11-28 12:00:00"
  }
}
```

**接口 2：图片生成**
- 方法：`POST`
- URL：`{{base_url}}/createPicture`
- Headers：
  ```
  Content-Type: application/json
  ```
- Body（JSON）：
```json
{
  "originPicBase64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "city": 1,
  "sex": 1,
  "mode": 0,
  "clothes": {
    "items": [
      {
        "category": 2,
        "style_file_name": "female_clothes",
        "style_name": "女士上装"
      },
      {
        "category": 3,
        "style_file_name": "female_pants",
        "style_name": "女士下装"
      }
    ]
  }
}
```

### 2. 设置环境变量

在 Apifox 中创建环境：
- 环境名称：`本地开发`
- 变量：
  - `base_url`: `http://localhost:8123`

## 方法三：使用 Apifox CLI（高级）

如果你使用 Apifox CLI，可以：

```bash
# 安装 Apifox CLI
npm install -g @apifox/cli

# 导入 OpenAPI 文档
apifox import openapi http://localhost:8123/openapi.json
```

## 优化 FastAPI 文档（可选）

为了让导入的文档更完整，可以在 `journey_poster.py` 中添加更多文档信息：

```python
app = FastAPI(
    title="Journey Poster API",
    description="""
    ## 年会AI-环球之旅图片生成服务
    
    ### 功能说明
    - 图生图：基于用户上传的图片和选择的城市、服装，生成4张不同场景的图片
    - 支持轻松模式和大师模式两种生成方式
    
    ### 接口列表
    - `/createPicture`: 图片生成接口
    - `/health`: 健康检查接口
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)
```

## 常见问题

### Q1: 导入后接口参数不完整？
**A:** 确保 FastAPI 的 Pydantic 模型有完整的 `Field` 描述，例如：
```python
originPicBase64: str = Field(..., description="用户输入的原图Base64编码")
```

### Q2: 导入后无法测试？
**A:** 
1. 确保 FastAPI 服务正在运行
2. 检查 Apifox 中的环境变量 `base_url` 是否正确
3. 检查接口的 URL 是否使用了环境变量：`{{base_url}}/createPicture`

### Q3: 如何更新接口文档？
**A:** 
- 修改代码后，重启 FastAPI 服务
- 在 Apifox 中重新导入 `openapi.json`（选择"覆盖导入"）

## 参考链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Apifox 导入文档](https://apifox.com/help/app/import)
- [OpenAPI 规范](https://swagger.io/specification/)

