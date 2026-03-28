from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Request,
    UploadFile,
    File,
    Form,
    Depends,
)
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime
from app.core.storage import storage_service
from app.core.logging import get_logger
from app.api.deps import get_current_user
from app.models.user import SystemUser
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response, StreamingResponse
from app.core.minio_client import MinioClient
from urllib.parse import unquote
from app.core.log_decorator import log_operate

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@log_operate(title="上传文件", business_type=1)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    sub_dir: str = Form("uploads"),  # 允许指定子目录，默认为 uploadsco
    current_user: SystemUser = Depends(get_current_user),
):
    """
    通用文件上传接口
    返回相对路径，可直接用于 cover_url 等字段
    """
    # 验证文件类型 (可选，这里做简单限制)
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail=f"不支持的文件类型: {file.content_type}, 仅支持图片"
        )

    # 生成文件名
    ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.{ext}"

    # 相对路径
    relative_path = f"{sub_dir}/{filename}"

    # 保存文件
    try:
        content = await file.read()
        storage_service.save_file(content, relative_path)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    # 返回相对路径和完整访问URL (如果配置了CDN/MinIO则返回对应的，这里返回相对路径供前端保存)
    return {
        "url": relative_path,
        "filename": filename,
        "size": len(content),
        "content_type": file.content_type,
    }


@router.api_route("/{file_path:path}", methods=["GET", "HEAD"])
async def get_storage_file(file_path: str, request: Request):
    """
    获取存储文件
    优先从本地获取，如果本地不存在则从 MinIO 代理回源 (解决 CORS 和 Range 问题)
    """

    # 1. 尝试本地获取
    # 使用 storage_service 获取本地绝对路径
    # 注意：这里我们只用 storage_service 获取路径逻辑，不触发生命周期的回源下载(因为我们要手动代理)
    file_path = unquote(file_path)
    local_abs_path = storage_service.get_local_abs_path(file_path)

    if os.path.exists(local_abs_path):
        response = FileResponse(local_abs_path)
        # 手动添加 CORS 头 (FileResponse 有时会丢失)
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # 2. 本地不存在，尝试 MinIO 代理
    if not MinioClient.is_enabled():
        raise HTTPException(status_code=404, detail="File not found")

    # MinIO 路径处理
    minio_path = file_path.replace("\\", "/")

    # 获取对象元数据
    stat = await run_in_threadpool(MinioClient.stat_object, minio_path)
    if not stat:
        raise HTTPException(status_code=404, detail="File not found in storage")

    file_size = stat.size
    content_type = stat.content_type or "application/octet-stream"

    # 处理 HEAD 请求
    if request.method == "HEAD":
        headers = {
            "Content-Length": str(file_size),
            "Content-Type": content_type,
            "Accept-Ranges": "bytes",
        }
        origin = request.headers.get("origin")
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
        else:
            headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        headers["Access-Control-Allow-Headers"] = "*"
        return Response(status_code=200, headers=headers)

    # 处理 Range 请求
    range_header = request.headers.get("range")
    offset = 0
    length = 0  # 0 means read until end
    status_code = 200
    content_length = file_size

    headers = {
        "Content-Type": content_type,
        "Accept-Ranges": "bytes",
    }

    if range_header:
        try:
            # Parse Range header: bytes=0-1024
            range_str = range_header.replace("bytes=", "")
            start_str, end_str = range_str.split("-")
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

            if start >= file_size:
                raise HTTPException(status_code=416, detail="Range not satisfiable")

            offset = start
            length = end - start + 1
            status_code = 206
            content_length = length
            headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        except ValueError:
            pass  # Invalid range, ignore

    headers["Content-Length"] = str(content_length)

    # 获取 MinIO 流
    # 注意：get_object_stream 这里我们假设它支持 offset 和 length (需要在 minio_client 中实现)
    minio_stream = await run_in_threadpool(
        MinioClient.get_object_stream, minio_path, offset=offset, length=length
    )

    if not minio_stream:
        raise HTTPException(status_code=500, detail="Failed to retrieve file stream")

    def iter_file():
        total_read = 0
        try:
            # 32KB chunks
            for chunk in minio_stream.stream(32 * 1024):
                total_read += len(chunk)
                yield chunk

            logger.debug(
                f"Stream finished. Total read: {total_read}, Expected: {content_length}"
            )
            if total_read != content_length:
                logger.warning(
                    f"MinIO stream ended early! Read {total_read} of {content_length}"
                )

        except GeneratorExit:
            logger.info("Client disconnected during MinIO streaming")
            return
        except Exception as e:
            logger.error(f"Error during MinIO streaming: {e}")
            # We cannot re-raise easily inside a generator to affect headers,
            # but it will cause the stream to abort, which Uvicorn might log.
            # Ideally we might want to close properly.
            raise e
        finally:
            logger.debug("Closing MinIO stream")
            minio_stream.close()
            minio_stream.release_conn()

            # 触发后台异步下载到本地，以便下次直接访问本地
            # 使用 storage_service 的内部方法触发
            try:
                storage_service.trigger_async_download(minio_path)
            except Exception as e:
                logger.warning(f"Failed to trigger async download: {e}")

    response = StreamingResponse(
        iter_file(), status_code=status_code, media_type=content_type, headers=headers
    )

    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"

    response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response
