# In Grace API - 主入口文件
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings

from app.core.database import Base, engine, RedisClient
from app.core.logging import setup_logging, get_logger

from app.core.exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

from app.api.endpoints import (
    users_router,
    configs_router,
    menus_router,
    roles_router,
    system_logs_router,
    storage_router,
)

# 初始化日志系统
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=settings.LOG_DIR,
    log_filename=settings.LOG_FILENAME,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT,
    enable_console=settings.LOG_ENABLE_CONSOLE,
    enable_file=settings.LOG_ENABLE_FILE,
    use_json_format=settings.LOG_USE_JSON,
)

# 获取日志器
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # 启动时执行

    logger.info("Starting In Grace API...")

    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


    # 连接Redis
    await RedisClient.connect()
    logger.info("Redis connected")

    # 确保存储目录存在
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    logger.info(f"Storage path: {settings.STORAGE_PATH}")

    yield

    # 关闭时执行

    logger.info("Shutting down In Grace API...")


    await RedisClient.disconnect()
    logger.info("Redis disconnected")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基础后端框架 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

logger.info("Global exception handlers registered")


@app.middleware("http")
async def add_cors_headers_for_preview(request: Request, call_next):

    response = await call_next(request)

    if request.url.path.startswith("/api/storage") or request.url.path.startswith(
        "/storage"
    ):
        origin = request.headers.get("origin")

        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response


# 注册API路由

app.include_router(
    users_router, prefix=f"{settings.API_PREFIX}/users", tags=["用户管理"]
)

app.include_router(
    configs_router,
    prefix=f"{settings.API_PREFIX}/configs",
    tags=["系统配置"],
)

app.include_router(
    menus_router,
    prefix=f"{settings.API_PREFIX}/menus",
    tags=["菜单管理"],
)

app.include_router(
    roles_router,
    prefix=f"{settings.API_PREFIX}/roles",
    tags=["角色管理"],
)

app.include_router(
    system_logs_router,
    prefix=f"{settings.API_PREFIX}/system-logs",
    tags=["操作日志"],
)

app.include_router(
    storage_router, prefix=f"{settings.API_PREFIX}/storage", tags=["存储服务"]
)
app.include_router(storage_router, prefix=f"/storage", tags=["存储服务"])


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""

    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["系统"])
async def root():
    """API根路径"""

    return {
        "message": "Welcome to In Grace API (Base Framework)",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        workers=1,
    )
