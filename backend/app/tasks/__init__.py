# Celery任务模块初始化

from ..core.celery_app import celery_app
from .render import (
    render_video_from_template,
    generate_thumbnails,
    convert_video,
)
from .export import export_materials, export_project, cleanup_old_exports
from .ai_gen import generate_video_from_images, generate_image_from_input

__all__ = [
    "celery_app",
    # 渲染任务
    "render_video_from_template",
    "generate_thumbnails",
    "convert_video",
    # 导出任务
    "export_materials",
    "export_project",
    "cleanup_old_exports",
    # AI生成任务
    "generate_video_from_images",
    "generate_image_from_input",
]
