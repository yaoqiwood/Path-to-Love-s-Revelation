"""
活动参与者管理服务
- 参与者 CRUD
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.participant import Participant
from app.repository.participant_repo import ParticipantRepository
from app.schemas.participant_schema import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantPage,
)

logger = get_logger(__name__)


class ParticipantService:
    """参与者服务，供 FastAPI 端点使用"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ParticipantRepository(db)

    async def list_participants(
        self,
        page: int = 1,
        page_size: int = 20,
        participant_name: Optional[str] = None,
        gender: Optional[int] = None,
        mbti: Optional[str] = None,
    ) -> ParticipantPage:
        """分页获取参与者列表"""
        items, total = await self.repo.list(
            participant_name=participant_name,
            gender=gender,
            mbti=mbti,
            page=page,
            page_size=page_size,
        )
        return ParticipantPage(total=total, items=items)

    async def get_participant(self, participant_id: int) -> Participant:
        """获取参与者详情，不存在则抛 404"""
        participant = await self.repo.get_by_id(participant_id)
        if not participant:
            raise HTTPException(status_code=404, detail="参与者不存在")
        return participant

    async def get_participant_by_token(self, token: str) -> Participant:
        """根据永久Token获取参与者"""
        participant = await self.repo.get_by_token(token)
        if not participant:
            raise HTTPException(status_code=404, detail="参与者不存在")
        return participant

    async def login_by_token(self, permanent_token: str, client_ip: str = ""):
        """通过永久Token直接登录，返回JWT令牌"""
        from app.core.security import create_access_token, Token
        from app.models.user import SystemUser
        from sqlalchemy import select
        from datetime import datetime

        # 1. 验证永久Token对应的参与者是否存在
        participant = await self.repo.get_by_token(permanent_token)
        if not participant:
            raise HTTPException(status_code=401, detail="无效的永久Token")

        # 2. 查找关联的系统用户（用户名 = token去掉末尾数字部分）
        username = permanent_token[:-4]
        result = await self.db.execute(
            select(SystemUser).where(SystemUser.username == username)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="关联用户不存在")

        if not user.enable_status:
            raise HTTPException(status_code=401, detail="用户已被禁用")

        # 3. 更新登录信息
        user.last_login_time = datetime.now()
        user.last_login_ip = client_ip
        await self.db.flush()

        # 4. 生成JWT
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        logger.info(f"参与者 [{participant.participant_name}] 通过永久Token登录")
        return Token(access_token=access_token, token_type="bearer")

    async def create_participant(self, data: ParticipantCreate) -> Participant:
        """新增参与者，同时自动创建关联的系统用户（角色: player）"""
        from app.utils.token_generator import generate_participant_token
        from app.core.security import get_password_hash
        from app.models.user import SystemUser, SystemRole
        from sqlalchemy import select

        token = data.permanent_token
        if token:
            # 手动指定 token，检查唯一性
            existing = await self.repo.get_by_token(token)
            if existing:
                raise HTTPException(status_code=400, detail="永久Token已存在")
        else:
            # 自动生成 token，重试以避免碰撞
            for _ in range(100):
                token = generate_participant_token()
                existing = await self.repo.get_by_token(token)
                if not existing:
                    break
            else:
                raise HTTPException(status_code=500, detail="Token生成失败，请重试")

        # 检查用户名(token)是否已被占用
        existing_user = await self.db.execute(
            select(SystemUser).where(SystemUser.username == token)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已被占用，请重试")

        # 1. 创建参与者
        participant = Participant(
            participant_name=data.participant_name,
            permanent_token=token,
            gender=data.gender,
            age=data.age,
            mbti=data.mbti,
            hometown=data.hometown,
            current_residence=data.current_residence,
        )
        self.db.add(participant)

        # 2. 自动创建系统用户（用户名=token，密码=token，昵称=姓名）
        player_role_result = await self.db.execute(
            select(SystemRole).where(SystemRole.id == 2)
        )
        player_role = player_role_result.scalar_one_or_none()

        new_user = SystemUser(
            username=token[:-4],
            nickname=data.participant_name,
            password=get_password_hash(token),
            salt="bcrypt",
            enable_status=1,
        )
        if player_role:
            new_user.roles = [player_role]

        self.db.add(new_user)

        await self.db.flush()
        await self.db.refresh(participant)

        logger.info(f"创建参与者 [{data.participant_name}] 及用户 [{token}]")
        return participant

    async def update_participant(
        self, participant_id: int, data: ParticipantUpdate
    ) -> Participant:
        """更新参与者"""
        participant = await self.repo.get_by_id(participant_id)
        if not participant:
            raise HTTPException(status_code=404, detail="参与者不存在")

        # 若更新 token，检查唯一性
        if data.permanent_token is not None:
            existing = await self.repo.get_by_token(data.permanent_token)
            if existing and existing.id != participant_id:
                raise HTTPException(status_code=400, detail="永久Token已存在")

        if data.participant_name is not None:
            participant.participant_name = data.participant_name
        if data.permanent_token is not None:
            participant.permanent_token = data.permanent_token
        if data.gender is not None:
            participant.gender = data.gender
        if data.age is not None:
            participant.age = data.age
        if data.mbti is not None:
            participant.mbti = data.mbti
        if data.hometown is not None:
            participant.hometown = data.hometown
        if data.current_residence is not None:
            participant.current_residence = data.current_residence

        await self.db.flush()
        await self.db.refresh(participant)
        return participant

    async def delete_participant(self, participant_id: int) -> dict:
        """删除参与者（物理删除）"""
        participant = await self.repo.get_by_id(participant_id)
        if not participant:
            raise HTTPException(status_code=404, detail="参与者不存在")

        await self.repo.delete(participant)
        return {"message": "删除成功"}


# ==================== 依赖注入 ====================


async def get_participant_service(
    db: AsyncSession = Depends(get_db),
) -> ParticipantService:
    return ParticipantService(db)


ParticipantServiceDep = Annotated[ParticipantService, Depends(get_participant_service)]
