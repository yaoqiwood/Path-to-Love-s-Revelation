# 角色管理API端点

from typing import List, Optional
from fastapi import APIRouter, Request

from app.core.log_decorator import log_operate
from app.schemas.user_schema import RoleCreate, RoleUpdate, RoleResponse
from app.api.deps import CurrentUser, CurrentSuperUser
from app.services import RoleServiceDep

router = APIRouter()


# ==================== 角色列表 ====================


@router.get("/", response_model=dict)
async def list_roles(
    current_user: CurrentUser,
    service: RoleServiceDep,
    page: int = 1,
    page_size: int = 50,
    name: Optional[str] = None,
):
    """分页获取角色列表"""
    return await service.list_roles(page, page_size, name)


# ==================== 所有角色 (用于下拉选择) ====================


@router.get("/all", response_model=List[RoleResponse])
async def get_all_roles(
    current_user: CurrentUser,
    service: RoleServiceDep,
):
    """获取所有启用的角色（用于用户分配角色下拉）"""
    return await service.get_all_roles()


# ==================== 角色详情 ====================


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    current_user: CurrentUser,
    role_id: int,
    service: RoleServiceDep,
):
    """获取角色详情"""
    return await service.get_role(role_id)


# ==================== 新增角色 ====================


@router.post("/", response_model=RoleResponse)
@log_operate(title="新增角色", business_type=1)
async def create_role(
    request: Request,
    current_user: CurrentSuperUser,
    service: RoleServiceDep,
    data: RoleCreate,
):
    """新增角色"""
    return await service.create_role(data, current_user.username)


# ==================== 更新角色 ====================


@router.put("/{role_id}", response_model=RoleResponse)
@log_operate(title="更新角色", business_type=2)
async def update_role(
    request: Request,
    current_user: CurrentSuperUser,
    service: RoleServiceDep,
    role_id: int,
    data: RoleUpdate,
):
    """更新角色"""
    return await service.update_role(role_id, data, current_user.username)


# ==================== 删除角色 ====================


@router.delete("/{role_id}")
@log_operate(title="删除角色", business_type=3)
async def delete_role(
    request: Request,
    current_user: CurrentSuperUser,
    service: RoleServiceDep,
    role_id: int,
):
    """删除角色"""
    return await service.delete_role(role_id)


# ==================== 角色权限 (菜单) 管理 ====================


@router.get("/{role_id}/menus", response_model=List[int])
async def get_role_menus(
    current_user: CurrentUser,
    service: RoleServiceDep,
    role_id: int,
):
    """获取角色已分配的菜单ID列表"""
    return await service.get_role_menus(role_id)


@router.put("/{role_id}/menus")
@log_operate(title="更新角色权限", business_type=2)
async def set_role_menus(
    request: Request,
    current_user: CurrentSuperUser,
    service: RoleServiceDep,
    role_id: int,
    data: dict,
):
    """设置角色的菜单权限"""
    return await service.set_role_menus(role_id, data, current_user.username)
