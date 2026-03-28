from typing import List, Optional, Annotated
from datetime import datetime
import uuid
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import SystemRole, SystemRoleMenu
from app.schemas.user_schema import RoleCreate, RoleUpdate, RoleResponse
from app.repository import RoleRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repo = RoleRepository(db)

    async def list_roles(
        self, page: int, page_size: int, name: Optional[str] = None
    ) -> dict:
        """分页获取角色列表"""
        roles, total = await self.repo.list_roles(page, page_size, name)

        return {
            "total": total,
            "items": [RoleResponse.model_validate(r) for r in roles],
        }

    async def get_all_roles(self) -> List[RoleResponse]:
        """获取所有启用的角色"""
        roles = await self.repo.get_all_enabled()
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_role(self, role_id: int) -> RoleResponse:
        """获取角色详情"""
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        return RoleResponse.model_validate(role)

    async def create_role(self, data: RoleCreate, username: str) -> RoleResponse:
        """新增角色"""
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(status_code=400, detail="角色编码已存在")

        role = SystemRole(
            name=data.name,
            code=data.code,
            sort=data.sort,
            remark=data.remark or "",
            enable_status=data.enable_status,
            create_time=datetime.now(),
            create_by=username,
        )
        role = await self.repo.create(role)
        return RoleResponse.model_validate(role)

    async def update_role(
        self, role_id: int, data: RoleUpdate, username: str
    ) -> RoleResponse:
        """更新角色"""
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")

        update_fields = data.model_dump(exclude_unset=True)
        update_fields["update_time"] = datetime.now()
        update_fields["update_by"] = username

        role = await self.repo.update(role, update_fields)
        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: int) -> dict:
        """删除角色"""
        role = await self.repo.get_by_id(role_id, include_users=True)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")

        # 过滤出未被软删除的活跃用户
        active_users = [user for user in role.users if user.del_status == 0]
        if active_users:
            raise HTTPException(status_code=400, detail="该角色下存在用户，不允许删除")

        # 清除所有遗留的用户关联（例如已软删除的用户），避免数据库外键约束报错
        role.users = []

        await self.repo.delete(role)
        return {"message": "删除成功"}

    async def get_role_menus(self, role_id: int) -> List[int]:
        """获取角色已分配的菜单ID列表"""
        role = await self.repo.get_by_id(role_id, include_menus=True)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")

        return [menu.id for menu in role.menus]

    async def set_role_menus(self, role_id: int, data: dict, username: str) -> dict:
        """设置角色的菜单权限"""
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")

        menu_ids = data.get("menu_ids", [])

        role_menu_objects = [
            SystemRoleMenu(
                id=str(uuid.uuid4()),
                role_id=role_id,
                menu_id=menu_id,
            )
            for menu_id in menu_ids
        ]

        await self.repo.set_role_menus(role_id, menu_ids, role_menu_objects)

        await self.repo.update(
            role, {"update_by": username, "update_time": datetime.now()}
        )

        return {"message": "权限设置成功"}


async def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
