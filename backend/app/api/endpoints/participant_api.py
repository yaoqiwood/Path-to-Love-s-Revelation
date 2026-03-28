# 活动参与者API端点

from typing import Optional
from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from ...core.security import Token
from ...schemas.participant_schema import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    ParticipantPage,
)
from ..deps import CurrentUser
from ...services.participant_service import ParticipantServiceDep

router = APIRouter()


# ==================== 公开接口（无需登录） ====================


class TokenLoginRequest(BaseModel):
    permanent_token: str


@router.post("/login", response_model=Token)
async def login_by_token(
    data: TokenLoginRequest,
    request: Request,
    service: ParticipantServiceDep,
):
    """通过永久Token直接登录，返回JWT访问令牌（无需认证）"""
    client_ip = request.client.host if request.client else ""
    return await service.login_by_token(data.permanent_token, client_ip=client_ip)


# ==================== 需要登录的接口 ====================


@router.get("/", response_model=ParticipantPage)
async def list_participants(
    current_user: CurrentUser,
    service: ParticipantServiceDep,
    page: int = 1,
    page_size: int = 20,
    participant_name: Optional[str] = None,
    gender: Optional[int] = None,
    mbti: Optional[str] = None,
):
    """分页获取参与者列表"""
    return await service.list_participants(
        page=page,
        page_size=page_size,
        participant_name=participant_name,
        gender=gender,
        mbti=mbti,
    )


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: int,
    current_user: CurrentUser,
    service: ParticipantServiceDep,
):
    """获取参与者详情"""
    return await service.get_participant(participant_id)


@router.get("/token/{token}", response_model=ParticipantResponse)
async def get_participant_by_token(
    token: str,
    current_user: CurrentUser,
    service: ParticipantServiceDep,
):
    """根据永久Token获取参与者"""
    return await service.get_participant_by_token(token)


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    data: ParticipantCreate,
    request: Request,
    current_user: CurrentUser,
    service: ParticipantServiceDep,
):
    """新增参与者"""
    return await service.create_participant(data)


@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int,
    data: ParticipantUpdate,
    request: Request,
    current_user: CurrentUser,
    service: ParticipantServiceDep,
):
    """更新参与者"""
    return await service.update_participant(participant_id, data)


@router.delete("/{participant_id}")
async def delete_participant(
    participant_id: int,
    request: Request,
    current_user: CurrentUser,
    service: ParticipantServiceDep,
):
    """删除参与者"""
    return await service.delete_participant(participant_id)
