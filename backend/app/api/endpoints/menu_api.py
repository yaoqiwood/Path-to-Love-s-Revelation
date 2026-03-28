# 菜单管理API端点

from typing import List, Optional
from fastapi import APIRouter, Request

from app.core.log_decorator import log_operate
from app.schemas.user_schema import MenuCreate, MenuUpdate, MenuResponse
from app.api.deps import CurrentUser, CurrentSuperUser
from app.services import MenuServiceDep

router = APIRouter()


# ==================== 菜单树 ====================


@router.get("/tree", response_model=List[MenuResponse])
async def get_menu_tree(
    current_user: CurrentUser,
    service: MenuServiceDep,
):
    """获取菜单树形结构"""
    return await service.get_menu_tree()


# ==================== 菜单列表 (平铺) ====================


@router.get("/", response_model=List[MenuResponse])
async def list_menus(
    current_user: CurrentUser,
    service: MenuServiceDep,
    menu_name: Optional[str] = None,
    menu_type: Optional[str] = None,
):
    """获取菜单列表（平铺，支持筛选）"""
    return await service.list_menus(menu_name, menu_type)


# ==================== 菜单详情 ====================


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(
    current_user: CurrentUser,
    service: MenuServiceDep,
    menu_id: int,
):
    """获取菜单详情"""
    return await service.get_menu(menu_id)


# ==================== 新增菜单 ====================


@router.post("/", response_model=MenuResponse)
@log_operate(title="新增菜单", business_type=1)
async def create_menu(
    request: Request,
    current_user: CurrentSuperUser,
    service: MenuServiceDep,
    data: MenuCreate,
):
    """新增菜单"""
    return await service.create_menu(data, current_user.username)


# ==================== 更新菜单 ====================


@router.put("/{menu_id}", response_model=MenuResponse)
@log_operate(title="更新菜单", business_type=2)
async def update_menu(
    request: Request,
    current_user: CurrentSuperUser,
    service: MenuServiceDep,
    menu_id: int,
    data: MenuUpdate,
):
    """更新菜单"""
    return await service.update_menu(menu_id, data, current_user.username)


# ==================== 删除菜单 ====================


@router.delete("/{menu_id}")
@log_operate(title="删除菜单", business_type=3)
async def delete_menu(
    request: Request,
    current_user: CurrentSuperUser,
    service: MenuServiceDep,
    menu_id: int,
):
    """删除菜单（同时删除子菜单）"""
    return await service.delete_menu(menu_id)
