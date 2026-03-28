from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Config Schemas ====================


class ExportSettings(BaseModel):
    """导出设置配置"""

    format: str = "mp4"
    resolution: str = "1080p"
    fps: int = 30
    quality: str = "high"


class AIGenerationParams(BaseModel):
    """AI生成参数配置"""

    model: str = "stable-diffusion"
    steps: int = 30
    cfg_scale: float = 7.5
    sampler: str = "euler_a"


class RenderSettings(BaseModel):
    """渲染设置配置"""

    max_concurrent: int = 3
    timeout_seconds: int = 600
    temp_dir: str = "./temp"


class TranslationConfig(BaseModel):
    """翻译服务配置"""

    # DeepL 配置
    deepl_enabled: bool = True
    deepl_primary_key: Optional[str] = None
    deepl_backup_key: Optional[str] = None

    # Google 翻译配置
    google_enabled: bool = True

    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0

    # 超时设置（秒）
    timeout: int = 30

    # HTML 标签处理
    tag_handling: str = "html"
    splitting_tags: str = "<br>"

    class Config:
        from_attributes = True


class ConfigCreate(BaseModel):
    """创建配置请求"""

    key: str = Field(..., max_length=200)
    value: Any = None
    value_type: str = Field(default="string", max_length=50)
    group: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = None
    is_secret: bool = False


class ConfigUpdate(BaseModel):
    """更新配置请求"""

    value: Optional[Any] = None
    value_type: Optional[str] = Field(None, max_length=50)
    group: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = None
    is_secret: Optional[bool] = None
    is_active: Optional[bool] = None


class ConfigResponse(BaseModel):
    """配置响应"""

    id: int
    key: str
    value: Any
    value_type: Optional[str] = None
    group: Optional[str] = None
    remark: Optional[str] = None
    is_secret: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigListResponse(BaseModel):
    """配置列表响应"""

    items: List[ConfigResponse]
    total: int


class ConfigValueResponse(BaseModel):
    """简化的配置值响应 (仅返回值)"""

    key: str
    value: Any
    value_type: Optional[str] = None


class ConfigBatchRequest(BaseModel):
    """批量获取配置请求"""

    keys: List[str]


class ConfigBatchResponse(BaseModel):
    """批量获取配置响应"""

    configs: Dict[str, Any]
