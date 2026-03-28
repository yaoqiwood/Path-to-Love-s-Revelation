# 系统日志数据模型

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from datetime import datetime

from ..core.database import Base


class SystemLogOperate(Base):
    """系统操作日志表"""

    __tablename__ = "system_log_operate"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(BigInteger, default=0, comment="操作人ID")
    username = Column(String(255), nullable=True)
    title = Column(String(50), default="", comment="操作标题")
    business_type = Column(
        Integer, default=0, comment="业务类型（0其它 1新增 2修改 3删除）"
    )
    url = Column(String(200), nullable=False, default="", comment="请求URL")
    ip = Column(String(30), default="", comment="请求IP")
    location = Column(String(255), nullable=True, comment="操作地点")
    method = Column(String(100), default="", comment="方法名称")
    request_method = Column(String(10), default="", comment="请求方式")
    operator_type = Column(
        Integer, default=0, comment="操作类别（0其它 1后台用户 2手机端用户）"
    )
    param = Column(String(2000), default="", comment="请求参数")
    result = Column(String(2000), default="", comment="返回参数")
    status = Column(Integer, default=0, comment="操作状态（0正常 1异常）")
    error = Column(String(2000), nullable=True, comment="错误信息")
    cost_time = Column(BigInteger, default=0, comment="消耗时间")
    create_time = Column(
        DateTime, nullable=False, default=datetime.now, comment="操作时间"
    )

    def __repr__(self):
        return f"<SystemLogOperate(id={self.id}, title='{self.title}', username='{self.username}')>"
