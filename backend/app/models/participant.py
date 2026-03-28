# 活动参与者数据模型

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    SmallInteger,
    DateTime,
)
from datetime import datetime

from ..core.database import Base


class Participant(Base):
    """活动参与者表"""

    __tablename__ = "participant"

    id = Column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键"
    )
    participant_name = Column(
        String(32), nullable=False, default="", comment="参与者姓名"
    )
    permanent_token = Column(
        String(128), unique=True, index=True, nullable=False, default="", comment="永久Token"
    )
    gender = Column(
        SmallInteger, nullable=False, default=0, comment="性别: 0=未知, 1=男, 2=女"
    )
    age = Column(
        SmallInteger, nullable=True, default=None, comment="年龄"
    )
    mbti = Column(
        String(4), nullable=True, default=None, comment="MBTI人格类型"
    )
    hometown = Column(
        String(64), nullable=True, default=None, comment="籍贯"
    )
    current_residence = Column(
        String(64), nullable=True, default=None, comment="现住地"
    )
    create_time = Column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_time = Column(
        DateTime, nullable=True, onupdate=datetime.now, comment="更新时间"
    )

    def __repr__(self):
        return f"<Participant(id={self.id}, participant_name='{self.participant_name}', mbti='{self.mbti}')>"
