from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class PersonnelSchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PersonnelPayloadBase(PersonnelSchemaBase):
    name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    mobile: Optional[str] = None
    id_card: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("id_card", "id_card_no"),
    )
    mbti: Optional[str] = None
    native_place: Optional[str] = None
    profession: Optional[str] = None
    church: Optional[str] = None
    faith_duration: Optional[str] = None
    referrer: Optional[str] = None
    self_introduction: Optional[str] = None
    relationship_status: Optional[str] = None
    travel_mode: Optional[str] = None
    address: Optional[str] = None
    family_overview: Optional[str] = None
    review_status: Optional[str] = None
    reviewer: Optional[str] = None
    passcode: Optional[str] = None
    user_role: Optional[int] = None
    personal_photo: Optional[str] = None
    user_id: Optional[str] = None
    private_message_quota: Optional[int] = None
    heart_message_quota: Optional[int] = None
    remaining_heart_value: Optional[int] = None
    remaining_mbti_test_count: Optional[int] = None
    submitted_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_deleted: Optional[bool] = None
    remark: Optional[str] = None


class PersonnelCreate(PersonnelPayloadBase):
    name: str
    nickname: str
    mobile: str
    person_id: Optional[int] = None
    id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("_id", "id"),
        serialization_alias="_id",
    )
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "nickname": "同工小王",
                "name": "王弟兄",
                "gender": "男",
                "age": 26,
                "mobile": "13800138000",
                "id_card": "350123200001010011",
                "mbti": "INFJ",
                "native_place": "福建福州",
                "profession": "产品经理",
                "church": "晨曦团契",
                "faith_duration": "5年",
                "referrer": "李姊妹",
                "self_introduction": "热爱服事，平时负责青年团契活动组织。",
                "relationship_status": "未婚单身",
                "travel_mode": "地铁",
                "address": "福建省福州市鼓楼区",
                "family_overview": "家中三口人，父母均为基督徒。",
                "review_status": "pending",
                "reviewer": "",
                "user_role": 0,
                "personal_photo": "",
                "user_id": "",
                "private_message_quota": 0,
                "heart_message_quota": 3,
                "remaining_heart_value": 3,
                "remaining_mbti_test_count": 0,
            }
        },
    )


class PersonnelUpdate(PersonnelPayloadBase):
    person_id: Optional[int] = None
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "nickname": "同工小王",
                "name": "王弟兄",
                "gender": "男",
                "age": 27,
                "mobile": "13800138000",
                "mbti": "ENFJ",
                "review_status": "approved",
                "reviewer": "系统管理员",
                "user_role": 1,
                "personal_photo": "https://cdn.example.com/avatar/personnel-204.jpg",
                "private_message_quota": 2,
                "heart_message_quota": 5,
                "remaining_heart_value": 4,
                "remaining_mbti_test_count": 0,
            }
        },
    )


class PersonnelResponse(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    person_id: int
    name: str
    nickname: str
    gender: str
    age: Optional[int] = None
    mobile: str
    id_card: str
    mbti: str
    native_place: str
    profession: str
    church: str
    faith_duration: str
    referrer: str
    self_introduction: str
    relationship_status: str
    travel_mode: str
    address: str
    family_overview: str
    review_status: str
    reviewer: str
    passcode: str
    user_role: int
    personal_photo: str
    user_id: str
    private_message_quota: int
    heart_message_quota: int
    remaining_heart_value: int
    remaining_mbti_test_count: int
    submitted_at: str
    updated_at: str
    is_deleted: bool
    remark: str = ""


class PersonnelLoginProfile(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    person_id: int
    nickname: str
    name: str
    passcode: str
    review_status: str
    user_role: int
    personal_photo: str
    user_id: str
    submitted_at: str
    updated_at: str


class PersonnelLoginRecord(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    person_id: int
    name: str
    nickname: str
    gender: str
    age: Optional[int] = None
    mobile: str
    mbti: str
    native_place: str
    profession: str
    church: str
    faith_duration: str
    referrer: str
    self_introduction: str
    relationship_status: str
    travel_mode: str
    address: str
    user_role: int
    personal_photo: str
    user_id: str
    private_message_quota: int
    heart_message_quota: int
    remaining_heart_value: int
    remaining_mbti_test_count: int
    submitted_at: str
    updated_at: str
    remark: str = ""


class PersonnelLoginProfileResponse(PersonnelSchemaBase):
    matched: bool
    record: Optional[PersonnelLoginProfile] = None


class PersonnelLoginConfirm(PersonnelSchemaBase):
    passcode: str
    personnel_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("_id", "personnel_id", "id"),
    )
    person_id: Optional[int] = None
    name: Optional[str] = None
    nickname: Optional[str] = None


class PersonnelLoginTokenResponse(PersonnelSchemaBase):
    access_token: str
    token_type: str = "bearer"
    profile: PersonnelLoginRecord


class PersonnelMbtiUpdateByToken(PersonnelSchemaBase):
    mbti: str
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "mbti": "INFJ",
            }
        },
    )


class PersonnelMbtiUpdateResult(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    name: str
    result: bool


class PersonnelDeleteResponse(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    deleted: bool


class PersonnelHeartMessageHistorySelf(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    person_id: int
    name: str
    nickname: str
    mbti: str
    personal_photo: str
    remaining_heart_value: int
    heart_message_quota: int
    remaining_mbti_test_count: int


class PersonnelHeartMessageHistoryContact(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    name: str
    nickname: str
    personal_photo: str
    mbti: str


class PersonnelHeartMessageHistoryItem(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    sender_record_id: str
    receiver_record_id: str
    content: str
    created_at: str
    created_at_text: str


class PersonnelHeartMessageHistoryResponse(PersonnelSchemaBase):
    self: PersonnelHeartMessageHistorySelf
    contact: PersonnelHeartMessageHistoryContact
    list: List[PersonnelHeartMessageHistoryItem]
    can_send: bool
    can_send_reason: str


class PersonnelHeartHomeSelf(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    person_id: int
    name: str
    nickname: str
    mbti: str
    personal_photo: str
    remaining_heart_value: int
    heart_message_quota: int


class PersonnelHeartHomeContact(PersonnelSchemaBase):
    id: str = Field(serialization_alias="_id")
    name: str
    nickname: str
    gender: str
    mbti: str
    personal_photo: str
    latest_message: str
    latest_message_at: str
    can_send: bool
    chat_status: str = ""


class PersonnelHeartHomeResponse(PersonnelSchemaBase):
    self: PersonnelHeartHomeSelf
    contacts: List[PersonnelHeartHomeContact]


class PersonnelListStats(PersonnelSchemaBase):
    total: int
    pending: int
    approved: int
    rejected: int


class PersonnelListResponse(PersonnelSchemaBase):
    list: List[PersonnelResponse]
    page: int
    page_size: int = Field(serialization_alias="pageSize")
    total: int
    stats: PersonnelListStats
