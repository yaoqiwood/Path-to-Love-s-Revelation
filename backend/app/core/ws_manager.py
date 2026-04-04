"""WebSocket 连接管理器 — 单例，管理在线用户的 WS 连接"""

from typing import Optional

from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """管理所有 WebSocket 连接，按 personnel_id 分组"""

    def __init__(self):
        # personnel_id -> list[WebSocket]
        self._connections: dict[str, list[WebSocket]] = {}
        # personnel_id -> {contactsVersion: int, inboxVersion: int}
        self._versions: dict[str, dict[str, int]] = {}

    async def connect(self, personnel_id: str, ws: WebSocket):
        await ws.accept()
        if personnel_id not in self._connections:
            self._connections[personnel_id] = []
        self._connections[personnel_id].append(ws)
        logger.info(
            "WS connected: personnel_id=%s, total=%d",
            personnel_id,
            len(self._connections[personnel_id]),
        )

    def disconnect(self, personnel_id: str, ws: WebSocket):
        conns = self._connections.get(personnel_id)
        if conns:
            try:
                conns.remove(ws)
            except ValueError:
                pass
            if not conns:
                del self._connections[personnel_id]
        logger.info("WS disconnected: personnel_id=%s", personnel_id)

    async def send_to_user(self, personnel_id: str, data: dict):
        """向指定用户的所有连接推送 JSON 消息"""
        conns = self._connections.get(personnel_id, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(personnel_id, ws)

    async def broadcast(self, data: dict):
        """广播给所有在线连接"""
        for personnel_id in list(self._connections.keys()):
            await self.send_to_user(personnel_id, data)

    def is_online(self, personnel_id: str) -> bool:
        return bool(self._connections.get(personnel_id))

    def online_count(self) -> int:
        return sum(len(v) for v in self._connections.values())

    def online_users(self) -> list[str]:
        return list(self._connections.keys())

    def bump_version(self, personnel_id: str, key: str = "contactsVersion"):
        """递增用户的版本号 (contacts / inbox)"""
        if personnel_id not in self._versions:
            self._versions[personnel_id] = {"contactsVersion": 0, "inboxVersion": 0}
        self._versions[personnel_id][key] = self._versions[personnel_id].get(key, 0) + 1

    def get_versions(self, personnel_id: str) -> dict:
        """获取用户当前版本号（内存缓存，不查 DB）"""
        return dict(self._versions.get(personnel_id, {"contactsVersion": 0, "inboxVersion": 0}))


# 全局单例
ws_manager = ConnectionManager()
