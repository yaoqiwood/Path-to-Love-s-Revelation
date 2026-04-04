from sqlalchemy import Boolean, Column, Integer, SmallInteger, String

from ..core.database import Base


class PersonnelUser(Base):
    """人员档案表"""

    __tablename__ = "personnel_user"

    id = Column(
        "_id",
        String(64),
        primary_key=True,
        comment="记录ID，如 personnel-101",
    )
    person_id = Column(Integer, nullable=False, unique=True, comment="人员编号")
    name = Column(String(64), nullable=False, default="", comment="姓名")
    nickname = Column(String(64), nullable=False, default="", comment="昵称")
    gender = Column(String(16), nullable=False, default="", comment="性别")
    age = Column(SmallInteger, nullable=True, comment="年龄")
    mobile = Column(String(20), nullable=False, default="", unique=True, comment="手机号")
    id_card_no = Column(
        String(18),
        nullable=False,
        default="",
        comment="身份证号",
    )
    mbti = Column(String(8), nullable=False, default="", comment="MBTI")
    native_place = Column(String(64), nullable=False, default="", comment="籍贯")
    profession = Column(String(128), nullable=False, default="", comment="职业")
    church = Column(String(128), nullable=False, default="", comment="教会/团契")
    faith_duration = Column(String(32), nullable=False, default="", comment="信主时长")
    referrer = Column(String(128), nullable=False, default="", comment="推荐人")
    self_introduction = Column(
        String(1000),
        nullable=False,
        default="",
        comment="自我介绍",
    )
    relationship_status = Column(
        String(32),
        nullable=False,
        default="",
        comment="感情状态",
    )
    travel_mode = Column(String(32), nullable=False, default="", comment="出行方式")
    address = Column(String(255), nullable=False, default="", comment="地址")
    family_overview = Column(
        String(1000),
        nullable=False,
        default="",
        comment="家庭概况",
    )
    review_status = Column(
        String(16),
        nullable=False,
        default="pending",
        comment="审核状态",
    )
    reviewer = Column(String(64), nullable=False, default="", comment="审核人")
    passcode = Column(String(32), nullable=False, default="", unique=True, comment="邀请码")
    user_role = Column(SmallInteger, nullable=False, default=0, comment="用户角色")
    personal_photo = Column(
        String(255),
        nullable=False,
        default="",
        comment="头像地址",
    )
    user_id = Column(String(64), nullable=False, default="", comment="绑定用户ID")
    private_message_quota = Column(
        Integer,
        nullable=False,
        default=0,
        comment="私信额度",
    )
    heart_message_quota = Column(
        Integer,
        nullable=False,
        default=0,
        comment="心动消息额度",
    )
    remaining_heart_value = Column(
        Integer,
        nullable=False,
        default=0,
        comment="剩余心动值",
    )
    remaining_mbti_test_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="剩余MBTI测试次数",
    )
    submitted_at = Column(
        String(40),
        nullable=False,
        default="",
        comment="提交时间(ISO8601)",
    )
    updated_at = Column(
        String(40),
        nullable=False,
        default="",
        comment="更新时间(ISO8601)",
    )
    is_deleted = Column(Boolean, nullable=False, default=False, comment="软删除")

    @property
    def id_card(self) -> str:
        return self.id_card_no or ""

    @id_card.setter
    def id_card(self, value: str) -> None:
        self.id_card_no = value or ""

    @property
    def remark(self) -> str:
        return ""
