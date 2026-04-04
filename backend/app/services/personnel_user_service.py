from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BizError, BizException
from app.core.database import get_db
from app.core.security import create_access_token, decode_token
from app.models.personnel_user import PersonnelUser
from app.models.user import SystemUser
from app.repository import (
    PersonnelHeartMessageRepository,
    PersonnelUserRepository,
    UserRepository,
)
from app.schemas.personnel_schema import (
    PersonnelCreate,
    PersonnelDeleteResponse,
    PersonnelHeartHomeContact,
    PersonnelHeartHomeResponse,
    PersonnelHeartHomeSelf,
    PersonnelHeartMessageHistoryContact,
    PersonnelHeartMessageHistoryItem,
    PersonnelHeartMessageHistoryResponse,
    PersonnelHeartMessageHistorySelf,
    PersonnelLoginConfirm,
    PersonnelLoginRecord,
    PersonnelLoginProfile,
    PersonnelLoginProfileResponse,
    PersonnelLoginTokenResponse,
    PersonnelListResponse,
    PersonnelListStats,
    PersonnelMbtiUpdateResult,
    PersonnelResponse,
    PersonnelUpdate,
    PersonnelHeartInboxItem,
    PersonnelHeartInboxResponse,
    PersonnelHeartState,
    PersonnelHeartStateResponse,
    PersonnelHeartMessageCreateResponse,
)
from app.models.personnel_heart_message import PersonnelHeartMessage as PersonnelHeartMessageModel
from app.core.logging import get_logger

logger = get_logger(__name__)


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
        self.heart_message_repo = PersonnelHeartMessageRepository(db)
        self.user_repo = UserRepository(db)

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

    async def update_mbti_by_token(self, token: str, mbti: str) -> PersonnelMbtiUpdateResult:
        normalized_token = (token or "").strip()
        if not normalized_token:
            raise BizException(
                code=BizError.BAD_REQUEST,
                message="token不能为空",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        normalized_mbti = (mbti or "").strip().upper()
        if not normalized_mbti:
            raise BizException(
                code=BizError.BAD_REQUEST,
                message="mbti不能为空",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if len(normalized_mbti) > 8:
            raise BizException(
                code=BizError.BAD_REQUEST,
                message="mbti长度不能超过8位",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token_data = decode_token(normalized_token)
        if token_data is None or not token_data.subject:
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="登录已过期，请重新登录",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        personnel = await self._get_personnel_from_token(token_data)
        if personnel:
            updated = await self.repo.update(
                personnel,
                {"mbti": normalized_mbti, "updated_at": now_iso_text()},
            )
            return PersonnelMbtiUpdateResult(
                id=updated.id,
                name=updated.name,
                result=True,
            )

        if token_data.personnel_id:
            raise BizException(
                code=BizError.PERSONNEL_USER_NOT_FOUND,
                message="查无此用户",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        system_user = await self._get_system_user_from_token(token_data)
        if system_user:
            raise BizException(
                code=BizError.PERSONNEL_USER_NOT_FOUND,
                message="查无此用户",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        personnel = await self.repo.get_by_user_id(token_data.subject)
        if not personnel:
            raise BizException(
                code=BizError.PERSONNEL_USER_NOT_FOUND,
                message="查无此用户",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        updated = await self.repo.update(
            personnel,
            {"mbti": normalized_mbti, "updated_at": now_iso_text()},
        )
        return PersonnelMbtiUpdateResult(
            id=updated.id,
            name=updated.name,
            result=True,
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
            remaining_mbti_test_count=(
                payload["remaining_mbti_test_count"]
                if payload.get("remaining_mbti_test_count") is not None
                else 0
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
            "remaining_mbti_test_count": "remaining_mbti_test_count",
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

    async def delete_personnel(self, personnel_id: str) -> PersonnelDeleteResponse:
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        await self.repo.update(
            personnel,
            {"is_deleted": True, "updated_at": now_iso_text()},
        )
        return PersonnelDeleteResponse(id=personnel_id, deleted=True)

    async def list_heart_messages(
        self,
        personnel_id: str,
        contact_id: str,
        since: Optional[str],
        authorization: str,
    ) -> PersonnelHeartMessageHistoryResponse:
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="聊天对象不存在")

        await self._authorize_personnel_history_access(personnel, authorization)

        conversation_key = self._build_conversation_key(personnel_id, contact_id)
        since_dt = self._parse_since_datetime(since)
        rows = await self.heart_message_repo.list_visible_conversation_messages(
            conversation_key, since_dt
        )
        latest_message = await self.heart_message_repo.get_latest_visible_conversation_message(
            conversation_key
        )

        return PersonnelHeartMessageHistoryResponse(
            self=self._build_history_self(personnel),
            contact=self._build_history_contact(contact),
            list=[self._build_history_item(row) for row in rows],
            can_send=self._can_send_to_contact(personnel_id, latest_message),
            can_send_reason=self._build_can_send_reason(personnel_id, latest_message),
        )

    async def list_inbox(
        self,
        personnel_id: str,
        keyword: Optional[str],
        authorization: str,
    ) -> PersonnelHeartInboxResponse:
        """收信箱列表"""
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        await self._authorize_personnel_history_access(personnel, authorization)

        rows = await self.heart_message_repo.list_inbox_messages(personnel_id)

        # 按 sender 分组，每个 sender 只取最新消息
        seen_senders: dict[str, dict] = {}
        for row in rows:
            sender_id = row["sender_record_id"]
            if sender_id == personnel_id:
                continue  # 跳过自己发的
            if sender_id not in seen_senders:
                seen_senders[sender_id] = row

        inbox_items: list[PersonnelHeartInboxItem] = []
        for sender_id, row in seen_senders.items():
            sender = await self.repo.get_by_id(sender_id)
            sender_mbti = sender.mbti if sender else ""

            # 过滤关键字
            if keyword:
                kw = keyword.strip().lower()
                if kw and kw not in (sender_mbti or "").lower():
                    if kw not in (row.get("content") or "").lower():
                        continue

            # 轮次制：最新消息是对方发的 → 可回复
            conversation_key = self._build_conversation_key(personnel_id, sender_id)
            latest = await self.heart_message_repo.get_latest_visible_conversation_message(
                conversation_key
            )
            can_reply = True
            can_reply_reason = ""
            if latest and latest.get("sender_record_id") == personnel_id:
                can_reply = False
                can_reply_reason = "请等待对方再次来信"

            inbox_items.append(
                PersonnelHeartInboxItem(
                    message_id=str(row["id"]),
                    contact_id=sender_id,
                    sender_mbti=sender_mbti,
                    content=row.get("content") or "",
                    created_at=self._to_iso_text(row.get("created_at")),
                    can_reply=can_reply,
                    can_reply_reason=can_reply_reason,
                )
            )

        return PersonnelHeartInboxResponse(
            self=self._build_heart_home_self(personnel),
            list=inbox_items,
        )

    async def get_heart_state(
        self,
        personnel_id: str,
        authorization: str,
    ) -> PersonnelHeartStateResponse:
        """消息状态版本号"""
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        await self._authorize_personnel_history_access(personnel, authorization)

        contacts_version = await self.heart_message_repo.count_messages_for_user(personnel_id)
        inbox_version = await self.heart_message_repo.count_inbox_messages(personnel_id)

        now_text = now_iso_text()
        return PersonnelHeartStateResponse(
            self=self._build_heart_home_self(personnel),
            state=PersonnelHeartState(
                contactsVersion=contacts_version,
                inboxVersion=inbox_version,
                latestMessageAtText=now_text,
                updatedAtText=now_text,
            ),
        )

    async def send_heart_message(
        self,
        personnel_id: str,
        contact_id: str,
        content: str,
        scene: str,
        authorization: str,
    ) -> PersonnelHeartMessageCreateResponse:
        """发送心动消息"""
        personnel = await self.repo.get_by_id(personnel_id)
        if not personnel:
            raise HTTPException(status_code=404, detail="人员档案不存在")

        contact = await self.repo.get_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="聊天对象不存在")

        await self._authorize_personnel_history_access(personnel, authorization)

        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="消息内容不能为空")

        conversation_key = self._build_conversation_key(personnel_id, contact_id)
        now = datetime.now(timezone.utc)
        msg_id = f"heart-{now.strftime('%Y%m%d%H%M%S')}-{personnel_id[-3:]}"

        message = PersonnelHeartMessageModel(
            id=msg_id,
            conversation_key=conversation_key,
            sender_record_id=personnel_id,
            receiver_record_id=contact_id,
            content=content.strip()[:300],
            status="delivered",
            is_anonymous=(scene != "chat"),
            quota_cost=1,
            message_scene=scene or "contacts",
            user_remark="",
            created_at=now,
            updated_at=now,
            delivered_at=now,
            is_deleted=False,
        )

        await self.heart_message_repo.create_message(message)
        await self.db.commit()

        # WebSocket 推送给接收方
        try:
            from app.core.ws_manager import ws_manager
            await ws_manager.send_to_user(contact_id, {
                "type": "new_message",
                "conversation_key": conversation_key,
                "message": {
                    "_id": msg_id,
                    "sender_record_id": personnel_id,
                    "receiver_record_id": contact_id,
                    "content": content.strip()[:300],
                    "created_at": self._to_iso_text(now),
                    "created_at_text": self._to_iso_text(now),
                },
            })
            await ws_manager.send_to_user(contact_id, {"type": "inbox_update"})
            await ws_manager.send_to_user(personnel_id, {"type": "contacts_update"})
            # 递增内存版本号
            ws_manager.bump_version(contact_id, "inboxVersion")
            ws_manager.bump_version(contact_id, "contactsVersion")
            ws_manager.bump_version(personnel_id, "contactsVersion")
        except Exception as exc:
            logger.warning("WS push failed: %s", exc)

        return PersonnelHeartMessageCreateResponse(id=msg_id)

    async def get_heart_home(
        self,
        authorization: str,
        keyword: Optional[str] = None,
        personnel_id: Optional[str] = None,
    ) -> PersonnelHeartHomeResponse:
        current_personnel = await self._get_current_personnel_from_authorization(
            authorization
        )
        if personnel_id and personnel_id != current_personnel.id:
            raise BizException(
                code=BizError.PERMISSION_DENIED,
                message="无权查看其他人员的联系人列表",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        opposite_gender = self._resolve_opposite_gender(current_personnel.gender)
        if not opposite_gender:
            return PersonnelHeartHomeResponse(
                self=self._build_heart_home_self(current_personnel),
                contacts=[],
            )

        contacts = await self.repo.list_heart_home_contacts(
            exclude_id=current_personnel.id,
            opposite_gender=opposite_gender,
            keyword=(keyword or "").strip() or None,
        )
        visible_messages = await self.heart_message_repo.list_visible_personnel_messages(
            current_personnel.id
        )
        latest_by_contact, latest_sent_by_contact = self._build_latest_message_map(
            current_personnel.id, visible_messages
        )

        # 查询双方从联系人列表发消息的记录，用于判断 chat_status
        i_sent_to = set(await self.heart_message_repo.list_contacts_receivers(current_personnel.id))
        sent_to_me = set(await self.heart_message_repo.list_contacts_senders(current_personnel.id))

        contact_items = [
            self._build_heart_home_contact(
                current_personnel.id,
                contact,
                latest_by_contact.get(contact.id),
                latest_sent_by_contact.get(contact.id),
                chat_status=(
                    "unlocked" if contact.id in i_sent_to and contact.id in sent_to_me
                    else "pending" if contact.id in i_sent_to
                    else "none"
                ),
            )
            for contact in contacts
        ]
        contact_items.sort(
            key=lambda item: item.latest_message_at or "",
            reverse=True,
        )

        return PersonnelHeartHomeResponse(
            self=self._build_heart_home_self(current_personnel),
            contacts=contact_items,
        )

    async def list_opposite_gender_users(
        self,
        authorization: str,
        keyword: Optional[str] = None,
    ) -> PersonnelHeartHomeResponse:
        current_personnel = await self._get_current_personnel_from_authorization(
            authorization
        )
        opposite_gender = self._resolve_opposite_gender(current_personnel.gender)
        if not opposite_gender:
            return PersonnelHeartHomeResponse(
                self=self._build_heart_home_self(current_personnel),
                contacts=[],
            )

        users = await self.repo.list_opposite_gender_users(
            exclude_id=current_personnel.id,
            opposite_gender=opposite_gender,
            keyword=(keyword or "").strip() or None,
        )

        my_id = current_personnel.id
        i_sent_to = set(
            await self.heart_message_repo.list_contacts_receivers(my_id)
        )
        they_sent_to_me = set(
            await self.heart_message_repo.list_contacts_senders(my_id)
        )

        visible_messages = await self.heart_message_repo.list_visible_personnel_messages(
            my_id
        )
        latest_by_contact, latest_sent_by_contact = self._build_latest_message_map(my_id, visible_messages)

        contact_items = []
        for u in users:
            if u.id in i_sent_to and u.id in they_sent_to_me:
                chat_status = "unlocked"
            elif u.id in i_sent_to:
                chat_status = "initiated"
            else:
                chat_status = "none"

            latest_msg = latest_by_contact.get(u.id)
            is_unlocked = chat_status == "unlocked"

            # 未解锁：只显示自己发出的消息；已解锁：显示双方消息
            display_msg = latest_msg if is_unlocked else latest_sent_by_contact.get(u.id)
            latest_message_at = self._to_iso_text(
                display_msg.get("created_at") if display_msg else None
            )

            if is_unlocked:
                can_send = True
            else:
                can_send = self._can_send_to_contact(my_id, latest_msg)

            contact_items.append(
                PersonnelHeartHomeContact(
                    id=u.id,
                    name=u.name,
                    nickname=u.nickname,
                    gender=u.gender,
                    mbti=u.mbti,
                    personal_photo=u.personal_photo,
                    latest_message=(display_msg or {}).get("content", ""),
                    latest_message_at=latest_message_at,
                    can_send=can_send,
                    chat_status=chat_status,
                )
            )
        return PersonnelHeartHomeResponse(
            self=self._build_heart_home_self(current_personnel),
            contacts=contact_items,
        )

    async def _get_personnel_from_token(self, token_data) -> Optional[PersonnelUser]:
        if token_data.personnel_id:
            personnel = await self.repo.get_by_id(token_data.personnel_id)
            if personnel and self._personnel_matches_subject(
                personnel, token_data.subject
            ):
                return personnel
            return None

        if token_data.subject and not token_data.user_id:
            return await self.repo.get_by_id(token_data.subject)

        return None

    async def _get_system_user_from_token(self, token_data) -> Optional[SystemUser]:
        if token_data.user_id is None:
            return None

        user = await self.user_repo.get_by_id_active(token_data.user_id)
        if user is None or not user.is_active:
            return None
        return user

    @staticmethod
    def _personnel_matches_subject(personnel: PersonnelUser, subject: str) -> bool:
        return subject in {personnel.id, (personnel.user_id or "").strip()}

    async def _authorize_personnel_history_access(
        self, personnel: PersonnelUser, authorization: str
    ) -> None:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="Authorization 请求头格式错误",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = decode_token(token.strip())
        if token_data is None or not token_data.subject:
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="登录已过期，请重新登录",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if personnel.review_status != "approved":
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="当前人员档案未通过审核",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_data.personnel_id:
            if token_data.personnel_id == personnel.id or self._personnel_matches_subject(
                personnel, token_data.subject
            ):
                return
            raise BizException(
                code=BizError.PERMISSION_DENIED,
                message="无权查看该聊天记录",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        system_user = await self._get_system_user_from_token(token_data)
        if system_user:
            return

        if token_data.subject == (personnel.user_id or "").strip():
            return

        raise BizException(
            code=BizError.PERMISSION_DENIED,
            message="无权查看该聊天记录",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    async def _get_current_personnel_from_authorization(
        self, authorization: str
    ) -> PersonnelUser:
        scheme, _, token = (authorization or "").partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="Authorization 请求头格式错误",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = decode_token(token.strip())
        if token_data is None or not token_data.subject:
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="登录已过期，请重新登录",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        personnel = await self._get_personnel_from_token(token_data)
        if personnel is None and token_data.subject:
            personnel = await self.repo.get_by_user_id(token_data.subject)

        if personnel is None:
            raise BizException(
                code=BizError.PERSONNEL_USER_NOT_FOUND,
                message="查无此用户",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if personnel.is_deleted or personnel.review_status != "approved":
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="当前人员档案未通过审核",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return personnel

    @staticmethod
    def _build_conversation_key(left_id: str, right_id: str) -> str:
        normalized = sorted([(left_id or "").strip(), (right_id or "").strip()])
        return "::".join(normalized)

    @staticmethod
    def _parse_since_datetime(value: Optional[str]) -> Optional[datetime]:
        text = (value or "").strip()
        if not text:
            return None

        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="since 参数格式错误") from exc

    @staticmethod
    def _to_iso_text(value: Optional[datetime]) -> str:
        if value is None:
            return ""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )

    def _build_history_self(
        self, personnel: PersonnelUser
    ) -> PersonnelHeartMessageHistorySelf:
        return PersonnelHeartMessageHistorySelf(
            id=personnel.id,
            person_id=personnel.person_id,
            name=personnel.name,
            nickname=personnel.nickname,
            mbti=personnel.mbti,
            personal_photo=personnel.personal_photo,
            remaining_heart_value=personnel.remaining_heart_value,
            heart_message_quota=personnel.heart_message_quota,
            remaining_mbti_test_count=personnel.remaining_mbti_test_count,
        )

    def _build_history_contact(
        self, personnel: PersonnelUser
    ) -> PersonnelHeartMessageHistoryContact:
        return PersonnelHeartMessageHistoryContact(
            id=personnel.id,
            name=personnel.name,
            nickname=personnel.nickname,
            personal_photo=personnel.personal_photo,
            mbti=personnel.mbti,
        )

    def _build_history_item(self, row: dict) -> PersonnelHeartMessageHistoryItem:
        created_at_text = self._to_iso_text(row.get("created_at"))
        return PersonnelHeartMessageHistoryItem(
            id=row["id"],
            sender_record_id=row["sender_record_id"],
            receiver_record_id=row["receiver_record_id"],
            content=row["content"] or "",
            created_at=created_at_text,
            created_at_text=created_at_text,
        )

    @staticmethod
    def _can_send_to_contact(personnel_id: str, latest_message: Optional[dict]) -> bool:
        if not latest_message:
            return True
        return latest_message.get("sender_record_id") != personnel_id

    def _build_can_send_reason(
        self, personnel_id: str, latest_message: Optional[dict]
    ) -> str:
        if self._can_send_to_contact(personnel_id, latest_message):
            return ""
        return "请等待对方回复后再发送下一条"

    @staticmethod
    def _resolve_opposite_gender(gender: str) -> str:
        normalized = (gender or "").strip()
        if normalized == "男":
            return "女"
        if normalized == "女":
            return "男"
        return ""

    def _build_heart_home_self(self, personnel: PersonnelUser) -> PersonnelHeartHomeSelf:
        return PersonnelHeartHomeSelf(
            id=personnel.id,
            person_id=personnel.person_id,
            name=personnel.name,
            nickname=personnel.nickname,
            mbti=personnel.mbti,
            personal_photo=personnel.personal_photo,
            remaining_heart_value=personnel.remaining_heart_value,
            heart_message_quota=personnel.heart_message_quota,
        )

    def _build_latest_message_map(
        self, personnel_id: str, rows: list[dict]
    ) -> tuple[dict[str, dict], dict[str, dict]]:
        """返回 (latest_by_contact, latest_sent_by_contact)"""
        latest_by_contact: dict[str, dict] = {}
        latest_sent_by_contact: dict[str, dict] = {}
        for row in sorted(
            rows,
            key=lambda item: item.get("created_at") or datetime.min,
        ):
            sender_id = row.get("sender_record_id") or ""
            receiver_id = row.get("receiver_record_id") or ""
            contact_id = receiver_id if sender_id == personnel_id else sender_id
            if not contact_id:
                continue
            latest_by_contact[contact_id] = row
            if sender_id == personnel_id:
                latest_sent_by_contact[contact_id] = row
        return latest_by_contact, latest_sent_by_contact

    def _build_heart_home_contact(
        self,
        personnel_id: str,
        contact: PersonnelUser,
        latest_message: Optional[dict],
        latest_sent_message: Optional[dict],
        chat_status: str = "none",
    ) -> PersonnelHeartHomeContact:
        is_unlocked = chat_status == "unlocked"

        # 未解锁：只显示自己发出的最后一条消息
        # 已解锁：显示双方的最后一条消息
        display_message = latest_message if is_unlocked else latest_sent_message

        latest_message_at = self._to_iso_text(
            display_message.get("created_at") if display_message else None
        )
        return PersonnelHeartHomeContact(
            id=contact.id,
            name=contact.name,
            nickname=contact.nickname,
            gender=contact.gender,
            mbti=contact.mbti,
            personal_photo=contact.personal_photo,
            latest_message=(display_message or {}).get("content", ""),
            latest_message_at=latest_message_at,
            can_send=is_unlocked or self._can_send_to_contact(personnel_id, latest_message),
            chat_status=chat_status,
        )

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
