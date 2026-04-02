from typing import Optional

from fastapi import APIRouter, Body, Path, Query, Request

from app.api.deps import CurrentSuperUser, CurrentUser
from app.core.log_decorator import log_operate
from app.schemas.personnel_schema import (
    PersonnelCreate,
    PersonnelLoginConfirm,
    PersonnelLoginProfileResponse,
    PersonnelLoginTokenResponse,
    PersonnelListResponse,
    PersonnelResponse,
    PersonnelUpdate,
)
from app.services import PersonnelUserServiceDep

router = APIRouter()


@router.get("/login-profile", response_model=PersonnelLoginProfileResponse)
async def get_login_profile_by_passcode(
    service: PersonnelUserServiceDep,
    passcode: str = Query(..., description="登录口令", examples=["LOVE201"]),
):
    """根据口令匹配人员档案，用于前端二次确认"""
    return await service.get_login_profile_by_passcode(passcode)


@router.post("/login", response_model=PersonnelLoginTokenResponse)
async def login_by_passcode(
    request: Request,
    service: PersonnelUserServiceDep,
    data: PersonnelLoginConfirm = Body(
        ...,
        openapi_examples={
            "confirm": {
                "summary": "口令确认登录",
                "value": {
                    "passcode": "LOVE201",
                    "_id": "personnel-201",
                    "person_id": 201,
                    "name": "王弟兄",
                    "nickname": "同工小王",
                },
            }
        },
    ),
):
    """根据口令和前端确认的基础信息签发登录 token"""
    client_ip = request.client.host if request.client else ""
    return await service.login_by_passcode(data, client_ip=client_ip)


@router.get("/list", response_model=PersonnelListResponse)
async def list_personnel(
    current_user: CurrentUser,
    service: PersonnelUserServiceDep,
    page: int = Query(1, description="页码", examples=[1]),
    page_size: int = Query(10, description="每页条数", examples=[10]),
    keyword: Optional[str] = Query(
        None,
        description="搜索编号/昵称/姓名/手机号/MBTI/邀请码",
        examples=["王弟兄"],
    ),
    review_status: str = Query(
        "all",
        description="审核状态: all/pending/approved/rejected",
        examples=["approved"],
    ),
    include_deleted: bool = Query(
        False,
        description="是否包含已软删除数据",
        examples=[False],
    ),
):
    """分页获取人员档案列表"""
    return await service.list_personnel(
        page=page,
        page_size=page_size,
        keyword=keyword,
        review_status=review_status,
        include_deleted=include_deleted,
    )


@router.get("/{personnel_id}", response_model=PersonnelResponse)
async def get_personnel(
    current_user: CurrentUser,
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="人员记录ID", examples=["personnel-201"]),
):
    """获取人员档案详情"""
    return await service.get_personnel(personnel_id)


@router.post("/", response_model=PersonnelResponse)
@log_operate(title="新增人员档案", business_type=1)
async def create_personnel(
    request: Request,
    current_user: CurrentSuperUser,
    service: PersonnelUserServiceDep,
    data: PersonnelCreate = Body(
        ...,
        openapi_examples={
            "basic": {
                "summary": "基础新增示例",
                "value": {
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
                    "user_role": 0,
                },
            },
            "full": {
                "summary": "带自定义编号和邀请码",
                "value": {
                    "_id": "personnel-301",
                    "person_id": 301,
                    "nickname": "管理员小陈",
                    "name": "陈弟兄",
                    "gender": "男",
                    "age": 29,
                    "mobile": "13800138001",
                    "passcode": "LOVE301",
                    "mbti": "ENTJ",
                    "review_status": "approved",
                    "reviewer": "系统",
                    "user_role": 2,
                    "private_message_quota": 5,
                    "heart_message_quota": 5,
                    "remaining_heart_value": 5,
                },
            },
        },
    ),
):
    """新增人员档案"""
    return await service.create_personnel(data)


@router.put("/{personnel_id}", response_model=PersonnelResponse)
@log_operate(title="更新人员档案", business_type=2)
async def update_personnel(
    request: Request,
    current_user: CurrentSuperUser,
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="人员记录ID", examples=["personnel-201"]),
    data: PersonnelUpdate = Body(
        ...,
        openapi_examples={
            "review": {
                "summary": "审核通过",
                "value": {
                    "review_status": "approved",
                    "reviewer": "系统管理员",
                    "user_role": 1,
                },
            },
            "profile": {
                "summary": "更新基础资料",
                "value": {
                    "nickname": "同工小王",
                    "mbti": "ENFJ",
                    "profession": "运营经理",
                    "address": "福建省福州市台江区",
                    "private_message_quota": 2,
                },
            },
        },
    ),
):
    """更新人员档案"""
    return await service.update_personnel(personnel_id, data)


@router.delete("/{personnel_id}")
@log_operate(title="删除人员档案", business_type=3)
async def delete_personnel(
    request: Request,
    current_user: CurrentSuperUser,
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="人员记录ID", examples=["personnel-201"]),
):
    """软删除人员档案"""
    return await service.delete_personnel(personnel_id)
