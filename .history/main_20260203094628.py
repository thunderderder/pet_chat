import os
import base64
import httpx
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cat-backend")

app = FastAPI()

# 配置
API_KEY = "sk_56f40c3c_4711e351bc6e7b71802f7eaa888fbdf6ac9b"
# 优先使用环境变量，否则使用默认值
API_BASE_URL = os.getenv("API_BASE_URL", "https://student-api.ai-builders.space/backend")
# 是否忽略 SSL 验证（仅用于开发环境解决证书问题）
VERIFY_SSL = os.getenv("VERIFY_SSL", "False").lower() == "true"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    text: str
    image_url: str  # 返回图片的 data URI 用于前端展示

PROMPT = """你是一个幽默、温和、善意的“宠物读心师”。
请根据图片中猫或狗的表情、姿态、场景和氛围，
用**一句话**、**第一人称**、**轻松搞笑但不冒犯**的语气，
猜测“它此刻可能在想什么”。

输出要求：
1）只输出一-两句话，不要解释推理；
2）不要出现“可能”“大概”“也许”等不确定词；
3）不要给诊断、不要给饲养建议；
4）避免负面、恐惧或攻击性表述；
5）尽量口语化，适合分享到朋友圈。"""

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # 读取图片并转为 base64
    content = await file.read()
    base64_image = base64.b64encode(content).decode("utf-8")
    data_uri = f"data:{file.content_type};base64,{base64_image}"

    # 构造请求
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    payload = {
        "model": "gemini-2.5-pro",  # 使用多模态能力较强的模型
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri}
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    try:
        logger.info(f"Sending request to {API_BASE_URL}...")
        async with httpx.AsyncClient(verify=VERIFY_SSL, timeout=30.0, follow_redirects=True) as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            # Log the final URL if redirection happened
            if response.history:
                logger.info(f"Request was redirected to {response.url}")

            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                logger.error(f"Response Body: {response.text}")
                # Fallback / Mock logic for demo purposes if API fails
                return {
                    "text": "（模拟数据：API连接失败）铲屎的，虽然我不知道你在拍什么，但记得把美颜开最大！",
                    "image_url": data_uri,
                    "debug_info": f"API Error: {response.status_code}"
                }
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            logger.info("Successfully analyzed image")
            return {"text": answer, "image_url": data_uri}

    except Exception as e:
        logger.exception("Unexpected error during analysis")
        return {
            "text": "（模拟数据：网络错误）哎呀，网络好像断了，但我还是爱你的！",
            "image_url": data_uri,
            "debug_info": str(e)
        }

# 挂载静态文件
if not os.path.exists("static"):
    os.makedirs("static")
    
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
