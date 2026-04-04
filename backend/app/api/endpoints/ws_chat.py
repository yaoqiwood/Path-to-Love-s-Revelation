"""WebSocket 聊天端点 — 全双工实时消息通信"""

import asyncio
import traceback
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.core.security import decode_token
from app.core.ws_manager import ws_manager
from app.services.personnel_user_service import PersonnelUserService

logger = get_logger(__name__)

router = APIRouter()

HEARTBEAT_INTERVAL = 30  # 秒


async def _resolve_personnel_id(token: str) -> str | None:
    """从 JWT token 解析 personnel_id"""
    if not token:
        return None
    token_data = decode_token(token.strip())
    if token_data is None:
        return None
    return token_data.personnel_id or token_data.subject or None


def _make_auth(token: str) -> str:
    """构造 Bearer authorization 字符串"""
    return f"Bearer {token.strip()}"


async def _with_service(handler):
    """为每个 WS 操作创建独立的 DB session + service"""
    async with SessionLocal() as db:
        try:
            service = PersonnelUserService(db)
            result = await handler(service)
            await db.commit()
            return result
        except Exception:
            await db.rollback()
            raise


def _serialize(obj) -> dict:
    """将 Pydantic model 序列化为 dict"""
    if hasattr(obj, "model_dump"):
        return obj.model_dump(by_alias=True)
    if hasattr(obj, "dict"):
        return obj.dict(by_alias=True)
    return obj


# ==================== 消息处理器 ====================


async def _handle_init(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """连接后拉取初始数据：联系人 + 收信箱 + 状态"""
    auth = _make_auth(token)
    keyword = (data.get("keyword") or "").strip() or None

    async def _do(service: PersonnelUserService):
        contacts_resp = await service.list_opposite_gender_users(
            authorization=auth, keyword=keyword
        )
        inbox_resp = await service.list_inbox(
            personnel_id=personnel_id, keyword=keyword, authorization=auth
        )
        state_resp = await service.get_heart_state(
            personnel_id=personnel_id, authorization=auth
        )
        return contacts_resp, inbox_resp, state_resp

    contacts_resp, inbox_resp, state_resp = await _with_service(_do)
    await ws.send_json({
        "type": "init_data",
        "requestId": data.get("requestId"),
        "contacts": _serialize(contacts_resp),
        "inbox": _serialize(inbox_resp),
        "state": _serialize(state_resp),
    })


async def _handle_load_contacts(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """刷新联系人列表"""
    auth = _make_auth(token)
    keyword = (data.get("keyword") or "").strip() or None

    async def _do(service: PersonnelUserService):
        return await service.list_opposite_gender_users(
            authorization=auth, keyword=keyword
        )

    resp = await _with_service(_do)
    await ws.send_json({
        "type": "contacts_data",
        "requestId": data.get("requestId"),
        **_serialize(resp),
    })


async def _handle_load_inbox(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """刷新收信箱"""
    auth = _make_auth(token)
    keyword = (data.get("keyword") or "").strip() or None

    async def _do(service: PersonnelUserService):
        return await service.list_inbox(
            personnel_id=personnel_id, keyword=keyword, authorization=auth
        )

    resp = await _with_service(_do)
    await ws.send_json({
        "type": "inbox_data",
        "requestId": data.get("requestId"),
        **_serialize(resp),
    })


async def _handle_load_history(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """加载聊天记录"""
    auth = _make_auth(token)
    contact_id = data.get("contactId", "")
    since = data.get("since")

    if not contact_id:
        await ws.send_json({
            "type": "message_error",
            "requestId": data.get("requestId"),
            "error": "contactId 不能为空",
        })
        return

    async def _do(service: PersonnelUserService):
        return await service.list_heart_messages(
            personnel_id=personnel_id,
            contact_id=contact_id,
            since=since,
            authorization=auth,
        )

    resp = await _with_service(_do)
    await ws.send_json({
        "type": "history_data",
        "requestId": data.get("requestId"),
        **_serialize(resp),
    })


async def _handle_send_message(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """发送消息"""
    auth = _make_auth(token)
    contact_id = data.get("contactId", "")
    content = data.get("content", "")
    scene = data.get("scene", "contacts")

    if not contact_id or not content:
        await ws.send_json({
            "type": "message_error",
            "requestId": data.get("requestId"),
            "error": "contactId 和 content 不能为空",
        })
        return

    async def _do(service: PersonnelUserService):
        return await service.send_heart_message(
            personnel_id=personnel_id,
            contact_id=contact_id,
            content=content,
            scene=scene,
            authorization=auth,
        )

    resp = await _with_service(_do)
    await ws.send_json({
        "type": "message_sent",
        "requestId": data.get("requestId"),
        **_serialize(resp),
    })


async def _handle_load_state(
    ws: WebSocket, personnel_id: str, token: str, data: dict
) -> None:
    """获取消息状态版本号"""
    auth = _make_auth(token)

    async def _do(service: PersonnelUserService):
        return await service.get_heart_state(
            personnel_id=personnel_id, authorization=auth
        )

    resp = await _with_service(_do)
    await ws.send_json({
        "type": "state_data",
        "requestId": data.get("requestId"),
        **_serialize(resp),
    })


# ==================== 消息路由表 ====================

_HANDLERS = {
    "init": _handle_init,
    "load_contacts": _handle_load_contacts,
    "load_inbox": _handle_load_inbox,
    "load_history": _handle_load_history,
    "send_message": _handle_send_message,
    "load_state": _handle_load_state,
}


# ==================== WebSocket 端点 ====================


@router.websocket("/chat")
async def ws_chat(
    ws: WebSocket,
    token: str = Query("", description="JWT Bearer token"),
):
    """
    WebSocket 聊天端点 — 全双工通信

    连接: ws://host/ws/chat?token=xxx

    客户端 → 服务端:
        {"type": "init"}                                      初始化
        {"type": "load_contacts", "keyword?": ""}             联系人列表
        {"type": "load_inbox", "keyword?": ""}                收信箱
        {"type": "load_history", "contactId": "", "since?": ""} 聊天记录
        {"type": "send_message", "contactId": "", "content": "", "scene": ""} 发消息
        {"type": "load_state"}                                状态版本号
        {"type": "ping"}                                      心跳

    服务端 → 客户端:
        {"type": "connected", "personnel_id": ""}
        {"type": "init_data", "contacts": {}, "inbox": {}, "state": {}}
        {"type": "contacts_data", ...}
        {"type": "inbox_data", ...}
        {"type": "history_data", ...}
        {"type": "message_sent", "id": ""}
        {"type": "message_error", "error": ""}
        {"type": "new_message", ...}        (推送)
        {"type": "contacts_update"}         (推送)
        {"type": "inbox_update"}            (推送)
        {"type": "pong"}
    """
    personnel_id = await _resolve_personnel_id(token)
    if not personnel_id:
        await ws.close(code=4001, reason="Invalid or missing token")
        return

    await ws_manager.connect(personnel_id, ws)
    try:
        await ws.send_json(
            {"type": "connected", "personnel_id": personnel_id}
        )
        while True:
            try:
                data = await asyncio.wait_for(
                    ws.receive_json(), timeout=HEARTBEAT_INTERVAL + 10
                )
            except asyncio.TimeoutError:
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    break
                continue

            msg_type = (data or {}).get("type", "")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
            elif msg_type == "pong":
                pass
            elif msg_type in _HANDLERS:
                try:
                    await _HANDLERS[msg_type](ws, personnel_id, token, data)
                except Exception as exc:
                    logger.warning(
                        "WS handler %s error for %s: %s",
                        msg_type,
                        personnel_id,
                        exc,
                    )
                    logger.debug(traceback.format_exc())
                    await ws.send_json({
                        "type": "message_error",
                        "requestId": (data or {}).get("requestId"),
                        "error": str(exc),
                    })
            else:
                logger.debug(
                    "WS unknown type=%s from %s", msg_type, personnel_id
                )
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WS error for %s: %s", personnel_id, exc)
    finally:
        ws_manager.disconnect(personnel_id, ws)
