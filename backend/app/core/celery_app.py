# Celery核心配置

from celery import Celery
import os

from .config import settings

# ==================== 队列定义 ====================
# 默认只有一个通用队列
QUEUE_DEFAULT = "default_queue"

# 创建Celery实例
celery_app = Celery(
    "base_framework",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 加载配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    task_track_started=True,
    task_soft_time_limit=3600,
    task_time_limit=3700,
    worker_prefetch_multiplier=1,
    task_default_queue=QUEUE_DEFAULT,
    # Redis 优先级队列支持
    broker_transport_options={
        "priority_steps": list(range(10)),
        "sep": ":",
        "queue_order_strategy": "priority",
    },
    task_default_priority=5,
    task_routes={},
    task_annotations={},
)

# 自动发现任务模块
celery_app.autodiscover_tasks([])

# 定时任务调度 (Celery Beat)
celery_app.conf.beat_schedule = {}


# ==================== Worker 初始化钩子 ====================

from celery.signals import worker_init, setup_logging as celery_setup_logging


@celery_setup_logging.connect
def configure_celery_logging(**kwargs):
    """
    连接此信号后，Celery 不再自行配置日志，
    完全由项目的 setup_logging 接管，确保日志写入 celery.log。
    """
    from .logging import setup_logging

    setup_logging(log_filename="celery.log")


@worker_init.connect
def init_worker_services(**kwargs):
    """Worker 启动时初始化共享服务"""
    from .database import RedisSyncClient

    try:
        RedisSyncClient.connect()
    except Exception as e:
        print(f"[Celery Worker] Warning: Failed to connect Redis: {e}")
