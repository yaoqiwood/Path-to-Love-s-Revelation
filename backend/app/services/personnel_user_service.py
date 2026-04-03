from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.personnel_user import PersonnelUser
from app.repository import PersonnelUserRepository
from app.schemas.personnel_schema import (
    PersonnelCreate,
    PersonnelLoginConfirm,
    PersonnelLoginRecord,
    PersonnelLoginProfile,
    PersonnelLoginProfileResponse,
    PersonnelLoginTokenResponse,
    PersonnelListResponse,
    PersonnelListStats,
    PersonnelResponse,
    PersonnelUpdate,
)


def now_iso_text() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


class PersonnelUserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PersonnelUserRepository(db)

    async def list_personnel(
        self,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        review_status: Optional[str] = "all",
        include_deleted: bool = False,
    ) -> PersonnelListResponse:
        items, total = await self.repo.list(
            keyword=keyword,
            review_status=review_status,
            page=page,
            page_size=page_size,
            include_deleted=include_deleted,
        )
        stats = await self.repo.get_stats()
        return PersonnelListResponse(
            list=[PersonnelResponse.model_validate(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
            stats=PersonnelListStats(**stats),
        )

    async def get_personnel(self, personnel_id: str) -> PersonnelResponse:
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")
        return PersonnelResponse.model_validate(personnel)

    async def get_login_profile_by_passcode(
        self, passcode: str
    ) -> PersonnelLoginProfileResponse:
        personnel = await self._get_active_personnel_by_passcode(passcode)
        if not personnel:
            return PersonnelLoginProfileResponse(matched=False, record=None)

        return PersonnelLoginProfileResponse(
            matched=True,
            record=self._build_login_profile(personnel),
        )

    async def login_by_passcode(
        self, data: PersonnelLoginConfirm, client_ip: str = ""
    ) -> PersonnelLoginTokenResponse:
        personnel = await self._get_active_personnel_by_passcode(data.passcode)
        if not personnel:
            raise HTTPException(status_code=404, detail="未找到对应口令的人员档案")

        self._validate_login_identity(personnel, data)

        if personnel.review_status != "approved":
            raise HTTPException(status_code=403, detail="当前人员档案未通过审核")

        token_subject = (personnel.user_id or "").strip() or personnel.id
        access_token = create_access_token(
            data={
                "sub": str(token_subject),
                "username": personnel.nickname or personnel.name,
                "personnel_id": personnel.id,
            }
        )

        return PersonnelLoginTokenResponse(
            access_token=access_token,
            token_type="bearer",
            profile=self._build_login_record(personnel),
        )

    async def create_personnel(self, data: PersonnelCreate) -> PersonnelResponse:
        payload = data.model_dump(exclude_unset=True)
        person_id = payload.get("person_id") or await self._next_person_id()

        await self._ensure_person_id_available(person_id)

        mobile = (payload.get("mobile") or "").strip()
        if not mobile:
            raise HTTPException(status_code=400, detail="手机号不能为空")
        await self._ensure_mobile_available(mobile)

        passcode = (payload.get("passcode") or f"LOVE{person_id}").strip()
        if not passcode:
            raise HTTPException(status_code=400, detail="邀请码不能为空")
        await self._ensure_passcode_available(passcode)

        created_at = payload.get("submitted_at") or now_iso_text()
        updated_at = payload.get("updated_at") or created_at
        personnel_id = payload.get("id") or f"personnel-{person_id}"

        existing = await self.repo.get_by_id(personnel_id, include_deleted=True)
        if existing:
            raise HTTPException(status_code=400, detail="记录ID已存在")

        personnel = PersonnelUser(
            id=personnel_id,
            person_id=person_id,
            name=(payload.get("name") or "").strip(),
            nickname=(payload.get("nickname") or "").strip(),
            gender=(payload.get("gender") or "").strip(),
            age=payload.get("age"),
            mobile=mobile,
            id_card_no=(payload.get("id_card") or "").strip(),
            mbti=(payload.get("mbti") or "").strip().upper(),
            native_place=(payload.get("native_place") or "").strip(),
            profession=(payload.get("profession") or "").strip(),
            church=(payload.get("church") or "").strip(),
            faith_duration=(payload.get("faith_duration") or "").strip(),
            referrer=(payload.get("referrer") or "").strip(),
            self_introduction=(payload.get("self_introduction") or "").strip(),
            relationship_status=(payload.get("relationship_status") or "").strip(),
            travel_mode=(payload.get("travel_mode") or "").strip(),
            address=(payload.get("address") or "").strip(),
            family_overview=(payload.get("family_overview") or "").strip(),
            review_status=(payload.get("review_status") or "pending").strip(),
            reviewer=(payload.get("reviewer") or "").strip(),
            passcode=passcode,
            user_role=payload["user_role"] if payload.get("user_role") is not None else 0,
            personal_photo=(payload.get("personal_photo") or "").strip(),
            user_id=(payload.get("user_id") or "").strip(),
            private_message_quota=(
                payload["private_message_quota"]
                if payload.get("private_message_quota") is not None
                else 0
            ),
            heart_message_quota=(
                payload["heart_message_quota"]
                if payload.get("heart_message_quota") is not None
                else 3
            ),
            remaining_heart_value=(
                payload["remaining_heart_value"]
                if payload.get("remaining_heart_value") is not None
                else 3
            ),
            submitted_at=created_at,
            updated_at=updated_at,
            is_deleted=bool(payload.get("is_deleted", False)),
        )
        personnel = await self.repo.create(personnel)
        return PersonnelResponse.model_validate(personnel)

    async def update_personnel(
        self, personnel_id: str, data: PersonnelUpdate
    ) -> PersonnelResponse:
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        payload = data.model_dump(exclude_unset=True)
        update_fields = {}

        if "person_id" in payload and payload["person_id"] is not None:
            if payload["person_id"] != personnel.person_id:
                await self._ensure_person_id_available(payload["person_id"], personnel.id)
            update_fields["person_id"] = payload["person_id"]

        if "mobile" in payload and payload["mobile"] is not None:
            mobile = payload["mobile"].strip()
            if not mobile:
                raise HTTPException(status_code=400, detail="手机号不能为空")
            if mobile != personnel.mobile:
                await self._ensure_mobile_available(mobile, personnel.id)
            update_fields["mobile"] = mobile

        if "passcode" in payload and payload["passcode"] is not None:
            passcode = payload["passcode"].strip()
            if not passcode:
                raise HTTPException(status_code=400, detail="邀请码不能为空")
            if passcode != personnel.passcode:
                await self._ensure_passcode_available(passcode, personnel.id)
            update_fields["passcode"] = passcode

        mapping = {
            "name": "name",
            "nickname": "nickname",
            "gender": "gender",
            "age": "age",
            "id_card": "id_card_no",
            "mbti": "mbti",
            "native_place": "native_place",
            "profession": "profession",
            "church": "church",
            "faith_duration": "faith_duration",
            "referrer": "referrer",
            "self_introduction": "self_introduction",
            "relationship_status": "relationship_status",
            "travel_mode": "travel_mode",
            "address": "address",
            "family_overview": "family_overview",
            "review_status": "review_status",
            "reviewer": "reviewer",
            "user_role": "user_role",
            "personal_photo": "personal_photo",
            "user_id": "user_id",
            "private_message_quota": "private_message_quota",
            "heart_message_quota": "heart_message_quota",
            "remaining_heart_value": "remaining_heart_value",
            "submitted_at": "submitted_at",
            "is_deleted": "is_deleted",
        }
        for payload_key, model_key in mapping.items():
            if payload_key not in payload:
                continue
            value = payload[payload_key]
            if isinstance(value, str):
                value = value.strip()
            if payload_key == "mbti" and value:
                value = value.upper()
            update_fields[model_key] = value

        update_fields["updated_at"] = payload.get("updated_at") or now_iso_text()

        personnel = await self.repo.update(personnel, update_fields)
        return PersonnelResponse.model_validate(personnel)

    async def delete_personnel(self, personnel_id: str) -> dict:
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        await self.repo.update(
            personnel,
            {"is_deleted": True, "updated_at": now_iso_text()},
        )
        return {"id": personnel_id}

    async def _next_person_id(self) -> int:
        max_person_id = await self.repo.get_max_person_id()
        return (max_person_id or 100) + 1

    async def _ensure_person_id_available(
        self, person_id: int, current_id: Optional[str] = None
    ) -> None:
        existing = await self.repo.get_by_person_id(person_id)
        if existing and existing.id != current_id:
            raise HTTPException(status_code=400, detail="人员编号已存在")

    async def _ensure_mobile_available(
        self, mobile: str, current_id: Optional[str] = None
    ) -> None:
        existing = await self.repo.get_by_mobile(mobile)
        if existing and existing.id != current_id:
            raise HTTPException(status_code=400, detail="手机号已存在")

    async def _ensure_passcode_available(
        self, passcode: str, current_id: Optional[str] = None
    ) -> None:
        existing = await self.repo.get_by_passcode(passcode)
        if existing and existing.id != current_id:
            raise HTTPException(status_code=400, detail="邀请码已存在")

    async def _get_active_personnel_by_passcode(
        self, passcode: str
    ) -> Optional[PersonnelUser]:
        normalized_passcode = (passcode or "").strip().upper()
        if not normalized_passcode:
            raise HTTPException(status_code=400, detail="口令不能为空")

        personnel = await self.repo.get_by_passcode(normalized_passcode)
        if not personnel or personnel.is_deleted:
            return None
        return personnel

    def _build_login_profile(self, personnel: PersonnelUser) -> PersonnelLoginProfile:
        return PersonnelLoginProfile.model_validate(personnel)

    def _build_login_record(self, personnel: PersonnelUser) -> PersonnelLoginRecord:
        return PersonnelLoginRecord.model_validate(personnel)

    def _validate_login_identity(
        self, personnel: PersonnelUser, data: PersonnelLoginConfirm
    ) -> None:
        if data.personnel_id and data.personnel_id != personnel.id:
            raise HTTPException(status_code=400, detail="人员身份确认失败，请重新匹配")

        if data.person_id is not None and data.person_id != personnel.person_id:
            raise HTTPException(status_code=400, detail="人员编号校验失败，请重新匹配")

        if data.name and data.name.strip() != (personnel.name or "").strip():
            raise HTTPException(status_code=400, detail="姓名校验失败，请重新匹配")

        if data.nickname and data.nickname.strip() != (personnel.nickname or "").strip():
            raise HTTPException(status_code=400, detail="昵称校验失败，请重新匹配")


async def get_personnel_user_service(
    db: AsyncSession = Depends(get_db),
) -> PersonnelUserService:
    return PersonnelUserService(db)


PersonnelUserServiceDep = Annotated[
    PersonnelUserService, Depends(get_personnel_user_service)
]
