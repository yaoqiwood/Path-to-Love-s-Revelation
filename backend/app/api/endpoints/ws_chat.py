"""WebSocket 聊天端点 — 实时消息推送"""

import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.logging import get_logger
from app.core.security import decode_token
from app.core.ws_manager import ws_manager

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


@router.websocket("/chat")
async def ws_chat(
    ws: WebSocket,
    token: str = Query("", description="JWT Bearer token"),
):
    """
    WebSocket 聊天端点

    连接: ws://host/ws/chat?token=xxx
    服务端推送:
        {"type": "new_message", "conversation_key": "...", "message": {...}}
        {"type": "contacts_update"}
        {"type": "inbox_update"}
    客户端发送:
        {"type": "ping"}  -> 服务端回 {"type": "pong", "contactsVersion": N, "inboxVersion": N}
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
                # 客户端超时未发任何消息，发送 ping 探活
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    break
                continue

            msg_type = (data or {}).get("type", "")
            if msg_type == "ping":
                # 从内存读版本号，不查 DB，不阻塞连接池
                versions = ws_manager.get_versions(personnel_id)
                await ws.send_json({"type": "pong", **versions})
            elif msg_type == "pong":
                pass  # 客户端响应了我们的 ping
            else:
                logger.debug(
                    "WS unknown message type=%s from %s",
                    msg_type,
                    personnel_id,
                )
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WS error for %s: %s", personnel_id, exc)
    finally:
        ws_manager.disconnect(personnel_id, ws)
