from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import SystemMenu


class MenuRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, menu_name: Optional[str] = None, menu_type: Optional[str] = None
    ) -> List[SystemMenu]:
        stmt = select(SystemMenu).order_by(SystemMenu.menu_sort)

        if menu_name:
            stmt = stmt.where(SystemMenu.menu_name.like(f"%{menu_name}%"))
        if menu_type:
            stmt = stmt.where(SystemMenu.menu_type == menu_type)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, menu_id: int) -> Optional[SystemMenu]:
        result = await self.db.execute(
            select(SystemMenu).where(SystemMenu.id == menu_id)
        )
        return result.scalar_one_or_none()

    async def get_children(self, pid: int) -> List[SystemMenu]:
        result = await self.db.execute(select(SystemMenu).where(SystemMenu.pid == pid))
        return list(result.scalars().all())

    async def create(self, menu: SystemMenu) -> SystemMenu:
        self.db.add(menu)
        await self.db.flush()
        await self.db.refresh(menu)
        return menu

    async def update(self, menu: SystemMenu, update_fields: dict) -> SystemMenu:
        for field, value in update_fields.items():
            setattr(menu, field, value)
        await self.db.flush()
        await self.db.refresh(menu)
        return menu

    async def delete(self, menu: SystemMenu) -> None:
        await self.db.delete(menu)
        await self.db.flush()
