# Apifox 请求示例

## 1. 豆包图片生成 API（直接调用）

### 请求配置

**URL:** `https://ark.cn-beijing.volces.com/api/v3/images/generations`

**Method:** `POST`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{LLM_API_KEY}}
```

**Body (JSON):**
```json
{
  "model": "ep-m-20251127211119-7fbfh",
  "prompt": "一位亚洲男性，自然美颜，真实质感。\n背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑（随机生成四种不同场景），使人物与背景自然融合：光影一致、色彩统一、景深协调，整体呈现照片级超写实风格。\n\n人物服装：提供的服饰图片。\n\n人物姿势可根据场景做自然变化，但必须保持合理的人体结构和正常比例。\n整体风格：超写实、高清、自然色调、真实空气感、柔和氛围光。\n一次性生成四张不同构图和场景的高清照片，供选择。",
  "image": "data:image/jpeg;base64,{{IMAGE_BASE64}}",
  "size": "2K",
  "sequential_image_generation": "auto",
  "sequential_image_generation_options": {
    "max_images": 4
  },
  "response_format": "b64_json",
  "stream": true,
  "watermark": false
}
```

**环境变量设置：**
- `LLM_API_KEY`: 你的火山引擎 API Key
- `IMAGE_BASE64`: 图片的 Base64 编码（不含 `data:image/jpeg;base64,` 前缀）

**注意：**
- `image` 参数需要完整的 Base64 格式：`data:image/jpeg;base64,<base64_data>` 或 `data:image/png;base64,<base64_data>`
- 如果使用流式响应（`stream: true`），响应会是 Server-Sent Events (SSE) 格式
- 如果使用非流式（`stream: false`），响应格式如下：

```json
{
  "model": "ep-m-20251127211119-7fbfh",
  "created": 1757321139,
  "data": [
    {
      "url": "https://...",
      "size": "3104x1312"
    }
  ],
  "usage": {
    "generated_images": 1,
    "output_tokens": 1234,
    "total_tokens": 5678
  }
}
```

## 2. 你的业务接口（FastAPI）

### 2.1 健康检查

**URL:** `{{base_url}}/health`

**Method:** `GET`

**响应示例：**
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

### 2.2 图片生成接口

**URL:** `{{base_url}}/createPicture`

**Method:** `POST`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON) - 轻松模式示例：**
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

**Body (JSON) - 大师模式示例：**
```json
{
  "originPicBase64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "city": 0,
  "sex": 0,
  "mode": 1,
  "master_mode_tags": {
    "style": 0,
    "material": 1,
    "color": 2,
    "type": 0
  }
}
```

**城市枚举值：**
- 0: 东京
- 1: 巴黎
- 2: 伦敦
- 3: 纽约
- 4: 曼谷
- 5: 罗马
- 6: 马德里
- 7: 伊斯坦布尔
- 8: 米兰
- 9: 新加坡
- 10: 迪拜
- 11: 北京
- 12: 深圳
- 13: 柏林
- 14: 吉隆坡
- 15: 首尔
- 16: 上海
- 17: 香港
- 18: 阿姆斯特丹
- 19: 悉尼

**性别枚举值：**
- 0: 男
- 1: 女

**模式枚举值：**
- 0: 轻松模式（需要提供 `clothes`）
- 1: 大师模式（需要提供 `master_mode_tags`）

**服装类别枚举值：**
- 0: 男上装
- 1: 男下装
- 2: 女上装
- 3: 女下装
- 4: 连衣裙

**风格枚举值（大师模式）：**
- 0: 法式优雅
- 1: 日系简约
- 2: 未来科技
- 3: AI随机匹配

**材质枚举值（大师模式）：**
- 0: 牛仔
- 1: 丝绸
- 2: 棉料
- 3: 金属
- 4: AI随机匹配

**色调枚举值（大师模式）：**
- 0: 暖色调
- 1: 冷色调
- 2: 中性色调
- 3: AI随机匹配

**类型枚举值（大师模式）：**
- 0: 套装
- 1: 连衣裙
- 2: 外套
- 3: 当地特色服饰
- 4: AI随机匹配

**响应示例：**
```json
{
  "success": true,
  "status": 200,
  "message": "成功",
  "data": {
    "images": [
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    ],
    "city": 1,
    "mode": 0
  }
}
```

## 环境变量配置

在 Apifox 中创建环境，设置以下变量：

**本地开发环境：**
- `base_url`: `http://localhost:8123`
- `LLM_API_KEY`: `your_api_key_here`
- `IMAGE_BASE64`: `图片的Base64编码（不含前缀）`

**生产环境：**
- `base_url`: `https://your-production-domain.com`
- `LLM_API_KEY`: `your_production_api_key`
- `IMAGE_BASE64`: `图片的Base64编码（不含前缀）`

