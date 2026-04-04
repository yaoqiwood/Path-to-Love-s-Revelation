from datetime import datetime
from typing import Optional

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.personnel_heart_message import PersonnelHeartMessage


class PersonnelHeartMessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _visible_conversation_stmt(self, conversation_key: str):
        return (
            select(
                PersonnelHeartMessage.id.label("id"),
                PersonnelHeartMessage.sender_record_id.label("sender_record_id"),
                PersonnelHeartMessage.receiver_record_id.label("receiver_record_id"),
                PersonnelHeartMessage.content.label("content"),
                PersonnelHeartMessage.created_at.label("created_at"),
            )
            .where(
                PersonnelHeartMessage.conversation_key == conversation_key,
                PersonnelHeartMessage.is_deleted.is_(False),
                PersonnelHeartMessage.message_scene.in_(["chat", "inbox"]),
                PersonnelHeartMessage.status != "revoked",
            )
        )

    async def list_visible_conversation_messages(
        self, conversation_key: str, since: Optional[datetime] = None
    ) -> list[dict]:
        stmt = self._visible_conversation_stmt(conversation_key)
        if since is not None:
            stmt = stmt.where(PersonnelHeartMessage.created_at > since)

        result = await self.db.execute(stmt.order_by(PersonnelHeartMessage.created_at.asc()))
        return [dict(row._mapping) for row in result]

    async def get_latest_visible_conversation_message(
        self, conversation_key: str
    ) -> Optional[dict]:
        result = await self.db.execute(
            self._visible_conversation_stmt(conversation_key)
            .order_by(desc(PersonnelHeartMessage.created_at))
            .limit(1)
        )
        row = result.first()
        return dict(row._mapping) if row else None

    async def list_visible_personnel_messages(self, personnel_id: str) -> list[dict]:
        result = await self.db.execute(
            select(
                PersonnelHeartMessage.id.label("id"),
                PersonnelHeartMessage.conversation_key.label("conversation_key"),
                PersonnelHeartMessage.sender_record_id.label("sender_record_id"),
                PersonnelHeartMessage.receiver_record_id.label("receiver_record_id"),
                PersonnelHeartMessage.content.label("content"),
                PersonnelHeartMessage.created_at.label("created_at"),
            ).where(
                or_(
                    PersonnelHeartMessage.sender_record_id == personnel_id,
                    PersonnelHeartMessage.receiver_record_id == personnel_id,
                ),
                PersonnelHeartMessage.is_deleted.is_(False),
                PersonnelHeartMessage.message_scene.in_(["chat", "inbox"]),
                PersonnelHeartMessage.status != "revoked",
            )
        )
        return [dict(row._mapping) for row in result]
