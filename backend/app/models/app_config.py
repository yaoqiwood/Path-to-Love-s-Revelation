# 系统配置数据模型

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime

from ..core.database import Base


class AppConfig(Base):
    """
    系统配置模型
    用于存储各种自定义配置项，value 支持 JSON 格式
    """

    __tablename__ = "app_configs"

    id = Column(BigInteger, primary_key=True, index=True)

    # 配置键 (唯一)
    key = Column(String(200), nullable=False, unique=True, index=True)
    """ 配置键名, 如 'site.name', 'feature.enable_ai' """

    # 配置值 (JSON格式存储，支持各种类型)
    value = Column(JSON, nullable=True)
    """
    配置值，支持多种类型:
    - 字符串: "hello"
    - 数字: 123 or 3.14
    - 布尔: true/false
    - 数组: ["a", "b", "c"]
    - 对象: {"name": "test", "enabled": true}
    """

    # 值类型提示 (可选，用于前端展示和反序列化)
    value_type = Column(String(50), nullable=True, default="string")
    """
    值类型提示:
    - string: 字符串
    - number: 数字
    - boolean: 布尔值
    - json: JSON对象/数组
    - pydantic:ClassName: Pydantic模型类名
    """

    # 分组/命名空间
    group = Column(String(100), nullable=True, index=True)
    """ 配置分组, 如 'system', 'feature', 'ai', 'render' """

    # 备注说明
    remark = Column(Text, nullable=True)
    """ 配置项说明 """

    # 是否加密存储 (敏感信息)
    is_secret = Column(Boolean, default=False)
    """ 是否为敏感配置 (如API密钥)，获取时可能需要特殊权限 """

    # 是否启用
    is_active = Column(Boolean, default=True)
    """ 是否启用此配置 """

    # 时间相关
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.utcnow)

    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<AppConfig(key='{self.key}', group='{self.group}')>"


"""
使用示例:

1. 简单字符串配置:
   key: "site.name"
   value: "In Grace"
   value_type: "string"

2. 布尔开关:
   key: "feature.enable_ai_generation"
   value: true
   value_type: "boolean"

3. 数字配置:
   key: "render.max_concurrent_tasks"
   value: 5
   value_type: "number"

4. JSON对象配置:
   key: "ai.default_params"
   value: {"model": "stable-diffusion", "steps": 30, "cfg_scale": 7.5}
   value_type: "json"

5. Pydantic模型配置 (可反序列化):
   key: "export.default_settings"
   value: {"format": "mp4", "resolution": "1080p", "fps": 30}
   value_type: "pydantic:ExportSettings"
"""
