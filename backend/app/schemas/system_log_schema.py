# 系统操作日志 Schema

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class SystemLogResponse(BaseModel):
    """操作日志响应"""

    id: int
    user_id: int = 0
    username: Optional[str] = None
    title: str = ""
    business_type: int = 0
    url: str = ""
    ip: str = ""
    location: Optional[str] = None
    method: str = ""
    request_method: str = ""
    operator_type: int = 0
    param: str = ""
    result: str = ""
    status: int = 0
    error: Optional[str] = None
    cost_time: int = 0
    create_time: datetime

    class Config:
        from_attributes = True


class SystemLogListResponse(BaseModel):
    """操作日志分页响应"""

    total: int
    items: List[SystemLogResponse]
