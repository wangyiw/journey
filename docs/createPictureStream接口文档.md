# createPictureStream 流式图生图接口文档

## 一、接口基本信息

### 1.1 接口概述
流式图片生成接口，基于用户上传的原图和选择的参数，实时生成4张不同场景的图片。每生成一张图片就立即通过 Server-Sent Events (SSE) 推送到前端。

### 1.2 接口地址
```
POST /createPictureStream
```

### 1.3 请求方式
- **Content-Type**: `multipart/form-data`
- **响应格式**: `text/event-stream` (SSE)

---

## 二、Apifox 导入 cURL

```bash
curl --location 'http://localhost:8123/createPictureStream' \
--form 'file=@"/path/to/your/image.jpg"' \
--form 'data="{
  \"city\": \"Tokyo\",
  \"gender\": \"Female\",
  \"mode\": \"Easy\",
  \"clothes\": {
    \"upperStyle\": \"female_upper_01\",
    \"lowerStyle\": \"female_lower_01\",
    \"dress\": null
  }
}"'
```

**使用说明**：
1. 将 `/path/to/your/image.jpg` 替换为实际图片路径
2. 将 `http://localhost:8123` 替换为实际服务地址
3. 根据需要修改 `data` 参数中的配置

---

## 三、请求参数

### 3.1 Form-Data 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 用户上传的原图文件 |
| data | String | 是 | JSON 字符串格式的请求参数 |

### 3.2 data 参数详细说明（JSON 格式）

#### 3.2.1 公共参数

| 字段 | 类型 | 必填 | 说明 | 可选值 |
|------|------|------|------|--------|
| city | String | 是 | 城市名称 | Tokyo, Paris, London, NewYork, Bangkok, Rome, Madrid, Istanbul, Milan, Singapore, Dubai, Beijing, Shenzhen, Berlin, KualaLumpur, Seoul, Shanghai, HongKong, Amsterdam, Sydney |
| gender | String | 是 | 性别 | Male（男）, Female（女）|
| mode | String | 是 | 生成模式 | Easy（轻松模式）, Master（大师模式）|

#### 3.2.2 轻松模式参数（mode=Easy 时必填）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| clothes | Object | 是 | 服装配置对象 |
| clothes.upperStyle | String | 条件必填 | 上装样式ID（如 male_upper_01, female_upper_01）|
| clothes.lowerStyle | String | 条件必填 | 下装样式ID（如 male_lower_01, female_lower_01）|
| clothes.dress | String | 条件必填 | 连衣裙样式ID（如 female_dress_01，仅女性可用）|

**服装选择规则**：
- **男性**：必须同时传 `upperStyle` 和 `lowerStyle`，不能传 `dress`
- **女性**：可以传 `upperStyle + lowerStyle`，或只传 `dress`（二选一）

**可用样式ID**：
- 男上装：`male_upper_01`, `male_upper_02`, `male_upper_03`
- 男下装：`male_lower_01`, `male_lower_02`, `male_lower_03`
- 女上装：`female_upper_01`, `female_upper_02`, `female_upper_03`
- 女下装：`female_lower_01`, `female_lower_02`, `female_lower_03`
- 连衣裙：`female_dress_01`, `female_dress_02`, `female_dress_03`

#### 3.2.3 大师模式参数（mode=Master 时必填）

| 字段 | 类型 | 必填 | 说明 | 可选值 |
|------|------|------|------|--------|
| master_mode_tags | Object | 是 | 大师模式标签配置 | - |
| master_mode_tags.style | String | 否 | 风格 | FrenchElegant（法式优雅）, JapaneseSimple（日系简约）, FutureTech（未来科技）, AIRandom（AI随机匹配）|
| master_mode_tags.material | String | 否 | 材质 | Denim（牛仔）, Silk（丝绸）, Cotton（棉料）, Metal（金属）, AIRandom（AI随机匹配）|
| master_mode_tags.color | String | 否 | 色调 | Warm（暖色调）, Cold（冷色调）, Neutral（中性色调）, AIRandom（AI随机匹配）|
| master_mode_tags.type | String | 否 | 类型 | Suit（套装）, Dress（连衣裙）, Coat（外套）, LocalCostume（当地特色服饰）, AIRandom（AI随机匹配）|

**注意**：男性不能选择 `type=Dress`（连衣裙类型）

### 3.3 图片约束条件

上传的图片必须满足以下条件：
- **格式**：jpeg、png
- **宽高比**：[1/3, 3]
- **最小尺寸**：宽高 > 14px
- **最大大小**：≤ 10MB
- **最大像素**：≤ 6000×6000 px

---

## 四、响应格式

### 4.1 响应头
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

### 4.2 SSE 事件格式

每个事件以 `data:` 开头，以 `\n\n` 结尾：

```
data: {"status": "generating", "index": 0, "base64": "data:image/...", "message": "success"}

```

### 4.3 事件状态类型

#### 4.3.1 生成中（generating）
```json
{
  "status": "generating",
  "index": 0,
  "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA...",
  "message": "success"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| status | String | 固定值 "generating" |
| index | Integer | 图片索引（0-3）|
| base64 | String | 图片Base64编码（格式：data:image/jpeg;base64,...）|
| message | String | 提示信息，通常为 "success" |

#### 4.3.2 全部完成（completed）
```json
{
  "status": "completed",
  "message": "生成流程结束，共生成 4 张图片"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| status | String | 固定值 "completed" |
| message | String | 完成提示信息 |

#### 4.3.3 生成失败（failed）
```json
{
  "status": "failed",
  "message": "生成失败：参数验证错误"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| status | String | 固定值 "failed" |
| message | String | 错误信息 |

---

## 五、请求示例

### 5.1 轻松模式 - 男性上装+下装
```json
{
  "city": "Tokyo",
  "gender": "Male",
  "mode": "Easy",
  "clothes": {
    "upperStyle": "male_upper_01",
    "lowerStyle": "male_lower_01",
    "dress": null
  }
}
```

### 5.2 轻松模式 - 女性连衣裙
```json
{
  "city": "Paris",
  "gender": "Female",
  "mode": "Easy",
  "clothes": {
    "upperStyle": null,
    "lowerStyle": null,
    "dress": "female_dress_01"
  }
}
```

### 5.3 大师模式 - 女性法式优雅风格
```json
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
```

---

## 六、提示词拼接与资源映射机制

### 6.1 提示词拼接流程

#### 6.1.1 流程图
```
用户请求
    ↓
参数验证（CreatePictureRequest）
    ↓
策略工厂选择策略（PromptStrategyFactory）
    ├─ 轻松模式 → EasyModePromptStrategy
    └─ 大师模式 → MasterModePromptStrategy
    ↓
获取城市场景描述（CITY_SCENES）
    ↓
生成服装描述
    ├─ 轻松模式：固定模板 "人物服装：提供的服饰图片。"
    └─ 大师模式：根据标签拼接 "人物服装风格：{style}，材质：{material}，色调：{color}，类型：{type}。"
    ↓
填充基础提示词模板（BASE_PROMPT_TEMPLATE）
    ↓
返回完整提示词
```

#### 6.1.2 代码实现路径
1. **入口函数**：`core/prompt_strategy.py::generate_prompt_by_request()`
2. **策略工厂**：`PromptStrategyFactory.get_strategy(mode)`
3. **策略实现**：
   - 轻松模式：`EasyModePromptStrategy.generate_prompt()`
   - 大师模式：`MasterModePromptStrategy.generate_prompt()`

#### 6.1.3 提示词模板结构

**基础模板**（`BASE_PROMPT_TEMPLATE`）：
```
将用户人物从原图中进行干净、精细的抠图，保持人物五官特征、脸型轮廓、发型、肤色和整体形象高度一致。
增强脸部一致性，确保与原图相同的面部特征、比例与辨识度。
进行适度去除皮肤瑕疵，自然美颜但不过度，保持真实质感。
人物头部角度必须自然稳定，禁止生成正90度侧脸或极端侧脸。
确保手部结构正常，手指数量正确，不得生成多余手指、六根手指、畸形手部或不自然的手势。
{scene_description}，使人物与背景自然融合：光影一致、色彩统一、景深协调，整体呈现照片级超写实风格。

{clothing_description}

人物姿势可根据场景做自然变化，但必须保持合理的人体结构和正常比例。
整体风格：超写实、高清、自然色调、真实空气感、柔和氛围光。
一次性生成四张不同构图和场景的高清照片，供选择。
```

**城市场景描述示例**（`CITY_SCENES`）：
- 东京：`"背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑"`
- 巴黎：`"背景场景：巴黎埃菲尔铁塔、卢浮宫、巴黎圣母院、凯旋门"`

**服装描述模板**（`CLOTHING_TEMPLATES`）：
- 轻松模式：`"人物服装：提供的服饰图片。"`
- 大师模式：`"人物服装风格：{style}，材质：{material}，色调：{color}，类型：{type}。"`

### 6.2 资源映射机制

#### 6.2.1 服装素材路径映射

**映射表位置**：`core/image_utils.py::CLOTHES_STYLE_MAPPING`

**映射规则**：
```python
样式ID格式：{gender}_{category}_{number}
- gender: male/female
- category: upper/lower/dress
- number: 01/02/03
```

**映射表结构**：
```python
CLOTHES_STYLE_MAPPING = {
    # 男上装
    "male_upper_01": "male_clothes.jpg",
    "male_upper_02": "male_clothes.jpg",
    "male_upper_03": "male_clothes.jpg",
    
    # 男下装
    "male_lower_01": "male_pants.jpg",
    "male_lower_02": "male_pants.jpg",
    "male_lower_03": "male_pants.jpg",
    
    # 女上装
    "female_upper_01": "female_clothes.jpg",
    "female_upper_02": "female_clothes.jpg",
    "female_upper_03": "female_clothes.jpg",
    
    # 女下装
    "female_lower_01": "female_pants.jpg",
    "female_lower_02": "female_pants.jpg",
    "female_lower_03": "female_pants.jpg",
    
    # 连衣裙
    "female_dress_01": "female_dress.jpg",
    "female_dress_02": "female_dress.jpg",
    "female_dress_03": "female_dress.jpg",
}
```

#### 6.2.2 素材文件路径结构
```
utils/pictures/clothes/
├── male/
│   ├── male_clothes.jpg    # 男上装素材
│   └── male_pants.jpg       # 男下装素材
└── female/
    ├── female_clothes.jpg   # 女上装素材
    ├── female_pants.jpg     # 女下装素材
    └── female_dress.jpg     # 连衣裙素材
```

#### 6.2.3 素材加载流程
```
1. 接收样式ID（如 "female_upper_01"）
    ↓
2. 查询映射表获取文件名（"female_clothes.jpg"）
    ↓
3. 根据性别确定目录（female/）
    ↓
4. 拼接完整路径（utils/pictures/clothes/female/female_clothes.jpg）
    ↓
5. 读取文件并转换为Base64
    ↓
6. 返回Base64编码（data:image/jpeg;base64,...）
```

**代码实现**：`core/image_utils.py::load_clothes_image()`

### 6.3 完整处理流程

#### 6.3.1 轻松模式流程
```
1. 用户上传原图 + 选择城市 + 选择服装样式ID
    ↓
2. 验证参数（性别与服装匹配）
    ↓
3. 生成提示词
    ├─ 获取城市场景描述："背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑"
    └─ 服装描述："人物服装：提供的服饰图片。"
    ↓
4. 加载素材图片
    ├─ 人物原图（前端上传）
    ├─ 上装图片（后端本地加载：female_upper_01 → female_clothes.jpg）
    └─ 下装图片（后端本地加载：female_lower_01 → female_pants.jpg）
    ↓
5. 调用火山豆包生图API
    ├─ 输入：[人物原图Base64, 上装Base64, 下装Base64]
    └─ 提示词：完整拼接后的提示词
    ↓
6. 流式推送生成结果
    ├─ 第1张：{"status": "generating", "index": 0, "base64": "..."}
    ├─ 第2张：{"status": "generating", "index": 1, "base64": "..."}
    ├─ 第3张：{"status": "generating", "index": 2, "base64": "..."}
    ├─ 第4张：{"status": "generating", "index": 3, "base64": "..."}
    └─ 完成：{"status": "completed", "message": "生成流程结束，共生成 4 张图片"}
```

#### 6.3.2 大师模式流程
```
1. 用户上传原图 + 选择城市 + 选择风格标签
    ↓
2. 验证参数（性别与类型匹配）
    ↓
3. 生成提示词
    ├─ 获取城市场景描述："背景场景：巴黎埃菲尔铁塔、卢浮宫、巴黎圣母院、凯旋门"
    └─ 服装描述："人物服装风格：法式优雅，材质：丝绸，色调：中性色调，类型：套装。"
    ↓
4. 准备输入图片
    └─ 仅人物原图（前端上传）
    ↓
5. 调用火山豆包生图API
    ├─ 输入：[人物原图Base64]
    └─ 提示词：完整拼接后的提示词（AI根据标签自动生成服装）
    ↓
6. 流式推送生成结果（同轻松模式）
```

---

## 七、错误码说明

| HTTP状态码 | 错误场景 | 错误信息示例 |
|-----------|---------|------------|
| 422 | 参数验证失败 | "参数验证失败" |
| 400 | 图片格式错误 | "输入图片格式不正确，请提供有效的Base64编码" |
| 400 | 图片约束不满足 | "输入图片不符合要求：图片大小超过限制" |
| 400 | 服装配置错误 | "男性不能选择连衣裙" |
| 404 | 素材文件不存在 | "服装图片文件不存在，请联系管理员" |
| 500 | 服务器内部错误 | "服务器内部错误" |

---

## 八、注意事项

1. **SSE 连接保持**：客户端需要保持连接直到收到 `completed` 或 `failed` 状态
2. **超时处理**：建议设置合理的超时时间（建议 60-120 秒）
3. **重试机制**：接口内部已实现最多 2 次重试
4. **图片大小**：建议上传图片大小控制在 5MB 以内，以提高处理速度
5. **并发限制**：建议控制并发请求数，避免服务器压力过大
6. **素材扩展**：如需添加新的服装样式，需要：
   - 在 `CLOTHES_STYLE_MAPPING` 中添加映射关系
   - 将素材文件放置到对应的目录（male/ 或 female/）
7. **城市扩展**：如需添加新城市，需要在 `core/prompt.py::CITY_SCENES` 中添加配置

---

## 九、前端接入示例

### 9.1 JavaScript (EventSource)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('data', JSON.stringify({
  city: "Tokyo",
  gender: "Female",
  mode: "Easy",
  clothes: {
    upperStyle: "female_upper_01",
    lowerStyle: "female_lower_01",
    dress: null
  }
}));

// 使用 fetch 发送请求
fetch('http://localhost:8123/createPictureStream', {
  method: 'POST',
  body: formData
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  function readStream() {
    reader.read().then(({ done, value }) => {
      if (done) {
        console.log('Stream complete');
        return;
      }
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');
      
      lines.forEach(line => {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.substring(6));
          
          if (data.status === 'generating') {
            console.log(`收到第 ${data.index + 1} 张图片`);
            // 显示图片：data.base64
          } else if (data.status === 'completed') {
            console.log(data.message);
          } else if (data.status === 'failed') {
            console.error(data.message);
          }
        }
      });
      
      readStream();
    });
  }
  
  readStream();
})
.catch(error => {
  console.error('Error:', error);
});
```

---

## 十、相关文件路径

| 功能模块 | 文件路径 |
|---------|---------|
| 接口定义 | `journey_poster.py::create_picture_stream()` |
| 请求模型 | `model/createPictureReq.py::CreatePictureRequest` |
| 响应模型 | `model/createPictureResp.py::ImageStreamEvent` |
| 业务逻辑 | `service/generation_Image.py::DoubaoImages` |
| 提示词策略 | `core/prompt_strategy.py` |
| 提示词模板 | `core/prompt.py` |
| 图片工具 | `core/image_utils.py` |
| 枚举定义 | `core/enum.py` |
| 服装素材 | `utils/pictures/clothes/` |
