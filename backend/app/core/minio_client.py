# MinIO 客户端封装

import os
from typing import Optional, BinaryIO
from datetime import timedelta

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

# MinIO 客户端实例 (延迟初始化)
_minio_client = None


def get_minio_client():
    """
    获取 MinIO 客户端实例 (单例模式)
    仅在 MINIO_ENABLED=True 时初始化
    """
    global _minio_client

    if not settings.MINIO_ENABLED:
        return None

    if _minio_client is None:
        try:
            from minio import Minio

            logger.info(
                f"MinIO client not initialized: {settings.MINIO_ENDPOINT}, {settings.MINIO_BUCKET}"
            )

            _minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )

            # 确保 Bucket 存在
            if not _minio_client.bucket_exists(settings.MINIO_BUCKET):
                _minio_client.make_bucket(settings.MINIO_BUCKET)
                logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")

            logger.info(f"MinIO client initialized: {settings.MINIO_ENDPOINT}")

        except ImportError:
            logger.error("minio package not installed. Run: pip install minio")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            return None

    return _minio_client


class MinioClient:
    """
    MinIO 操作封装类
    提供上传、下载、删除、URL 生成等功能
    """

    @staticmethod
    def is_enabled() -> bool:
        """检查 MinIO 是否启用"""
        return settings.MINIO_ENABLED

    @staticmethod
    def upload_file(local_path: str, object_name: str) -> bool:
        """
        上传本地文件到 MinIO

        Args:
            local_path: 本地文件绝对路径
            object_name: MinIO 中的对象名称 (相对路径)

        Returns:
            是否上传成功
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            client.fput_object(
                settings.MINIO_BUCKET,
                object_name,
                local_path,
            )
            logger.debug(f"Uploaded to MinIO: {object_name}")
            return True
        except Exception as e:
            logger.error(f"MinIO upload failed for {object_name}: {e}")
            return False

    @staticmethod
    def upload_stream(file_obj: BinaryIO, object_name: str, length: int = -1) -> bool:
        """
        上传文件流到 MinIO

        Args:
            file_obj: 文件对象 (file-like object)
            object_name: MinIO 中的对象名称
            length: 文件长度 (-1 表示未知，将使用分块上传)

        Returns:
            是否上传成功
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                file_obj,
                length=length,
                part_size=10 * 1024 * 1024,  # 10MB 分块
            )
            logger.debug(f"Uploaded stream to MinIO: {object_name}")
            return True
        except Exception as e:
            logger.error(f"MinIO stream upload failed for {object_name}: {e}")
            return False

    @staticmethod
    def download_file(object_name: str, local_path: str) -> bool:
        """
        从 MinIO 下载文件到本地

        Args:
            object_name: MinIO 中的对象名称
            local_path: 本地保存路径

        Returns:
            是否下载成功
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            client.fget_object(
                settings.MINIO_BUCKET,
                object_name,
                local_path,
            )
            logger.debug(f"Downloaded from MinIO: {object_name} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"MinIO download failed for {object_name}: {e}")
            return False

    @staticmethod
    def delete_file(object_name: str) -> bool:
        """
        从 MinIO 删除文件

        Args:
            object_name: MinIO 中的对象名称

        Returns:
            是否删除成功
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            client.remove_object(settings.MINIO_BUCKET, object_name)
            logger.debug(f"Deleted from MinIO: {object_name}")
            return True
        except Exception as e:
            logger.error(f"MinIO delete failed for {object_name}: {e}")
            return False

    @staticmethod
    def file_exists(object_name: str) -> bool:
        """
        检查文件是否存在于 MinIO

        Args:
            object_name: MinIO 中的对象名称

        Returns:
            是否存在
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            client.stat_object(settings.MINIO_BUCKET, object_name)
            return True
        except Exception:
            return False

    @staticmethod
    def get_presigned_url(object_name: str, expires: int = 6000) -> Optional[str]:
        """
        获取预签名 URL (用于临时访问)

        Args:
            object_name: MinIO 中的对象名称
            expires: 过期时间 (秒)

        Returns:
            预签名 URL 或 None
        """
        client = get_minio_client()
        if not client:
            return None

        try:
            url = client.presigned_get_object(
                settings.MINIO_BUCKET,
                object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            return None

    @staticmethod
    def get_public_url(object_name: str) -> str:
        """
        获取公开访问 URL (需要 Bucket 设置为公开或配置代理)

        Args:
            object_name: MinIO 中的对象名称

        Returns:
            公开 URL
        """
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_name}"

    @staticmethod
    def get_object_stream(object_name: str, offset: int = 0, length: int = 0):
        """
        获取对象流 (支持分片读取)

        Args:
            object_name: 对象名称
            offset: 偏移量
            length: 读取长度 (0 表示读取到最后)

        Returns:
            response 对象 (urllib3.response.HTTPResponse)
        """
        client = get_minio_client()
        if not client:
            return None

        try:
            # get_object 返回的是 urllib3.response.HTTPResponse
            # 调用者需要负责关闭 response (response.close() or response.release_conn())
            return client.get_object(
                settings.MINIO_BUCKET,
                object_name,
                offset=offset,
                length=length if length > 0 else None,
            )
        except Exception as e:
            logger.error(f"Failed to get object stream for {object_name}: {e}")
            return None

    @staticmethod
    def stat_object(object_name: str):
        """获取对象元数据"""
        client = get_minio_client()
        if not client:
            return None
        try:
            return client.stat_object(settings.MINIO_BUCKET, object_name)
        except Exception:
            return None

    @staticmethod
    def copy_object(source_object_name: str, dest_object_name: str) -> bool:
        """
        在 MinIO 中复制对象
        """
        client = get_minio_client()
        if not client:
            return False

        try:
            from minio.commonconfig import CopySource

            client.copy_object(
                settings.MINIO_BUCKET,
                dest_object_name,
                CopySource(settings.MINIO_BUCKET, source_object_name),
            )
            logger.debug(f"Copied in MinIO: {source_object_name} -> {dest_object_name}")
            return True
        except Exception as e:
            logger.error(f"MinIO copy failed: {e}")
            return False
