# API端点初始化

from .user_api import router as users_router
from .api_config_api import router as configs_router
from .personnel_user_api import router as personnel_router
from .menu_api import router as menus_router
from .role_api import router as roles_router
from .system_log_api import router as system_logs_router
from .storage_api import router as storage_router
from .ws_chat import router as ws_router

__all__ = [
    "storage_router",
    "personnel_router",
    "users_router",
    "configs_router",
    "menus_router",
    "roles_router",
    "system_logs_router",
    "ws_router",
]
