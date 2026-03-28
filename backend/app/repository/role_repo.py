from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, func
from sqlalchemy.orm import selectinload

from app.models.user import SystemRole, SystemRoleMenu


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_roles(
        self, page: int, page_size: int, name: Optional[str] = None
    ) -> Tuple[List[SystemRole], int]:
        stmt = select(SystemRole).order_by(SystemRole.sort)
        if name:
            stmt = stmt.where(SystemRole.name.like(f"%{name}%"))

        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar_one()

        data_result = await self.db.execute(
            stmt.offset((page - 1) * page_size).limit(page_size)
        )
        roles = list(data_result.scalars().all())

        return roles, total

    async def get_all_enabled(self) -> List[SystemRole]:
        result = await self.db.execute(
            select(SystemRole)
            .where(SystemRole.enable_status == 1)
            .order_by(SystemRole.sort)
        )
        return list(result.scalars().all())

    async def get_by_id(
        self, role_id: int, include_users: bool = False, include_menus: bool = False
    ) -> Optional[SystemRole]:
        stmt = select(SystemRole).where(SystemRole.id == role_id)
        if include_users:
            stmt = stmt.options(selectinload(SystemRole.users))
        if include_menus:
            stmt = stmt.options(selectinload(SystemRole.menus))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[SystemRole]:
        result = await self.db.execute(
            select(SystemRole).where(SystemRole.code == code)
        )
        return result.scalar_one_or_none()

    async def create(self, role: SystemRole) -> SystemRole:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def update(self, role: SystemRole, update_fields: dict) -> SystemRole:
        for field, value in update_fields.items():
            setattr(role, field, value)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def delete(self, role: SystemRole) -> None:
        # 清除角色菜单关联
        await self.db.execute(
            sql_delete(SystemRoleMenu).where(SystemRoleMenu.role_id == role.id)
        )
        await self.db.delete(role)
        await self.db.flush()

    async def set_role_menus(
        self, role_id: int, menu_ids: List[int], role_menu_objects: List[SystemRoleMenu]
    ) -> None:
        # 清除旧的关联
        await self.db.execute(
            sql_delete(SystemRoleMenu).where(SystemRoleMenu.role_id == role_id)
        )

        # 添加新的关联
        for role_menu in role_menu_objects:
            self.db.add(role_menu)

        await self.db.flush()
