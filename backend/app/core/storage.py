# 统一存储服务
# 实现「本地优先 + MinIO 镜像」混合存储策略

import os
import shutil
import zipfile
from typing import Optional, Union, BinaryIO, Dict, Any, List
from pathlib import Path

from datetime import datetime

from .config import settings
from .logging import get_logger
from .minio_client import MinioClient
from app.constants.storage_constant import STORAGE_DIRS

logger = get_logger(__name__)


class StorageService:
    """
    统一存储服务

    策略:
    - 写入: 同步写入本地 → 异步复制到 MinIO (如果启用)
    - 读取: 本地优先 → MinIO 回源 (如果启用且本地不存在)
    - 删除: 同时删除本地和 MinIO
    """

    def __init__(self):
        self.base_path = Path(settings.STORAGE_PATH).resolve()
        # 确保基础目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._ensure_base_structure()

    def _ensure_base_structure(self):
        """确保基础存储结构存在"""
        for d in STORAGE_DIRS:
            os.makedirs(os.path.join(self.base_path, d), exist_ok=True)

    def _get_local_path(self, relative_path: str) -> Path:
        """获取本地绝对路径"""
        return self.base_path / relative_path

    def _ensure_dir(self, file_path: Path):
        """确保文件所在目录存在"""
        file_path.parent.mkdir(parents=True, exist_ok=True)

    # ==================== 写入操作 ====================

    def save_file(
        self,
        content: Union[bytes, BinaryIO],
        relative_path: str,
        async_upload: bool = True,
    ) -> str:
        """
        保存文件到存储系统

        Args:
            content: 文件内容 (bytes 或 file-like object)
            relative_path: 相对路径 (如 "fonts/xxx.ttf")
            async_upload: 是否异步上传到 MinIO (默认 True)

        Returns:
            保存后的相对路径
        """
        local_path = self._get_local_path(relative_path)
        self._ensure_dir(local_path)

        # 1. 同步写入本地
        try:
            if isinstance(content, bytes):
                with open(local_path, "wb") as f:
                    f.write(content)
            else:
                # file-like object
                with open(local_path, "wb") as f:
                    shutil.copyfileobj(content, f)

            logger.debug(f"Saved to local: {relative_path}")

        except Exception as e:
            logger.error(f"Failed to save file locally: {e}")
            raise

        # 2. 上传到 MinIO (如果启用)
        if MinioClient.is_enabled() and async_upload:
            self._upload_to_minio(relative_path)

        return relative_path

    def save_uploaded_file(
        self,
        upload_file,  # FastAPI UploadFile
        relative_path: str,
    ) -> str:
        """
        保存 FastAPI UploadFile 到存储系统

        Args:
            upload_file: FastAPI 的 UploadFile 对象
            relative_path: 相对路径

        Returns:
            保存后的相对路径
        """
        local_path = self._get_local_path(relative_path)
        self._ensure_dir(local_path)

        try:
            with open(local_path, "wb") as f:
                shutil.copyfileobj(upload_file.file, f)

            logger.debug(f"Saved uploaded file to local: {relative_path}")

        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise

        # 上传到 MinIO
        if MinioClient.is_enabled():
            self._upload_to_minio(relative_path)

        return relative_path

    def _upload_to_minio(self, relative_path: str):
        """
        上传到 MinIO (根据配置决定同步或异步)
        """
        if settings.MINIO_ASYNC_UPLOAD:
            # 异步上传 (通过 Celery)
            self._trigger_async_upload(relative_path)
        else:
            # 同步上传
            self._sync_upload(relative_path)

    def _trigger_async_upload(self, relative_path: str):
        """触发异步上传任务"""
        try:
            from ..tasks.storage_tasks import upload_to_minio

            upload_to_minio.delay(relative_path)
            logger.debug(f"Triggered async upload for: {relative_path}")
        except Exception as e:
            logger.warning(f"Failed to trigger async upload: {e}")

    def _sync_upload(self, relative_path: str):
        """同步上传到 MinIO"""
        try:
            local_path = self._get_local_path(relative_path)
            # MinIO 使用正斜杠
            minio_path = relative_path.replace("\\", "/")
            if MinioClient.upload_file(str(local_path), minio_path):
                logger.info(f"Sync uploaded to MinIO: {minio_path}")
            else:
                logger.error(f"Sync upload failed: {minio_path}")
        except Exception as e:
            logger.error(f"Sync upload error: {e}")

    def move_file(self, src_relative_path: str, dest_relative_path: str) -> bool:
        """
        移动文件 (同时处理本地和 MinIO)
        """
        success = False

        # 1. 本地移动
        src_local = self._get_local_path(src_relative_path)
        dest_local = self._get_local_path(dest_relative_path)

        if src_local.exists():
            self._ensure_dir(dest_local)
            try:
                shutil.move(str(src_local), str(dest_local))
                logger.debug(
                    f"Moved local file: {src_relative_path} -> {dest_relative_path}"
                )
                success = True
            except Exception as e:
                logger.error(f"Failed to move local file: {e}")
                # Don't return False yet, MinIO move might still succeed if local missing but MinIO present

        # 2. MinIO 移动 (Copy + Delete)
        if MinioClient.is_enabled():
            # MinIO paths use forward slashes
            src_minio = src_relative_path.replace("\\", "/")
            dest_minio = dest_relative_path.replace("\\", "/")

            if MinioClient.file_exists(src_minio):
                if MinioClient.copy_object(src_minio, dest_minio):
                    MinioClient.delete_file(src_minio)
                    logger.debug(f"Moved MinIO file: {src_minio} -> {dest_minio}")
                    success = True
                else:
                    logger.error(
                        f"Failed to move MinIO file: {src_minio} -> {dest_minio}"
                    )

        return success

    # ==================== 读取操作 ====================

    def get_file_path(
        self,
        relative_path: str,
        fallback_minio: bool = True,
        sync_download: bool = False,
    ) -> Optional[str]:
        """
        获取文件的本地路径
        如果本地不存在且 MinIO 启用，会尝试从 MinIO 回源

        Args:
            relative_path: 相对路径
            fallback_minio: 是否启用 MinIO 回源 (默认 True)
            sync_download: 如果发生回源，是否同步下载并返回本地路径 (默认 False，不阻塞，触发异步下载返回预签名 URL)

        Returns:
            本地绝对路径，如果不是同步下载并且文件不存在本地则可能返回 MinIO URL，如果文件不存在返回 None
        """
        local_path = self._get_local_path(relative_path)

        # 1. 本地存在，直接返回
        if local_path.exists():
            return str(local_path)

        # 2. 本地不存在，尝试从 MinIO 回源
        if fallback_minio and MinioClient.is_enabled():
            # MinIO 使用正斜杠，Windows 路径使用反斜杠，需要统一
            minio_path = relative_path.replace("\\", "/")

            # 使用同步检查是否存在 (stat_object 很快)
            if MinioClient.file_exists(minio_path):
                logger.info(f"Local file missing, found in MinIO: {minio_path}")

                if sync_download:
                    # 同步下载并返回本地路径
                    if MinioClient.download_file(minio_path, str(local_path)):
                        return str(local_path)
                    else:
                        logger.error(
                            f"Failed to sync download from MinIO: {minio_path}"
                        )
                        return None
                else:
                    # 触发异步回源 (下载到本地)
                    self.trigger_async_download(minio_path)

                    # 返回 MinIO 访问 URL (让前端直接访问 MinIO，避免阻塞)
                    # 优先使用预签名 URL 以确保安全性，如果需要公开访问改用 get_public_url
                    return MinioClient.get_presigned_url(minio_path)
            else:
                logger.warning(f"File not found in MinIO: {minio_path}")

        return None

    def trigger_async_download(self, relative_path: str):
        """触发异步回源下载任务"""
        try:
            from ..tasks.storage_tasks import sync_from_minio

            sync_from_minio.delay(relative_path)
            logger.debug(f"Triggered async download for: {relative_path}")
        except Exception as e:
            logger.warning(f"Failed to trigger async download: {e}")

    def get_file_content(self, relative_path: str) -> Optional[bytes]:
        """
        读取文件内容

        Args:
            relative_path: 相对路径

        Returns:
            文件内容 (bytes)，如果不存在返回 None
        """
        file_path = self.get_file_path(relative_path)
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        return None

    def file_exists(self, relative_path: str, check_minio: bool = True) -> bool:
        """
        检查文件是否存在

        Args:
            relative_path: 相对路径
            check_minio: 是否检查 MinIO (默认 True)

        Returns:
            是否存在
        """
        local_path = self._get_local_path(relative_path)

        if local_path.exists():
            return True

        if check_minio and MinioClient.is_enabled():
            return MinioClient.file_exists(relative_path)

        return False

    # ==================== 删除操作 ====================

    def delete_file(self, relative_path: str) -> bool:
        """
        删除文件 (同时删除本地和 MinIO)

        Args:
            relative_path: 相对路径

        Returns:
            是否成功 (只要有一个成功就返回 True)
        """
        success = False

        # 1. 删除本地
        local_path = self._get_local_path(relative_path)
        if local_path.exists():
            try:
                os.remove(local_path)
                logger.debug(f"Deleted local file: {relative_path}")
                success = True
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")

        # 2. 删除 MinIO
        if MinioClient.is_enabled():
            if MinioClient.delete_file(relative_path):
                success = True

        return success

    # ==================== URL 生成 ====================
    @staticmethod
    def get_url(relative_path: str, use_minio: bool = False) -> str:
        """
        获取文件访问 URL

        Args:
            relative_path: 相对路径
            use_minio: 是否使用 MinIO URL (默认使用本地相对路径)

        Returns:
            访问 URL
        """
        if use_minio and MinioClient.is_enabled():
            return MinioClient.get_public_url(relative_path)

        # 返回相对路径，由前端或 Nginx 处理
        return f"/storage/{relative_path}"

    @staticmethod
    def get_presigned_url(relative_path: str, expires: int = 3600) -> Optional[str]:
        """
        获取 MinIO 预签名 URL (临时访问)

        Args:
            relative_path: 相对路径
            expires: 过期时间 (秒)

        Returns:
            预签名 URL，如果未启用 MinIO 返回 None
        """
        if MinioClient.is_enabled():
            return MinioClient.get_presigned_url(relative_path, expires)
        return None

    # ==================== 工具方法 ====================

    def get_local_abs_path(self, relative_path: str) -> str:
        """
        获取本地绝对路径 (不检查是否存在)

        Args:
            relative_path: 相对路径

        Returns:
            本地绝对路径
        """
        return str(self._get_local_path(relative_path))

    def get_relative_path(self, absolute_path: str) -> str:
        """
        将绝对路径转换为相对于 storage 根目录的相对路径

        Args:
            absolute_path: 绝对路径

        Returns:
            相对路径（使用正斜杠）

        Raises:
            ValueError: 路径不在 storage 根目录下
        """
        abs_p = Path(absolute_path).resolve()
        try:
            rel = abs_p.relative_to(self.base_path)
            return str(rel).replace("\\", "/")
        except ValueError:
            raise ValueError(
                f"路径不在 storage 根目录下: {absolute_path} (base={self.base_path})"
            )

    def sync_to_minio(self, relative_path: str) -> bool:
        """
        手动同步文件到 MinIO (同步执行)

        Args:
            relative_path: 相对路径

        Returns:
            是否成功
        """
        if not MinioClient.is_enabled():
            return False

        local_path = self._get_local_path(relative_path)
        if not local_path.exists():
            logger.warning(f"Cannot sync, local file not found: {relative_path}")
            return False

        return MinioClient.upload_file(str(local_path), relative_path)

    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        stats = {"total_size": 0, "file_count": 0, "directories": {}}

        for root, dirs, files in os.walk(self.base_path):
            for f in files:
                file_path = os.path.join(root, f)
                stats["total_size"] += os.path.getsize(file_path)
                stats["file_count"] += 1

        # 各目录统计
        for d in STORAGE_DIRS:
            dir_path = os.path.join(self.base_path, d)
            if os.path.exists(dir_path):
                size = 0
                count = 0
                for root, dirs, files in os.walk(dir_path):
                    for f in files:
                        size += os.path.getsize(os.path.join(root, f))
                        count += 1
                stats["directories"][d] = {"size": size, "count": count}

        return stats

    def get_project_storage_path(self, project_id: int, subdir: str = None) -> str:
        """获取项目存储路径"""
        path = os.path.join(self.base_path, "projects", str(project_id))
        if subdir:
            path = os.path.join(path, subdir)
        os.makedirs(path, exist_ok=True)
        return path

    def archive_project(self, project_id: int, archive_name: str = None) -> str:
        """归档项目到备份目录"""
        project_path = self.get_project_storage_path(project_id)

        if not os.path.exists(project_path):
            raise ValueError(f"Project {project_id} storage not found")

        # 生成归档文件名
        if not archive_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"project_{project_id}_{timestamp}"

        backup_dir = os.path.join(self.base_path, "backups")
        archive_path = os.path.join(backup_dir, f"{archive_name}.zip")

        # 创建ZIP归档
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arc_name)

        return archive_path

    def restore_project(self, archive_path: str, project_id: int) -> str:
        """从归档恢复项目"""
        if not os.path.exists(archive_path):
            raise ValueError(f"Archive not found: {archive_path}")

        project_path = self.get_project_storage_path(project_id)

        # 清空现有目录
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        os.makedirs(project_path)

        # 解压归档
        with zipfile.ZipFile(archive_path, "r") as zipf:
            zipf.extractall(project_path)

        return project_path

    def export_materials(self, file_paths: List[str], export_name: str = None) -> str:
        """导出素材为ZIP包"""
        if not export_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"export_{timestamp}"

        export_dir = os.path.join(self.base_path, "exports")
        export_path = os.path.join(export_dir, f"{export_name}.zip")

        with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)

        return export_path

    def get_temp_storage_path(self, subdir: str = None) -> str:
        """获取项目存储路径"""
        if not subdir:
            path = os.path.join(self.base_path, "temp")
        else:
            path = os.path.join(self.base_path, "temp", subdir)
            os.makedirs(path, exist_ok=True)
        return path

    def cleanup_temp(self, max_age_hours: int = 24) -> int:
        """清理临时文件"""
        temp_dir = os.path.join(self.base_path, "temp")
        deleted_count = 0

        if not os.path.exists(temp_dir):
            return 0

        now = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except:
                        pass

        return deleted_count

    def delete_project_storage(self, project_id: int) -> bool:
        """删除项目存储"""
        project_path = os.path.join(self.base_path, "projects", str(project_id))

        if os.path.exists(project_path):
            try:
                shutil.rmtree(project_path)
                return True
            except:
                return False
        return True

    def get_project_files(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目所有文件列表"""
        project_path = self.get_project_storage_path(project_id)
        files = []

        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, project_path)
                stat = os.stat(file_path)

                files.append(
                    {
                        "name": filename,
                        "path": rel_path,
                        "full_path": file_path,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    }
                )

        return files


# 全局存储服务实例
storage_service = StorageService()
