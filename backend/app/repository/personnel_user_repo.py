from typing import Optional

from sqlalchemy import String, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.personnel_user import PersonnelUser


class PersonnelUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_stmt(self, include_deleted: bool = False):
        stmt = select(PersonnelUser)
        if not include_deleted:
            stmt = stmt.where(PersonnelUser.is_deleted.is_(False))
        return stmt

    async def create(self, personnel: PersonnelUser) -> PersonnelUser:
        self.db.add(personnel)
        await self.db.flush()
        await self.db.refresh(personnel)
        return personnel

    async def get_by_id(
        self, personnel_id: str, include_deleted: bool = False
    ) -> Optional[PersonnelUser]:
        result = await self.db.execute(
            self._base_stmt(include_deleted).where(PersonnelUser.id == personnel_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        keyword: Optional[str],
        review_status: Optional[str],
        page: int,
        page_size: int,
        include_deleted: bool = False,
    ) -> tuple[list[PersonnelUser], int]:
        stmt = self._base_stmt(include_deleted)

        if review_status and review_status != "all":
            stmt = stmt.where(PersonnelUser.review_status == review_status)

        if keyword:
            like_value = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    PersonnelUser.name.like(like_value),
                    PersonnelUser.nickname.like(like_value),
                    PersonnelUser.mobile.like(like_value),
                    PersonnelUser.mbti.like(like_value),
                    PersonnelUser.passcode.like(like_value),
                    PersonnelUser.person_id.cast(String).like(like_value),
                )
            )

        total_result = await self.db.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        )
        total = total_result.scalar_one()

        data_result = await self.db.execute(
            stmt.order_by(PersonnelUser.person_id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(data_result.scalars().all()), total

    async def get_stats(self) -> dict:
        result = await self.db.execute(
            select(
                func.count().label("total"),
                func.sum(PersonnelUser.review_status == "pending").label("pending"),
                func.sum(PersonnelUser.review_status == "approved").label("approved"),
                func.sum(PersonnelUser.review_status == "rejected").label("rejected"),
            ).where(PersonnelUser.is_deleted.is_(False))
        )
        row = result.one()
        return {
            "total": int(row.total or 0),
            "pending": int(row.pending or 0),
            "approved": int(row.approved or 0),
            "rejected": int(row.rejected or 0),
        }

    async def get_by_person_id(self, person_id: int) -> Optional[PersonnelUser]:
        result = await self.db.execute(
            select(PersonnelUser).where(PersonnelUser.person_id == person_id)
        )
        return result.scalar_one_or_none()

    async def get_by_mobile(self, mobile: str) -> Optional[PersonnelUser]:
        result = await self.db.execute(
            select(PersonnelUser).where(PersonnelUser.mobile == mobile)
        )
        return result.scalar_one_or_none()

    async def get_by_passcode(self, passcode: str) -> Optional[PersonnelUser]:
        result = await self.db.execute(
            select(PersonnelUser).where(PersonnelUser.passcode == passcode)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: str, include_deleted: bool = False
    ) -> Optional[PersonnelUser]:
        result = await self.db.execute(
            self._base_stmt(include_deleted).where(PersonnelUser.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_max_person_id(self) -> Optional[int]:
        result = await self.db.execute(select(func.max(PersonnelUser.person_id)))
        return result.scalar_one_or_none()

    async def update(self, personnel: PersonnelUser, fields: dict) -> PersonnelUser:
        for key, value in fields.items():
            setattr(personnel, key, value)
        await self.db.flush()
        await self.db.refresh(personnel)
        return personnel
