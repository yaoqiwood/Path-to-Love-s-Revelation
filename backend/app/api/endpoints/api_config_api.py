# 系统配置API端点

from typing import Optional
from fastapi import APIRouter, Query, Request, status

from app.schemas.app_config_schema import (
    ConfigCreate,
    ConfigUpdate,
    ConfigResponse,
    ConfigListResponse,
    ConfigValueResponse,
    ConfigBatchRequest,
    ConfigBatchResponse,
)
from app.services import AppConfigApiServiceDep
from app.api.deps import CurrentUser, CurrentSuperUser
from app.core.log_decorator import log_operate

router = APIRouter()


# ==================== API端点 ====================


@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
@log_operate(title="创建配置", business_type=1)
async def create_config(
    request: Request,
    config_data: ConfigCreate,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """创建配置项"""
    return await service.create_config(config_data, user_id=current_user.id)


@router.get("/", response_model=ConfigListResponse)
async def list_configs(
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
    group: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_secrets: bool = Query(False, description="是否显示敏感配置的真实值"),
):
    """获取配置列表"""
    return await service.list_configs(
        group=group, search=search, is_active=is_active, include_secrets=include_secrets
    )


@router.get("/groups")
async def list_config_groups(
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """获取所有配置分组"""
    return await service.list_groups()


@router.get("/key/{key}", response_model=ConfigValueResponse)
async def get_config_by_key(
    key: str,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
    deserialize: bool = Query(False, description="是否反序列化为Pydantic模型"),
):
    """通过键获取配置值"""
    return await service.get_config_by_key(key, deserialize=deserialize)


@router.post("/batch", response_model=ConfigBatchResponse)
async def get_configs_batch(
    batch_request: ConfigBatchRequest,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """批量获取配置值"""
    return await service.get_configs_batch(batch_request)


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: int,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """获取配置详情"""
    return await service.get_config(config_id)


@router.put("/{config_id}", response_model=ConfigResponse)
@log_operate(title="更新配置", business_type=2)
async def update_config(
    request: Request,
    config_id: int,
    config_data: ConfigUpdate,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """更新配置"""
    return await service.update_config(config_id, config_data, user_id=current_user.id)


@router.put("/key/{key}", response_model=ConfigResponse)
async def update_config_by_key(
    key: str,
    config_data: ConfigUpdate,
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """通过键更新配置"""
    return await service.update_config_by_key(key, config_data, user_id=current_user.id)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_operate(title="删除配置", business_type=3)
async def delete_config(
    request: Request,
    config_id: int,
    current_user: CurrentSuperUser,
    service: AppConfigApiServiceDep,
):
    """删除配置 (仅管理员)"""
    await service.delete_config(config_id)


# ==================== 缓存管理端点 ====================


@router.post("/cache/refresh")
async def refresh_config_cache(
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
    key: Optional[str] = None,
    group: Optional[str] = None,
):
    """刷新配置缓存"""
    return await service.refresh_cache(key=key, group=group)


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: CurrentUser,
    service: AppConfigApiServiceDep,
):
    """获取缓存统计信息"""
    return await service.get_cache_stats()
