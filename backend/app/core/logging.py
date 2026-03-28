# 日志系统配置
# 支持控制台输出、文件记录和日志轮转

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional

# Windows 平台使用 ConcurrentRotatingFileHandler 解决日志文件锁定问题
_USE_CONCURRENT_HANDLER = sys.platform == "win32"
if _USE_CONCURRENT_HANDLER:
    from concurrent_log_handler import ConcurrentRotatingFileHandler


class LoggerConfig:
    """日志配置管理类"""

    # 日志格式
    DEFAULT_FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )
    SIMPLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
    JSON_FORMAT = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "file": "%(filename)s", '
        '"line": %(lineno)d, "message": "%(message)s"}'
    )

    # 日志级别映射
    LEVEL_MAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(
        self,
        log_level: str = "INFO",
        log_dir: str = "./logs",
        log_filename: str = "app.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        rotation: str = "size",  # "size" or "time"
        enable_console: bool = True,
        enable_file: bool = True,
        use_json_format: bool = False,
    ):
        self.log_level = self.LEVEL_MAP.get(log_level.lower(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.log_filename = log_filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.rotation = rotation
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.use_json_format = use_json_format

        # 确保日志目录存在
        if self.enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    @property
    def log_format(self) -> str:
        """获取日志格式"""
        return self.JSON_FORMAT if self.use_json_format else self.DEFAULT_FORMAT

    def get_formatter(self) -> logging.Formatter:
        """创建日志格式化器"""
        return logging.Formatter(fmt=self.log_format, datefmt="%Y-%m-%d %H:%M:%S")

    def get_console_handler(self) -> logging.StreamHandler:
        """创建控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.log_level)
        handler.setFormatter(self.get_formatter())
        return handler

    def get_file_handler(self) -> logging.Handler:
        """创建文件处理器"""
        log_file = self.log_dir / self.log_filename

        if self.rotation == "time":
            handler = TimedRotatingFileHandler(
                filename=str(log_file),
                when="midnight",
                interval=1,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        elif _USE_CONCURRENT_HANDLER:
            handler = ConcurrentRotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        else:
            handler = RotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )

        handler.setLevel(self.log_level)
        handler.setFormatter(self.get_formatter())
        return handler

    def get_timed_file_handler(
        self,
        when: str = "midnight",
        interval: int = 1,
    ) -> TimedRotatingFileHandler:
        """创建文件处理器（按时间轮转）"""
        log_file = self.log_dir / self.log_filename
        handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when=when,
            interval=interval,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        handler.setLevel(self.log_level)
        handler.setFormatter(self.get_formatter())
        return handler

    def get_debug_file_handler(self) -> logging.Handler:
        """创建Debug日志专用处理器"""
        stem = Path(self.log_filename).stem  # app -> app, celery -> celery
        log_file = self.log_dir / f"{stem}_debug.log"

        if self.rotation == "time":
            handler = TimedRotatingFileHandler(
                filename=str(log_file),
                when="midnight",
                interval=1,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        elif _USE_CONCURRENT_HANDLER:
            handler = ConcurrentRotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        else:
            handler = RotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )

        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.get_formatter())
        return handler

    def get_error_file_handler(self) -> logging.Handler:
        """创建错误日志专用处理器"""
        stem = Path(self.log_filename).stem
        log_file = self.log_dir / f"{stem}_error.log"

        if self.rotation == "time":
            handler = TimedRotatingFileHandler(
                filename=str(log_file),
                when="midnight",
                interval=1,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        elif _USE_CONCURRENT_HANDLER:
            handler = ConcurrentRotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
        else:
            handler = RotatingFileHandler(
                filename=str(log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )

        handler.setLevel(logging.ERROR)
        handler.setFormatter(self.get_formatter())
        return handler


# 全局日志配置实例
_logger_config: Optional[LoggerConfig] = None
_loggers: dict[str, logging.Logger] = {}


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    log_filename: str = "app.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    rotation: str = "size",
    enable_console: bool = True,
    enable_file: bool = True,
    use_json_format: bool = False,
) -> LoggerConfig:
    """
    初始化日志系统

    Args:
        log_level: 日志级别 (debug/info/warning/error/critical)
        log_dir: 日志文件目录
        log_filename: 日志文件名
        max_bytes: 单个日志文件最大字节数
        backup_count: 日志文件保留数量
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件记录
        use_json_format: 是否使用JSON格式

    Returns:
        LoggerConfig: 日志配置实例
    """
    global _logger_config

    _logger_config = LoggerConfig(
        log_level=log_level,
        log_dir=log_dir,
        log_filename=log_filename,
        max_bytes=max_bytes,
        backup_count=backup_count,
        rotation=rotation,
        enable_console=enable_console,
        enable_file=enable_file,
        use_json_format=use_json_format,
    )

    # 配置根日志器
    # 将根日志级别强制设为 DEBUG，以便让所有日志流向 Handler，
    # 具体的过滤由 Handler 的 level 决定。
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 添加处理器
    if _logger_config.enable_console:
        root_logger.addHandler(_logger_config.get_console_handler())

    if _logger_config.enable_file:
        root_logger.addHandler(_logger_config.get_file_handler())
        root_logger.addHandler(
            _logger_config.get_debug_file_handler()
        )  # 添加 debug.log
        root_logger.addHandler(_logger_config.get_error_file_handler())

    # 配置第三方库日志级别
    third_party_level = max(_logger_config.log_level, logging.INFO)

    logging.getLogger("uvicorn").setLevel(third_party_level)
    logging.getLogger("uvicorn.access").setLevel(third_party_level)
    # SQL依然保持Warning以免刷屏，除非显式通过其他方式开启
    logging.getLogger("sqlalchemy.engine").setLevel(third_party_level)
    logging.getLogger("httpx").setLevel(third_party_level)
    logging.getLogger("httpcore").setLevel(third_party_level)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)  # 避免文件监控日志刷屏

    # 抑制 asyncio 的 ConnectionResetError 日志 (Windows 平台常见噪音)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    return _logger_config


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        logging.Logger: 日志器实例
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    return _loggers[name]


class LoggerMixin:
    """日志混入类，为类提供日志功能"""

    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志器"""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# 便捷的模块级日志器
logger = get_logger("creative_tools")
