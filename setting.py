import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional, List
from utils.logger import setup_logging
from concurrent.futures import ThreadPoolExecutor
import logging

ENV = os.getenv("ENV", "dev")

class Settings(BaseSettings):

    LLM_URL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_SCENE_ID: Optional[str] = None
    LLM_MODEL_CONFIG_URL: Optional[str] = None
    LLM_MODEL_CONFIG_FILE: Optional[str] = None

    LOG_LEVEL: str = "INFO" # "DEBUG" | "INFO"

    class Config:
        if ENV.lower() in ['test','TEST','sit','SIT']:
            env_file = ".env"
        elif ENV.lower() in ['prod','PROD','PRD','prd']:
            env_file = ".env.prd"
        else:
            env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"



settings = Settings()

# 创建线程池执行器，全局只需要一个
executor = ThreadPoolExecutor(max_workers=5)

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)
logger.info(f"当前环境ENV 变量->>>>>>>> {ENV} <<<<<<")

logger.info(f"LLM_URL: {settings.LLM_URL}")
# raise