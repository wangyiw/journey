#!/bin/bash
# 豆包图片生成 API - cURL 示例
# 基于 test_stream_simple.py 生成

# 配置变量（请在 Apifox 中设置为环境变量）
API_KEY="your_api_key_here"
BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID="ep-m-20251127211119-7fbfh"

# 注意：image 参数需要是完整的 Base64 编码图片
# 这里使用一个示例 Base64（实际使用时需要替换为真实的图片 Base64）
IMAGE_BASE64="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="

# 提示词（来自 test_stream_simple.py）
PROMPT="一位亚洲男性，自然美颜，真实质感。
背景场景：东京涩谷十字路口、浅草寺、东京塔、新宿御苑（随机生成四种不同场景），使人物与背景自然融合：光影一致、色彩统一、景深协调，整体呈现照片级超写实风格。

人物服装：提供的服饰图片。

人物姿势可根据场景做自然变化，但必须保持合理的人体结构和正常比例。
整体风格：超写实、高清、自然色调、真实空气感、柔和氛围光。
一次性生成四张不同构图和场景的高清照片，供选择。"

# 发送请求
curl -X POST "${BASE_URL}/images/generations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "{
    \"model\": \"${MODEL_ID}\",
    \"prompt\": \"${PROMPT}\",
    \"image\": \"${IMAGE_BASE64}\",
    \"size\": \"2K\",
    \"sequential_image_generation\": \"auto\",
    \"sequential_image_generation_options\": {
      \"max_images\": 4
    },
    \"response_format\": \"b64_json\",
    \"stream\": true,
    \"watermark\": false
  }"

