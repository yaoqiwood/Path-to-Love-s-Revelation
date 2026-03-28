from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ==================== Common Schemas ====================


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


# ==================== Role Schemas ====================


class RoleBase(BaseModel):
    name: str
    code: str
    sort: int = 0
    enable_status: int = 1
    remark: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    sort: Optional[int] = None
    enable_status: Optional[int] = None
    remark: Optional[str] = None


class RoleResponse(RoleBase):
    id: int
    create_time: datetime

    class Config:
        from_attributes = True


# ==================== Menu Schemas ====================


class MenuBase(BaseModel):
    pid: int = 0
    menu_type: str  # M, C, A
    menu_name: str
    menu_icon: Optional[str] = None
    menu_sort: int = 0
    perms: Optional[str] = None
    paths: Optional[str] = None
    component: Optional[str] = None
    selected: Optional[str] = None
    params: Optional[str] = None
    cache_status: int = 0
    show_status: int = 1
    enable_status: int = 1


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    pid: Optional[int] = None
    menu_type: Optional[str] = None
    menu_name: Optional[str] = None
    menu_icon: Optional[str] = None
    menu_sort: Optional[int] = None
    perms: Optional[str] = None
    paths: Optional[str] = None
    component: Optional[str] = None
    selected: Optional[str] = None
    params: Optional[str] = None
    cache_status: Optional[int] = None
    show_status: Optional[int] = None
    enable_status: Optional[int] = None


class MenuResponse(MenuBase):
    id: int
    create_time: datetime
    children: List["MenuResponse"] = []

    class Config:
        from_attributes = True


# ==================== User Schemas ====================


class UserBase(BaseModel):
    username: str
    nickname: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None  # Compat
    user_code: Optional[str] = None
    feishu_id: Optional[str] = None
    enable_status: int = 1

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v):
        if v == "":
            return None
        return v


class UserCreate(UserBase):
    nickname: Optional[str] = None  # 注册时可选，后端会回退使用 username
    password: str
    role_ids: List[int]


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    user_code: Optional[str] = None
    feishu_id: Optional[str] = None
    enable_status: Optional[int] = None
    role_ids: Optional[List[int]] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v):
        if v == "":
            return None
        return v


class UserPasswordReset(BaseModel):
    password: str


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    enable_status: int
    is_active: bool
    create_time: datetime
    last_login_time: Optional[datetime] = None
    last_login_ip: Optional[str] = None

    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class UserPage(BaseModel):
    total: int
    items: List[UserResponse]


class UserLogin(BaseModel):
    username: str
    password: str


# ==================== Router/Menu Tree Schemas ====================


class UserInfoResponse(BaseModel):
    user: UserResponse
    roles: List[str]
    perms: List[str]


class RouterMeta(BaseModel):
    title: str
    icon: Optional[str] = None
    hidden: bool = False
    keepAlive: bool = True


class RouterVO(BaseModel):
    path: str
    component: str
    name: str  # menu_name or route name
    meta: RouterMeta
    children: List["RouterVO"] = []
