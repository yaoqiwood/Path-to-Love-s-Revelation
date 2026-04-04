# 数据库连接配置

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import AsyncGenerator
import redis.asyncio as aioredis
import redis as sync_redis

from .config import settings


# ==================== MySQL (SQLAlchemy 异步 - FastAPI 用) ====================

# 注意：MYSQL_DATABASE_URL 的 scheme 需改为 mysql+aiomysql 或 mysql+asyncmy
# 例如: mysql+aiomysql://user:pass@host/db
engine = create_async_engine(
    settings.MYSQL_DATABASE_URL,
    pool_pre_ping=True,  # 使用前检测连接是否存活
    pool_size=20,  # 连接池基础大小
    max_overflow=20,  # 超出 pool_size 时允许的额外连接数
    pool_timeout=30,  # 等待连接的最长时间(秒)，超时抛出异常而非无限等待
    pool_recycle=1800,  # 30分钟回收连接，防止 MySQL 8h 自动断连
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 避免 commit 后访问对象时触发额外查询
    class_=AsyncSession,
)

Base = declarative_base()


# ==================== MySQL (SQLAlchemy 同步 - Celery worker 用) ====================

sync_engine = create_engine(
    settings.MYSQL_SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_sync_db():
    """获取同步数据库会话的上下文管理器（Celery 任务用）

    用法:
        with get_sync_db() as db:
            job = db.query(Model).filter(...).first()
            job.status = "DONE"
            # 退出时自动 commit / rollback / close
    """
    from contextlib import contextmanager

    @contextmanager
    def _ctx():
        db = SyncSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    return _ctx()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话的依赖项"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise



# ==================== Redis（异步 - FastAPI 用）====================


class RedisClient:
    """Redis 异步连接管理类（FastAPI 用）"""

    client: aioredis.Redis = None

    @classmethod
    async def connect(cls):
        """连接到Redis"""
        cls.client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        print(
            f"Connected to Redis (async): {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )

    @classmethod
    async def disconnect(cls):
        """断开Redis连接"""
        if cls.client:
            await cls.client.aclose()
            print("Disconnected from Redis (async)")

    @classmethod
    def get_client(cls) -> aioredis.Redis:
        """获取异步 Redis 客户端"""
        if cls.client is None:
            raise RuntimeError(
                "Redis未初始化，请在应用启动时调用 RedisClient.connect()"
            )
        return cls.client


def get_redis() -> aioredis.Redis:
    """获取异步 Redis 客户端（FastAPI 依赖项）"""
    return RedisClient.get_client()


# ==================== Redis（同步 - Celery worker 用）====================


class RedisSyncClient:
    """Redis 同步连接管理类（Celery worker 用）"""

    client: sync_redis.Redis = None

    @classmethod
    def connect(cls):
        """连接到Redis（同步）"""
        cls.client = sync_redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        # 验证连接
        cls.client.ping()
        print(
            f"Connected to Redis (sync): {settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )

    @classmethod
    def disconnect(cls):
        """断开Redis连接（同步）"""
        if cls.client:
            cls.client.close()
            print("Disconnected from Redis (sync)")

    @classmethod
    def get_client(cls) -> sync_redis.Redis:
        """获取同步 Redis 客户端"""
        if cls.client is None:
            raise RuntimeError(
                "Redis (sync) 未初始化，请调用 RedisSyncClient.connect()"
            )
        return cls.client


def get_redis_sync() -> sync_redis.Redis:
    """获取同步 Redis 客户端（Celery worker 用）"""
    return RedisSyncClient.get_client()
