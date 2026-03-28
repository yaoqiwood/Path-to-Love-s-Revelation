"""
配置管理服务
- AppConfigService: 同步版本，供 Celery worker 等同步上下文使用
- AppConfigApiService: 异步 API 业务逻辑（依赖 ConfigRepository），供 FastAPI 端点使用
"""

import json
from typing import Optional, Any, TypeVar, Type, Dict, Annotated
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.app_config import AppConfig
from app.core.database import get_db, get_redis
from app.core.logging import get_logger
from app.repository import AppConfigRepository
from app.schemas.app_config_schema import (
    ConfigCreate,
    ConfigUpdate,
    ConfigListResponse,
    ConfigValueResponse,
    ConfigBatchRequest,
    ConfigBatchResponse,
)

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

CACHE_PREFIX = "app_config:"
DEFAULT_TTL = 3600 * 24  # 24小时

# ==================== Pydantic 模型注册表 ====================

_pydantic_registry: dict[str, Type[BaseModel]] = {}


def register_pydantic_model(name: str, model_class: Type[BaseModel]):
    """注册 Pydantic 模型到注册表"""
    _pydantic_registry[name] = model_class


def get_pydantic_model(name: str) -> Optional[Type[BaseModel]]:
    """获取已注册的 Pydantic 模型"""
    return _pydantic_registry.get(name)


# 注册预定义模型
from app.schemas.app_config_schema import (
    ExportSettings,
    AIGenerationParams,
    RenderSettings,
    TranslationConfig,
)

register_pydantic_model("ExportSettings", ExportSettings)
register_pydantic_model("AIGenerationParams", AIGenerationParams)
register_pydantic_model("RenderSettings", RenderSettings)
register_pydantic_model("TranslationConfig", TranslationConfig)


# ==================== 工具函数 ====================


def deserialize_value(value: Any, value_type: Optional[str]) -> Any:
    """根据 value_type 反序列化配置值"""
    if value is None or value_type is None:
        return value

    if value_type.startswith("pydantic:"):
        model_name = value_type.replace("pydantic:", "")
        model_class = get_pydantic_model(model_name)
        if model_class and isinstance(value, dict):
            try:
                return model_class.model_validate(value)
            except Exception as e:
                logger.warning(f"Failed to deserialize to {model_name}: {e}")
                return value

    return value


def mask_secret_value(value: Any) -> str:
    """掩码敏感值"""
    if value is None:
        return "***"
    if isinstance(value, str):
        if len(value) <= 4:
            return "***"
        return value[:2] + "***" + value[-2:]
    return "***"


# ==================== 同步 AppConfigService（供 Celery worker 使用）====================


class AppConfigService:
    """同步配置服务，供 Celery 渲染/翻译等同步上下文使用（带 Redis 缓存）"""

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        if redis_client:
            self.redis_client = redis_client
        else:
            try:
                from app.core.database import get_redis_sync

                self.redis_client = get_redis_sync()
            except (RuntimeError, ImportError):
                self.redis_client = None

    @staticmethod
    def _get_cache_key(key: str) -> str:
        return f"{CACHE_PREFIX}{key}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从 Redis 同步读取缓存"""
        if not self.redis_client:
            return None
        try:
            data = self.redis_client.get(self._get_cache_key(key))
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"同步读取缓存失败 {key}: {str(e)}")
        return None

    def _set_to_cache(self, key: str, value: Any, ttl: int = None):
        """同步写入 Redis 缓存"""
        if not self.redis_client:
            return
        try:
            data = json.dumps(value, ensure_ascii=False)
            self.redis_client.setex(self._get_cache_key(key), ttl or DEFAULT_TTL, data)
        except Exception as e:
            logger.error(f"同步写入缓存失败 {key}: {str(e)}")

    def get_sync(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """获取配置值（优先从缓存读取）"""
        # 优先从缓存读取
        if use_cache:
            cached = self._get_from_cache(key)
            if cached is not None:
                return cached

        # 从数据库读取
        try:
            config = (
                self.db.query(AppConfig)
                .filter(AppConfig.key == key, AppConfig.is_active == True)
                .first()
            )
            if not config:
                return default

            value = config.value

            # 写入缓存
            if use_cache:
                self._set_to_cache(key, value)

            return value
        except Exception as e:
            logger.error(f"同步读取配置失败 {key}: {e}")
            return default

    def get_as_model_sync(
        self, key: str, model_class: Type[T], default: Optional[T] = None
    ) -> Optional[T]:
        """获取配置并反序列化为 Pydantic 模型"""
        value = self.get_sync(key)
        if value is None:
            return default
        try:
            if isinstance(value, dict):
                return model_class(**value)
            elif isinstance(value, str):
                return model_class(**json.loads(value))
            else:
                return default
        except Exception as e:
            logger.error(f"反序列化配置失败 {key}: {e}")
            return default

    def refresh_cache(self, key: Optional[str] = None):
        """刷新缓存（同步）"""
        if not self.redis_client:
            return
        try:
            if key:
                self.redis_client.delete(self._get_cache_key(key))
                self.get_sync(key, use_cache=True)
            else:
                # 清除所有配置缓存
                pattern = f"{CACHE_PREFIX}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"已同步清除 {len(keys)} 个配置缓存")
        except Exception as e:
            logger.error(f"同步刷新缓存失败: {str(e)}")


# ==================== AppConfigApiService（API 端点业务逻辑）====================


class AppConfigApiService:
    """异步配置 API 服务，供 FastAPI 端点使用"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AppConfigRepository(db)
        try:
            self.redis_client = get_redis()
        except RuntimeError:
            self.redis_client = None

    # ---- Redis 缓存 ----

    @staticmethod
    def _get_cache_key(key: str) -> str:
        return f"{CACHE_PREFIX}{key}"

    async def _get_from_cache(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            data = await self.redis_client.get(self._get_cache_key(key))
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"读取缓存失败 {key}: {str(e)}")
        return None

    async def _set_to_cache(self, key: str, value: Any, ttl: int = None):
        if not self.redis_client:
            return
        try:
            data = json.dumps(value, ensure_ascii=False)
            await self.redis_client.setex(
                self._get_cache_key(key), ttl or DEFAULT_TTL, data
            )
        except Exception as e:
            logger.error(f"写入缓存失败 {key}: {str(e)}")

    async def _delete_from_cache(self, key: str):
        if not self.redis_client:
            return
        try:
            await self.redis_client.delete(self._get_cache_key(key))
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {str(e)}")

    # ---- 异步配置读取（带缓存）----

    async def get(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """获取配置值（异步，带缓存）"""
        if use_cache:
            cached = await self._get_from_cache(key)
            if cached is not None:
                return cached

        config = await self.repo.get_by_key(key, active_only=True)
        if not config:
            return default

        value = config.value
        if use_cache:
            await self._set_to_cache(key, value)
        return value

    async def get_as_model(
        self,
        key: str,
        model_class: Type[T],
        default: Optional[T] = None,
        use_cache: bool = True,
    ) -> Optional[T]:
        """获取配置并反序列化为 Pydantic 模型"""
        value = await self.get(key, use_cache=use_cache)
        if value is None:
            return default
        try:
            if isinstance(value, dict):
                return model_class(**value)
            elif isinstance(value, str):
                return model_class(**json.loads(value))
            else:
                return default
        except Exception as e:
            logger.error(f"反序列化配置失败 {key}: {str(e)}")
            return default

    async def get_by_group(
        self, group: str, use_cache: bool = True, include_inactive: bool = False
    ) -> Dict[str, Any]:
        """获取分组下的所有配置"""
        cache_key = f"group:{group}"
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached is not None:
                return cached

        configs = await self.repo.get_by_group(group, include_inactive=include_inactive)
        result_dict: Dict[str, Any] = {}
        for config in configs:
            k = config.key
            if k.startswith(f"{group}."):
                k = k[len(group) + 1 :]
            result_dict[k] = config.value

        if use_cache:
            await self._set_to_cache(cache_key, result_dict)
        return result_dict

    async def set_value(
        self,
        key: str,
        value: Any,
        value_type: str = "json",
        group: Optional[str] = None,
        remark: Optional[str] = None,
        is_secret: bool = False,
    ) -> AppConfig:
        """设置配置值（创建或更新）"""
        config = await self.repo.get_by_key(key, active_only=False)
        if config:
            config = await self.repo.update(
                config,
                value=value,
                value_type=value_type,
                group=group,
                remark=remark,
                is_secret=is_secret,
            )
        else:
            config = AppConfig(
                key=key,
                value=value,
                value_type=value_type,
                group=group,
                remark=remark,
                is_secret=is_secret,
                is_active=True,
            )
            config = await self.repo.create(config)

        await self._delete_from_cache(key)
        if group:
            await self._delete_from_cache(f"group:{group}")
        return config

    # ---- CRUD（API 端点用）----

    async def create_config(self, config_data: ConfigCreate, user_id: int) -> AppConfig:
        """创建配置项"""
        existing = await self.repo.get_by_key(config_data.key, active_only=False)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置键已存在: {config_data.key}",
            )

        config = AppConfig(
            key=config_data.key,
            value=config_data.value,
            value_type=config_data.value_type,
            group=config_data.group,
            remark=config_data.remark,
            is_secret=config_data.is_secret,
            created_by=user_id,
        )
        config = await self.repo.create(config)
        logger.info(f"Config created: key={config.key}")
        return config

    async def get_config(self, config_id: int) -> AppConfig:
        """获取配置，不存在则抛 404"""
        config = await self.repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在"
            )
        return config

    async def get_config_by_key(
        self, key: str, deserialize: bool = False
    ) -> ConfigValueResponse:
        """通过键获取配置值"""
        config = await self.repo.get_by_key(key, active_only=True)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"配置不存在: {key}"
            )

        value = config.value
        value_type = config.value_type

        if deserialize and value_type:
            value = deserialize_value(value, value_type)

        return ConfigValueResponse(key=key, value=value, value_type=value_type)

    async def list_configs(
        self,
        group: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        include_secrets: bool = False,
    ) -> ConfigListResponse:
        """查询配置列表"""
        items, total = await self.repo.list(
            group=group, search=search, is_active=is_active
        )
        # 重要：不要直接修改 ORM 对象的 value，否则会被 session.commit() 写回数据库
        from app.schemas.app_config_schema import ConfigResponse

        response_items = []
        for config in items:
            value = config.value
            if not include_secrets and config.is_secret:
                value = mask_secret_value(value)
            response_items.append(
                ConfigResponse(
                    id=config.id,
                    key=config.key,
                    value=value,
                    value_type=config.value_type,
                    group=config.group,
                    remark=config.remark,
                    is_secret=config.is_secret,
                    is_active=config.is_active,
                    created_at=config.created_at,
                    updated_at=config.updated_at,
                )
            )
        return ConfigListResponse(items=response_items, total=total)

    async def list_groups(self) -> dict:
        """获取所有分组"""
        groups = await self.repo.list_groups()
        return {"groups": groups}

    async def get_configs_batch(
        self, request: ConfigBatchRequest
    ) -> ConfigBatchResponse:
        """批量获取配置值"""
        configs = await self.repo.get_batch(request.keys)
        result = {}
        for config in configs:
            if config.is_secret:
                result[config.key] = mask_secret_value(config.value)
            else:
                result[config.key] = config.value
        return ConfigBatchResponse(configs=result)

    async def update_config(
        self, config_id: int, config_data: ConfigUpdate, user_id: int
    ) -> AppConfig:
        """更新配置"""
        config = await self.get_config(config_id)
        update_data = config_data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        config = await self.repo.update(config, **update_data)
        logger.info(f"Config updated: key={config.key}")
        return config

    async def update_config_by_key(
        self, key: str, config_data: ConfigUpdate, user_id: int
    ) -> AppConfig:
        """通过键更新配置"""
        config = await self.repo.get_by_key(key, active_only=False)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"配置不存在: {key}"
            )
        update_data = config_data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        config = await self.repo.update(config, **update_data)
        logger.info(f"Config updated: key={config.key}")
        return config

    async def delete_config(self, config_id: int) -> None:
        """删除配置"""
        config = await self.get_config(config_id)
        await self.repo.delete(config)
        logger.info(f"Config deleted: key={config.key}")

    # ---- 缓存管理（API 端点用）----

    async def refresh_cache(
        self, key: Optional[str] = None, group: Optional[str] = None
    ) -> dict:
        """刷新缓存"""
        try:
            if key:
                await self._delete_from_cache(key)
                await self.get(key, use_cache=True)
                return {"message": f"已刷新配置缓存: {key}"}
            elif group:
                await self._delete_from_cache(f"group:{group}")
                await self.get_by_group(group, use_cache=True)
                return {"message": f"已刷新分组缓存: {group}"}
            else:
                if self.redis_client:
                    pattern = f"{CACHE_PREFIX}*"
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                return {"message": "已清除所有配置缓存"}
        except Exception as e:
            logger.error(f"刷新缓存失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"刷新缓存失败: {str(e)}",
            )

    async def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        try:
            if not self.redis_client:
                return {
                    "total_cached": 0,
                    "cache_prefix": CACHE_PREFIX,
                    "default_ttl": DEFAULT_TTL,
                }

            pattern = f"{CACHE_PREFIX}*"
            keys = await self.redis_client.keys(pattern)
            return {
                "total_cached": len(keys),
                "cache_prefix": CACHE_PREFIX,
                "default_ttl": DEFAULT_TTL,
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取缓存统计失败: {str(e)}",
            )


# ==================== 依赖注入 ====================


async def get_config_api_service(
    db: AsyncSession = Depends(get_db),
) -> AppConfigApiService:
    """FastAPI 依赖注入工厂"""
    return AppConfigApiService(db)


AppConfigApiServiceDep = Annotated[AppConfigApiService, Depends(get_config_api_service)]
