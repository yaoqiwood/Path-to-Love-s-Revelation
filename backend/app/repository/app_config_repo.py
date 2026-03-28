# 配置数据访问层

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.models.app_config import AppConfig


class AppConfigRepository:
    """配置 CRUD 操作"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, config: AppConfig) -> AppConfig:
        """创建配置"""
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def get_by_id(self, config_id: int) -> Optional[AppConfig]:
        """根据 ID 查询"""
        result = await self.db.execute(
            select(AppConfig).where(AppConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_by_key(
        self, key: str, active_only: bool = True
    ) -> Optional[AppConfig]:
        """根据 key 查询"""
        stmt = select(AppConfig).where(AppConfig.key == key)
        if active_only:
            stmt = stmt.where(AppConfig.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        group: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> tuple[List[AppConfig], int]:
        """查询配置列表，返回 (items, total)"""
        stmt = select(AppConfig)

        if is_active is not None:
            stmt = stmt.where(AppConfig.is_active == is_active)
        if group:
            stmt = stmt.where(AppConfig.group == group)
        if search:
            stmt = stmt.where(AppConfig.key.ilike(f"%{search}%"))

        # 总数
        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar_one()

        # 数据
        data_result = await self.db.execute(
            stmt.order_by(AppConfig.group, AppConfig.key)
        )
        items = data_result.scalars().all()

        return items, total

    async def list_groups(self) -> List[str]:
        """获取所有活跃分组"""
        stmt = select(distinct(AppConfig.group)).where(
            AppConfig.group.isnot(None), AppConfig.is_active == True
        )
        result = await self.db.execute(stmt)
        return [g for g in result.scalars().all() if g]

    async def get_batch(self, keys: List[str]) -> List[AppConfig]:
        """批量查询"""
        result = await self.db.execute(
            select(AppConfig).where(
                AppConfig.key.in_(keys), AppConfig.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_by_group(
        self, group: str, include_inactive: bool = False
    ) -> List[AppConfig]:
        """获取分组下的所有配置"""
        stmt = select(AppConfig).where(AppConfig.group == group)
        if not include_inactive:
            stmt = stmt.where(AppConfig.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, config: AppConfig, **fields) -> AppConfig:
        """更新配置字段"""
        for key, value in fields.items():
            if value is not None:
                setattr(config, key, value)
        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def delete(self, config: AppConfig) -> None:
        """删除配置"""
        await self.db.delete(config)
        await self.db.flush()
