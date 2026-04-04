from sqlalchemy import Boolean, Column, DateTime, Index, SmallInteger, String

from ..core.database import Base


class PersonnelHeartMessage(Base):
    """心动消息明细表（逻辑关联 personnel_user，不使用物理外键）"""

    __tablename__ = "personnel_heart_message"
    __table_args__ = (
        Index(
            "idx_personnel_heart_message_conversation_created",
            "conversation_key",
            "created_at",
        ),
        Index(
            "idx_personnel_heart_message_sender_created",
            "sender_record_id",
            "created_at",
        ),
        Index(
            "idx_personnel_heart_message_receiver_created",
            "receiver_record_id",
            "created_at",
        ),
        Index("idx_personnel_heart_message_status", "status"),
        Index("idx_personnel_heart_message_scene", "message_scene"),
        Index("idx_personnel_heart_message_deleted", "is_deleted"),
    )

    id = Column(
        "_id",
        String(64),
        primary_key=True,
        comment="消息ID，如 heart-20260404-001",
    )
    conversation_key = Column(
        String(191),
        nullable=False,
        default="",
        comment="会话键，双方 personnel_user._id 按字典序拼接",
    )
    sender_record_id = Column(
        String(64),
        nullable=False,
        default="",
        comment="发送方 personnel_user._id",
    )
    receiver_record_id = Column(
        String(64),
        nullable=False,
        default="",
        comment="接收方 personnel_user._id",
    )
    content = Column(String(300), nullable=False, default="", comment="消息内容")
    status = Column(
        String(16),
        nullable=False,
        default="draft",
        comment="状态:draft/queued/delivered/revoked",
    )
    is_anonymous = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否匿名发送",
    )
    quota_cost = Column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="消耗心动值",
    )
    message_scene = Column(
        String(16),
        nullable=False,
        default="chat",
        comment="消息场景:chat/inbox/manual",
    )
    user_remark = Column(
        String(255),
        nullable=False,
        default="",
        comment="用户备注/后台备注",
    )
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    delivered_at = Column(DateTime, nullable=True, comment="投递时间")
    revoked_at = Column(DateTime, nullable=True, comment="撤销时间")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="软删除")
