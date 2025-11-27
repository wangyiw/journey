import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env.dev')

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_URL")

# --- 这里必须填你在火山引擎控制台创建的推理接入点 ID ---
# 格式通常是 ep-2024xxxx-xxxxx
MODEL_ENDPOINT_ID = "ep-m-20251127211119-7fbfh"  # <--- 请务必修改这里！！！

print(f"正在测试连接...")
print(f"URL: {base_url}")
print(f"Model ID: {MODEL_ENDPOINT_ID}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

try:
    response = client.chat.completions.create(
        model=MODEL_ENDPOINT_ID,  
        messages=[
            {"role": "system", "content": "你是豆包。"},
            {"role": "user", "content": "你好，测试一下连接，请回复：连接成功。"},
        ],
    )
    print("\n✅ 调用成功！返回结果：")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n❌ 调用失败！详细报错如下：")
    print("-" * 30)
    print(e)
    print("-" * 30)
    
    # 简单的错误分析
    error_str = str(e)
    if "404" in error_str:
        print("💡 分析：404 错误通常意味着 Base URL 填错了（多写了路径），或者 Endpoint ID 不存在。")
    elif "400" in error_str:
        print("💡 分析：400 错误通常意味着 model 参数填错了，请检查是否使用了 ep-xxxx 格式的 ID。")
    elif "401" in error_str or "403" in error_str:
        print("💡 分析：API Key 错误或没有权限。")