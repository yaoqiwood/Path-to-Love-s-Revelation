# 用户数据模型

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    SmallInteger,
    BigInteger,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class SystemUser(Base):
    """系统管理成员表"""

    __tablename__ = "system_user"

    id = Column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键"
    )
    username = Column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
        default="",
        comment="用户账号",
    )
    nickname = Column(String(32), nullable=False, default="", comment="用户昵称")
    password = Column(String(200), nullable=False, default="", comment="用户密码")
    avatar = Column(String(200), nullable=False, default="", comment="用户头像")
    salt = Column(String(20), nullable=False, default="", comment="加密盐巴")
    enable_status = Column(
        SmallInteger, nullable=False, default=0, comment="是否启用: 0=否, 1=是"
    )
    last_login_ip = Column(String(20), nullable=False, default="", comment="最后登录IP")
    last_login_time = Column(DateTime, nullable=True, comment="最后登录")
    user_code = Column(String(32), nullable=True)
    feishu_id = Column(String(64), nullable=True, default=None, comment="飞书id")
    create_time = Column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_time = Column(
        DateTime, nullable=True, onupdate=datetime.utcnow, comment="更新时间"
    )
    create_by = Column(String(20), nullable=True)
    update_by = Column(String(20), nullable=True)
    del_status = Column(SmallInteger, nullable=False, default=0)

    # 为了兼容性保留
    email = Column(String(100), unique=True, index=True, nullable=True)

    # 关系
    roles = relationship(
        "SystemRole",
        secondary="system_user_role",
        back_populates="users",
        lazy="selectin",
    )

    # Backward compatibility for relationships

    @property
    def is_active(self):
        return self.enable_status == 1

    @property
    def full_name(self):
        return self.nickname

    @full_name.setter
    def full_name(self, value):
        self.nickname = value

    @property
    def hashed_password(self):
        return self.password

    @hashed_password.setter
    def hashed_password(self, value):
        self.password = value

    def __repr__(self):
        return f"<SystemUser(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"


class SystemRole(Base):
    """系统角色管理表"""

    __tablename__ = "system_role"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(20), nullable=False, default="", comment="角色名称")
    code = Column(
        String(20), nullable=False, unique=True, comment="角色编码"
    )  # Composite PK in SQL provided, using Flask-SQLAlchemy style might need adjustment but here we follow request
    remark = Column(String(200), default="", comment="备注信息")
    sort = Column(SmallInteger, nullable=False, default=0, comment="角色排序")
    enable_status = Column(
        SmallInteger, nullable=False, default=0, comment="是否禁用: 0=否, 1=是"
    )
    create_by = Column(String(20), nullable=True)
    update_by = Column(String(20), nullable=True)
    create_time = Column(
        DateTime, nullable=False, default=datetime.now, comment="创建时间"
    )
    update_time = Column(
        DateTime, nullable=True, onupdate=datetime.utcnow, comment="更新时间"
    )

    users = relationship(
        "SystemUser", secondary="system_user_role", back_populates="roles"
    )
    menus = relationship(
        "SystemMenu",
        secondary="system_role_menu",
        back_populates="roles",
    )

    def __repr__(self):
        return f"<SystemRole(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def is_superuser(self):
        return self.code == "admin"


class SystemUserRole(Base):
    """系统角色关联表"""

    __tablename__ = "system_user_role"

    user_id = Column(
        BigInteger,
        ForeignKey("system_user.id"),
        primary_key=True,
        nullable=False,
        default=0,
        comment="用户ID",
    )
    role_id = Column(
        Integer,
        ForeignKey("system_role.id"),
        primary_key=True,
        nullable=False,
        default=0,
        comment="角色ID",
    )


class SystemRoleMenu(Base):
    """系统角色菜单表"""

    __tablename__ = "system_role_menu"

    id = Column(String(100), primary_key=True, default="", comment="主键")
    role_id = Column(
        Integer,
        ForeignKey("system_role.id"),
        nullable=False,
        default=0,
        comment="角色ID",
    )
    menu_id = Column(
        Integer,
        ForeignKey("system_menu.id"),
        nullable=False,
        default=0,
        comment="菜单ID",
    )


class SystemMenu(Base):
    """系统菜单管理表"""

    __tablename__ = "system_menu"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    pid = Column(Integer, nullable=False, default=0, comment="上级菜单")
    menu_type = Column(
        String(2),
        nullable=False,
        default="",
        comment="权限类型: M=目录，C=菜单，A=按钮",
    )
    menu_name = Column(String(100), nullable=False, default="", comment="菜单名称")
    menu_icon = Column(String(100), nullable=False, default="", comment="菜单图标")
    menu_sort = Column(SmallInteger, nullable=False, default=0, comment="菜单排序")
    perms = Column(String(100), nullable=False, default="", comment="权限标识")
    paths = Column(String(100), nullable=False, default="", comment="路由地址")
    component = Column(String(200), nullable=False, default="", comment="前端组件")
    selected = Column(String(200), nullable=False, default="", comment="选中路径")
    params = Column(String(200), nullable=False, default="", comment="路由参数")
    cache_status = Column(
        SmallInteger, nullable=False, default=0, comment="是否缓存: 0=否, 1=是"
    )
    show_status = Column(
        SmallInteger, nullable=False, default=1, comment="是否显示: 0=否, 1=是"
    )
    enable_status = Column(
        SmallInteger, nullable=False, default=0, comment="是否禁用: 0=否, 1=是"
    )
    create_time = Column(DateTime, nullable=True, comment="创建时间")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
    create_by = Column(String(20), nullable=True)
    update_by = Column(String(20), nullable=True)

    roles = relationship(
        "SystemRole", secondary="system_role_menu", back_populates="menus"
    )

    def __repr__(self):
        return f"<SystemMenu(id={self.id}, menu_name='{self.menu_name}', menu_type='{self.menu_type}')>"
