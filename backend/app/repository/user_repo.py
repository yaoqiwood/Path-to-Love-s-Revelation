# 用户数据访问层

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.user import SystemUser, SystemRole, SystemMenu


class UserRepository:
    """用户 CRUD 操作"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---- SystemUser ----

    async def create(self, user: SystemUser) -> SystemUser:
        """创建用户"""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[SystemUser]:
        """根据 ID 查询"""
        result = await self.db.execute(
            select(SystemUser).where(SystemUser.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_active(self, user_id: int) -> Optional[SystemUser]:
        """根据 ID 查询（仅未删除）"""
        result = await self.db.execute(
            select(SystemUser).where(
                SystemUser.id == user_id, SystemUser.del_status == 0
            )
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[SystemUser]:
        """根据用户名查询"""
        result = await self.db.execute(
            select(SystemUser).where(SystemUser.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[SystemUser]:
        """根据邮箱查询"""
        result = await self.db.execute(
            select(SystemUser).where(SystemUser.email == email)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        username: Optional[str] = None,
        enable_status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[SystemUser], int]:
        """分页查询用户列表，返回 (items, total)"""
        stmt = select(SystemUser).where(SystemUser.del_status == 0)

        if username:
            stmt = stmt.where(SystemUser.username.like(f"%{username}%"))
        if enable_status is not None:
            stmt = stmt.where(SystemUser.enable_status == enable_status)

        # 总数
        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar_one()

        # 分页数据
        data_result = await self.db.execute(
            stmt.offset((page - 1) * page_size).limit(page_size)
        )
        items = data_result.scalars().all()

        return items, total

    async def update(self, user: SystemUser, **fields) -> SystemUser:
        """更新用户字段"""
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ---- SystemRole ----

    async def get_roles_by_ids(self, role_ids: List[int]) -> List[SystemRole]:
        """根据 ID 列表查询角色"""
        result = await self.db.execute(
            select(SystemRole).where(SystemRole.id.in_(role_ids))
        )
        return list(result.scalars().all())

    # ---- SystemMenu ----

    async def get_all_visible_menus(self) -> List[SystemMenu]:
        """获取所有启用且可见的菜单（管理员用）"""
        result = await self.db.execute(
            select(SystemMenu)
            .where(
                SystemMenu.menu_type.in_(["M", "C"]),
                SystemMenu.enable_status == 1,
                SystemMenu.show_status == 1,
            )
            .order_by(SystemMenu.menu_sort)
        )
        return list(result.scalars().all())

    async def get_menus_by_ids(self, menu_ids: set) -> List[SystemMenu]:
        """根据 ID 集合查询菜单"""
        result = await self.db.execute(
            select(SystemMenu).where(SystemMenu.id.in_(menu_ids))
        )
        return list(result.scalars().all())

    async def get_visible_menus_by_ids(self, menu_ids: set) -> List[SystemMenu]:
        """根据 ID 集合查询可见菜单"""
        result = await self.db.execute(
            select(SystemMenu).where(
                SystemMenu.id.in_(menu_ids),
                SystemMenu.enable_status == 1,
                SystemMenu.show_status == 1,
            )
        )
        return list(result.scalars().all())

    async def get_menus_by_role_ids(self, role_ids: List[int]) -> List[SystemMenu]:
        """根据角色 ID 列表查询关联的菜单"""
        from ..models.user import SystemRoleMenu

        result = await self.db.execute(
            select(SystemMenu)
            .join(SystemRoleMenu, SystemRoleMenu.menu_id == SystemMenu.id)
            .where(SystemRoleMenu.role_id.in_(role_ids))
        )
        return list(result.scalars().unique().all())
