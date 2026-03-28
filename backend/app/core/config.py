# 后端核心配置

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


# 获取当前环境变量指明的环境（默认开发）
ENV = os.getenv("APP_ENV", "development")

# 根据环境决定加载哪个 .env 文件，如果存在基础的 .env 也会一并加载（后者覆盖前者，或者只用特定的）
# 这里我们用列表按优先级加载：先加载基础 .env，再加载 .env.{ENV}
env_files = (".env", f".env.{ENV}")


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基本信息
    APP_NAME: str = "创意资产管理后台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API配置
    API_PREFIX: str = "/api"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8011

    # 数据库配置 - MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "creative_tools"

    @property
    def MYSQL_DATABASE_URL(self) -> str:
        url = f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        print(f"MYSQL_DATABASE_URL: {url}")
        return url

    @property
    def MYSQL_SYNC_DATABASE_URL(self) -> str:
        """同步数据库 URL（供 Celery worker 等同步上下文使用）"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"


    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        print(f"REDIS_URL: {url}")
        return url

    # 文件存储配置
    STORAGE_PATH: str = "./storage"
    EXPORT_OUTPUT_DIR: str = "./export"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_IMAGE_EXTENSIONS: list = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
    ALLOWED_VIDEO_EXTENSIONS: list = ["mp4", "avi", "mov", "mkv", "webm"]
    ALLOWED_AUDIO_EXTENSIONS: list = ["mp3", "wav", "ogg", "m4a", "aac", "flac"]

    # AI服务配置
    REPLICATE_API_TOKEN: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None

    # AI素材图生成配置
    IMAGINE_GEN_PROVIDER: str = (
        "lemon"  # 当前使用的提供商: lemon / grok / runway / pika
    )
    LEMON_API_KEY: Optional[str] = (
        "sk-9eKFGIXdwjbJTZHj1mmPXXq33MSPK50LdO84fg0IlfooUiSm"  # lemon API Key
    )
    LEMON_BASE_URL: str = "https://new.lemonapi.site"
    LEMON_REQUEST_TIMEOUT: int = 600  # 最大请求等待时长
    LEMON_IMAGINE_POLL_INTERVAL: int = 5  # 轮询间隔（秒）
    LEMON_IMAGINE_POLL_TIMEOUT: int = 600  # 最大等待（秒）

    # Mumu 中转站配置
    MUMU_API_KEY: Optional[str] = "sk-mwgXnQs1y94Xn8A4iSMZSD2rya48Ue8DTrP2mMl5ucylNCwD"
    MUMU_BASE_URL: str = "https://api.mumuverse.space"
    MUMU_REQUEST_TIMEOUT: int = 600

    # Kie 中转站配置
    KIE_API_KEY: Optional[str] = "b916034fe196caed38199c3d1bb8bc51"
    KIE_BASE_URL: str = "https://api.kie.ai"
    KIE_UPLOAD_URL: str = "https://kieai.redpandaai.co/api/file-base64-upload"
    KIE_REQUEST_TIMEOUT: int = 600

    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # 日志配置
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: str = "./logs"
    LOG_FILENAME: str = "app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_ENABLE_CONSOLE: bool = True
    LOG_ENABLE_FILE: bool = True
    LOG_USE_JSON: bool = False  # 是否使用JSON格式输出

    # MinIO 对象存储配置
    MINIO_ENABLED: bool = False  # 是否启用 MinIO 存储
    MINIO_ASYNC_UPLOAD: bool = True  # True=异步上传(需Celery), False=同步上传
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "creative-assets"
    MINIO_SECURE: bool = False  # True for HTTPS

    # 飞书机器人配置 - 异常告警
    FEISHU_ENABLED: bool = False
    FEISHU_WEBHOOK_TOKEN: str = ""
    FEISHU_SECRET_KEY: str = ""

    # 飞书机器人配置 - 一般通知
    FEISHU_NOTICE_ENABLED: bool = False
    FEISHU_NOTICE_WEBHOOK_TOKEN: str = ""
    FEISHU_NOTICE_SECRET_KEY: str = ""

    # 代理配置
    LOCAL_HTTP_PROXY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=env_files,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# 创建全局配置实例
settings = Settings()
