# 活动参与者 Pydantic Schema

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator


# ==================== Participant Schemas ====================


class ParticipantBase(BaseModel):
    participant_name: str
    permanent_token: str
    gender: int = 0
    age: Optional[int] = None
    mbti: Optional[str] = None
    hometown: Optional[str] = None
    current_residence: Optional[str] = None

    @field_validator("mbti", mode="before")
    @classmethod
    def normalize_mbti(cls, v):
        """MBTI 统一大写，最多4字符"""
        if v:
            return str(v).upper()[:4]
        return None


class ParticipantCreate(ParticipantBase):
    permanent_token: Optional[str] = None  # 可选，不传则后端自动生成


class ParticipantUpdate(BaseModel):
    participant_name: Optional[str] = None
    permanent_token: Optional[str] = None
    gender: Optional[int] = None
    age: Optional[int] = None
    mbti: Optional[str] = None
    hometown: Optional[str] = None
    current_residence: Optional[str] = None

    @field_validator("mbti", mode="before")
    @classmethod
    def normalize_mbti(cls, v):
        if v is not None:
            return str(v).upper()[:4]
        return v


class ParticipantResponse(ParticipantBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParticipantPage(BaseModel):
    total: int
    items: List[ParticipantResponse]
