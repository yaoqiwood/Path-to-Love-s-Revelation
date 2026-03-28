# 系统操作日志API端点

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.models.system_log import SystemLogOperate
from app.schemas.system_log_schema import SystemLogListResponse
from app.api.deps import CurrentUser

router = APIRouter()


@router.get("/", response_model=SystemLogListResponse)
async def list_system_logs(
    _current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    title: Optional[str] = Query(None, description="操作标题（模糊）"),
    username: Optional[str] = Query(None, description="操作人（模糊）"),
    business_type: Optional[int] = Query(
        None, description="业务类型（0其它 1新增 2修改 3删除）"
    ),
    status: Optional[int] = Query(None, description="操作状态（0正常 1异常）"),
    url: Optional[str] = Query(None, description="请求URL（模糊）"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_db),
):
    """分页查询系统操作日志"""
    stmt = select(SystemLogOperate)

    if title:
        stmt = stmt.where(SystemLogOperate.title.ilike(f"%{title}%"))
    if username:
        stmt = stmt.where(SystemLogOperate.username.ilike(f"%{username}%"))
    if business_type is not None:
        stmt = stmt.where(SystemLogOperate.business_type == business_type)
    if status is not None:
        stmt = stmt.where(SystemLogOperate.status == status)
    if url:
        stmt = stmt.where(SystemLogOperate.url.ilike(f"%{url}%"))
    if start_time:
        stmt = stmt.where(SystemLogOperate.create_time >= start_time)
    if end_time:
        stmt = stmt.where(SystemLogOperate.create_time <= end_time)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    data_result = await db.execute(
        stmt.order_by(SystemLogOperate.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = data_result.scalars().all()

    return {"items": items, "total": total}
