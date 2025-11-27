# 流式图片生成测试指南

## 测试文件说明

### 1. `test_stream_simple.py` - 简单测试（推荐）
直接测试豆包 API 的流式返回功能，不依赖其他业务逻辑。

**特点：**
- 使用固定的测试提示词
- 使用 `input_demo.jpeg` 作为输入图片
- 直接调用豆包 API
- 保存生成的图片到 `utils/pictures/output/` 目录

### 2. `test_stream_image.py` - 完整测试
测试完整的业务逻辑，包括提示词拼接和 LLMModel 类。

**特点：**
- 使用 `BASE_PROMPT_TEMPLATE` 和城市场景配置
- 调用 `LLMModel.createPictureBySeedReam()` 方法
- 测试完整的业务流程

## 运行测试

### 前置条件

1. **确保环境变量已配置**（`.env` 文件）：
```env
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_API_KEY=your_api_key_here
```

2. **确保测试图片存在**：
```
d:\DidaCode\journeyposter\utils\pictures\input_demo.jpeg
```

3. **安装依赖**：
```bash
pip install volcengine-python-sdk[ark]
pip install python-dotenv
pip install Pillow
```

### 运行简单测试（推荐先运行这个）

```bash
cd d:\DidaCode\journeyposter
python test_stream_simple.py
```

**预期输出：**
```
============================================================
简单测试流式图片生成
============================================================

1. 测试提示词:
一位亚洲女性，自然美颜，真实质感。
...

2. 加载测试图片: d:\DidaCode\journeyposter\utils\pictures\input_demo.jpeg
   ✓ 图片加载成功，大小: 1.24MB

3. 调用豆包生图 API
   - Base URL: https://ark.cn-beijing.volces.com/api/v3
   - API Key: 已设置
   - 模型: doubao-seedream-4-0-250828
   - 生成数量: 4 张
   - 响应格式: b64_json
   - 流式: True

4. 接收流式响应:
   ✓ 接收图片 1: 2.35MB
   ✓ 接收图片 2: 2.41MB
   ✓ 接收图片 3: 2.38MB
   ✓ 接收图片 4: 2.42MB
   ✓ 生成完成

5. 整理图片数据:
   ✓ 图片 1 已添加
   ✓ 图片 2 已添加
   ✓ 图片 3 已添加
   ✓ 图片 4 已添加

   总计生成: 4 张图片

6. 保存生成的图片:
   ✓ 图片 1 已保存: d:\DidaCode\journeyposter\utils\pictures\output\test_output_1.png (2.35MB)
   ✓ 图片 2 已保存: d:\DidaCode\journeyposter\utils\pictures\output\test_output_2.png (2.41MB)
   ✓ 图片 3 已保存: d:\DidaCode\journeyposter\utils\pictures\output\test_output_3.png (2.38MB)
   ✓ 图片 4 已保存: d:\DidaCode\journeyposter\utils\pictures\output\test_output_4.png (2.42MB)

============================================================
测试成功完成！
============================================================
```

### 运行完整测试

```bash
cd d:\DidaCode\journeyposter
python test_stream_image.py
```

## 测试要点

### 1. 流式事件类型
- `image_generation.partial_image`: 接收图片 Base64 数据（关键）
- `image_generation.partial_succeeded`: 图片生成成功（URL 模式）
- `image_generation.partial_failed`: 生成失败
- `image_generation.completed`: 生成完成

### 2. 验证内容
- ✅ 是否成功接收 4 张图片
- ✅ 每张图片的 Base64 数据是否完整
- ✅ 图片是否能正确保存为文件
- ✅ 图片大小是否合理（一般 2-3MB）

### 3. 常见问题

**问题1：API Key 未设置**
```
✗ 测试失败: API key is required
```
解决：检查 `.env` 文件中的 `LLM_API_KEY`

**问题2：图片加载失败**
```
✗ 图片加载失败: [Errno 2] No such file or directory
```
解决：确保 `input_demo.jpeg` 文件存在

**问题3：生成图片数量不足**
```
期望生成4张图片，实际生成2张
```
解决：检查 API 配额或网络连接

## 输出文件位置

生成的图片保存在：
```
d:\DidaCode\journeyposter\utils\pictures\output\
├── test_output_1.png
├── test_output_2.png
├── test_output_3.png
└── test_output_4.png
```

## 下一步

测试成功后，可以：
1. 检查生成的图片质量
2. 调整提示词参数
3. 测试不同的输入图片
4. 集成到完整的 API 接口中
