"""
用户管理服务
- 认证（注册、登录）
- 用户信息 & 动态路由
- 用户 CRUD 管理
"""

from typing import Optional, List, Annotated
from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    create_access_token,
    verify_password,
    Token,
)
from app.core.logging import get_logger
from app.models.user import SystemUser, SystemMenu
from app.repository import UserRepository
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserPage,
    UserInfoResponse,
    RouterVO,
    RouterMeta,
    UserPasswordReset,
    UserPasswordChange,
)
from app.core.exceptions import BizException, BizError

logger = get_logger(__name__)


class UserService:
    """用户服务，供 FastAPI 端点使用"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    # ==================== 认证 ====================

    async def register(self, user_data: UserCreate) -> SystemUser:
        """用户注册"""
        # 检查用户名
        existing = await self.repo.get_by_username(user_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )

        # 检查邮箱
        if user_data.email:
            existing_email = await self.repo.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
                )

        user = SystemUser(
            username=user_data.username,
            email=user_data.email,
            nickname=user_data.nickname or user_data.username,
            password=get_password_hash(user_data.password),
            salt="bcrypt",
            enable_status=1,
        )
        return await self.repo.create(user)

    async def login(self, user_data: UserLogin, client_ip: str = "") -> Token:
        """用户登录"""
        user = await self.repo.get_by_username(user_data.username)

        if not user or not verify_password(user_data.password, user.password):
            raise BizException(
                code=BizError.PASSWORD_ERROR,
                message="用户名或密码错误",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.enable_status:
            raise BizException(
                code=BizError.USER_DISABLED,
                message="用户已被禁用",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # 更新登录信息
        user.last_login_time = datetime.now()
        user.last_login_ip = client_ip
        await self.db.flush()

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        return Token(access_token=access_token, token_type="bearer")

    # ==================== 用户信息 & 路由 ====================

    async def get_user_info(self, current_user: SystemUser) -> UserInfoResponse:
        """获取当前用户信息、角色和权限"""
        roles = [r.code for r in current_user.roles]
        perms = set()

        role_ids = [r.id for r in current_user.roles]
        if role_ids:
            menus = await self.repo.get_menus_by_role_ids(role_ids)
            for menu in menus:
                if menu.perms:
                    perms.add(menu.perms)

        return UserInfoResponse(user=current_user, roles=roles, perms=list(perms))

    async def get_routers(self, current_user: SystemUser) -> List[RouterVO]:
        """获取动态路由（基于 RBAC）"""
        role_codes = [r.code for r in current_user.roles]
        is_admin = "admin" in role_codes

        if is_admin:
            all_menus = await self.repo.get_all_visible_menus()
        else:
            # 收集用户角色关联的菜单 ID
            menu_ids = set()
            role_ids = [r.id for r in current_user.roles]
            if role_ids:
                menus = await self.repo.get_menus_by_role_ids(role_ids)
                for menu in menus:
                    if (
                        menu.menu_type in ("M", "C")
                        and menu.enable_status == 1
                        and menu.show_status == 1
                    ):
                        menu_ids.add(menu.id)

            if not menu_ids:
                return []

            direct_menus = await self.repo.get_menus_by_ids(menu_ids)

            # 补充父级目录
            parent_ids = {
                m.pid for m in direct_menus if m.pid and m.pid not in menu_ids
            }
            if parent_ids:
                parent_menus = await self.repo.get_visible_menus_by_ids(parent_ids)
                all_menus = sorted(
                    list(direct_menus) + list(parent_menus),
                    key=lambda x: x.menu_sort,
                )
            else:
                all_menus = sorted(direct_menus, key=lambda x: x.menu_sort)

        return self._build_router_tree(all_menus)

    @staticmethod
    def _build_router_tree(menus: List[SystemMenu], pid: int = 0) -> List[RouterVO]:
        """构建菜单树"""
        routers = []
        for menu in menus:
            if menu.pid == pid:
                router_item = RouterVO(
                    path=menu.paths or "",
                    component=menu.component or "",
                    name=menu.menu_name,
                    meta=RouterMeta(
                        title=menu.menu_name,
                        icon=menu.menu_icon or "",
                        hidden=menu.show_status == 0,
                        keepAlive=menu.cache_status == 1,
                    ),
                )
                children = UserService._build_router_tree(menus, menu.id)
                if children:
                    router_item.children = children
                routers.append(router_item)
        return routers

    # ==================== 用户 CRUD 管理 ====================

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        enable_status: Optional[int] = None,
    ) -> UserPage:
        """分页获取用户列表"""
        items, total = await self.repo.list(
            username=username,
            enable_status=enable_status,
            page=page,
            page_size=page_size,
        )
        return UserPage(total=total, items=items)

    async def get_user(self, user_id: int) -> SystemUser:
        """获取用户详情，不存在则抛 404"""
        user = await self.repo.get_by_id_active(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(self, user_data: UserCreate, operator: str) -> SystemUser:
        """管理员新增用户"""
        existing = await self.repo.get_by_username(user_data.username)
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")

        new_user = SystemUser(
            username=user_data.username,
            nickname=user_data.nickname,
            password=get_password_hash(user_data.password),
            salt="bcrypt",
            email=user_data.email,
            enable_status=user_data.enable_status,
            user_code=user_data.user_code,
            feishu_id=user_data.feishu_id,
            create_by=operator,
        )

        if user_data.role_ids:
            new_user.roles = await self.repo.get_roles_by_ids(user_data.role_ids)

        return await self.repo.create(new_user)

    async def update_user(
        self, user_id: int, user_data: UserUpdate, operator: str
    ) -> SystemUser:
        """更新用户"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_data.nickname is not None:
            user.nickname = user_data.nickname
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.enable_status is not None:
            user.enable_status = user_data.enable_status
        if user_data.user_code is not None:
            user.user_code = user_data.user_code
        if user_data.feishu_id is not None:
            user.feishu_id = user_data.feishu_id
        if user_data.avatar is not None:
            user.avatar = user_data.avatar

        if user_data.role_ids is not None:
            user.roles = await self.repo.get_roles_by_ids(user_data.role_ids)

        user.update_by = operator
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: int, operator: str) -> dict:
        """软删除用户"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 软删除用户的同时清除其角色关联，以避免删除角色时因遗留关联引发外键冲突或业务阻拦
        user.roles = []
        user.del_status = 1
        user.update_by = operator
        await self.db.flush()

        return {"message": "Deleted successfully"}

    async def reset_password(
        self, user_id: int, data: UserPasswordReset, operator: str
    ) -> dict:
        """重置用户密码"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = get_password_hash(data.password)
        user.update_by = operator
        await self.db.flush()
        return {"message": "Password reset successfully"}

    async def change_password(
        self, current_user: SystemUser, data: UserPasswordChange
    ) -> dict:
        """修改个人密码"""
        if not verify_password(data.old_password, current_user.password):
            raise HTTPException(status_code=400, detail="旧密码错误")

        current_user.password = get_password_hash(data.new_password)
        await self.db.flush()
        return {"message": "Password changed successfully"}


# ==================== 依赖注入 ====================


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
