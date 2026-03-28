# 活动参与者数据访问层

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.participant import Participant


class ParticipantRepository:
    """活动参与者 CRUD 操作"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, participant: Participant) -> Participant:
        """创建参与者"""
        self.db.add(participant)
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def get_by_id(self, participant_id: int) -> Optional[Participant]:
        """根据 ID 查询"""
        result = await self.db.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[Participant]:
        """根据永久Token查询"""
        result = await self.db.execute(
            select(Participant).where(Participant.permanent_token == token)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        participant_name: Optional[str] = None,
        gender: Optional[int] = None,
        mbti: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Participant], int]:
        """分页查询参与者列表，返回 (items, total)"""
        stmt = select(Participant)

        if participant_name:
            stmt = stmt.where(Participant.participant_name.like(f"%{participant_name}%"))
        if gender is not None:
            stmt = stmt.where(Participant.gender == gender)
        if mbti:
            stmt = stmt.where(Participant.mbti == mbti.upper())

        # 总数
        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar_one()

        # 分页数据
        data_result = await self.db.execute(
            stmt.order_by(Participant.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = data_result.scalars().all()

        return items, total

    async def update(self, participant: Participant, **fields) -> Participant:
        """更新参与者字段"""
        for key, value in fields.items():
            if value is not None:
                setattr(participant, key, value)
        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def delete(self, participant: Participant) -> None:
        """物理删除参与者"""
        await self.db.delete(participant)
        await self.db.flush()
