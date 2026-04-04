from typing import Optional

from fastapi import APIRouter, Body, Header, HTTPException, Path, Query, Request, status
from fastapi.responses import JSONResponse

from app.api.deps import CurrentSuperUser, CurrentUser
from app.core.exceptions import BizError, BizException
from app.core.log_decorator import log_operate
from app.schemas.personnel_schema import (
    PersonnelCreate,
    PersonnelDeleteResponse,
    PersonnelHeartHomeResponse,
    PersonnelHeartInboxResponse,
    PersonnelHeartMessageCreate,
    PersonnelHeartMessageCreateResponse,
    PersonnelHeartMessageHistoryResponse,
    PersonnelHeartStateResponse,
    PersonnelLoginConfirm,
    PersonnelLoginProfileResponse,
    PersonnelLoginTokenResponse,
    PersonnelListResponse,
    PersonnelMbtiUpdateByToken,
    PersonnelMbtiUpdateResult,
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


@router.post("/updateMbti", response_model=PersonnelMbtiUpdateResult)
async def update_personnel_mbti_by_token(
    service: PersonnelUserServiceDep,
    authorization: str = Header(..., alias="Authorization"),
    data: PersonnelMbtiUpdateByToken = Body(
        ...,
        openapi_examples={
            "update_mbti": {
                "summary": "通过请求头 token 更新 MBTI",
                "value": {
                    "mbti": "INFJ",
                },
            }
        },
    ),
):
    """从 Authorization 请求头获取 token，更新对应 personnel_user 的 MBTI"""
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise BizException(
                code=BizError.INVALID_CREDENTIALS,
                message="Authorization 请求头格式错误",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await service.update_mbti_by_token(token.strip(), data.mbti)
    except BizException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "result": False,
            },
            headers=exc.headers,
        )
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": BizError.BAD_REQUEST,
                "message": exc.detail,
                "result": False,
            },
            headers=exc.headers,
        )


@router.get("/", response_model=PersonnelListResponse)
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


@router.get("/opposite-gender-users", response_model=PersonnelHeartHomeResponse)
async def list_opposite_gender_users(
    service: PersonnelUserServiceDep,
    authorization: str = Header(..., alias="Authorization"),
    keyword: Optional[str] = Query(
        None,
        description="搜索昵称或姓名",
        examples=["林"],
    ),
):
    """获取当前用户的异性用户列表，按姓名排序"""
    return await service.list_opposite_gender_users(
        authorization=authorization,
        keyword=keyword,
    )


@router.get("/heart-home", response_model=PersonnelHeartHomeResponse)
async def get_current_personnel_heart_home(
    service: PersonnelUserServiceDep,
    authorization: str = Header(..., alias="Authorization"),
    keyword: Optional[str] = Query(
        None,
        description="搜索昵称或姓名",
        examples=["林"],
    ),
):
    """根据 token 获取当前用户的异性联系人列表"""
    return await service.get_heart_home(
        authorization=authorization,
        keyword=keyword,
    )


@router.get("/{personnel_id}/heart-home", response_model=PersonnelHeartHomeResponse)
async def get_personnel_heart_home_legacy(
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="当前人员记录ID", examples=["personnel-201"]),
    authorization: str = Header(..., alias="Authorization"),
    keyword: Optional[str] = Query(
        None,
        description="搜索昵称或姓名",
        examples=["林"],
    ),
):
    """兼容旧路径，根据 token 获取当前用户的异性联系人列表"""
    return await service.get_heart_home(
        authorization=authorization,
        keyword=keyword,
        personnel_id=personnel_id,
    )


@router.get("/{personnel_id}", response_model=PersonnelResponse)
async def get_personnel(
    current_user: CurrentUser,
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="人员记录ID", examples=["personnel-201"]),
):
    """获取人员档案详情"""
    return await service.get_personnel(personnel_id)


@router.get(
    "/{personnel_id}/heart-messages",
    response_model=PersonnelHeartMessageHistoryResponse,
)
async def list_personnel_heart_messages(
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="当前人员记录ID", examples=["personnel-201"]),
    contact_id: str = Query(
        ...,
        alias="contactId",
        description="聊天对象记录ID",
        examples=["personnel-202"],
    ),
    since: Optional[str] = Query(
        None,
        description="增量拉取起始时间，ISO8601 格式",
        examples=["2026-04-04T10:00:00.000Z"],
    ),
    authorization: str = Header(..., alias="Authorization"),
):
    """获取指定联系人历史聊天记录（按页面业务字段裁剪）"""
    return await service.list_heart_messages(
        personnel_id=personnel_id,
        contact_id=contact_id,
        since=since,
        authorization=authorization,
    )


@router.post(
    "/{personnel_id}/heart-messages",
    response_model=PersonnelHeartMessageCreateResponse,
)
async def create_personnel_heart_message(
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="当前人员记录ID", examples=["personnel-201"]),
    data: PersonnelHeartMessageCreate = Body(...),
    authorization: str = Header(..., alias="Authorization"),
):
    """发送心动消息"""
    return await service.send_heart_message(
        personnel_id=personnel_id,
        contact_id=data.contactId,
        content=data.content,
        scene=data.scene,
        authorization=authorization,
    )


@router.get(
    "/{personnel_id}/heart-inbox",
    response_model=PersonnelHeartInboxResponse,
)
async def list_personnel_heart_inbox(
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="当前人员记录ID", examples=["personnel-201"]),
    keyword: Optional[str] = Query(
        None,
        description="搜索关键字",
        examples=[""],
    ),
    authorization: str = Header(..., alias="Authorization"),
):
    """获取收信箱列表"""
    return await service.list_inbox(
        personnel_id=personnel_id,
        keyword=keyword,
        authorization=authorization,
    )


@router.get(
    "/{personnel_id}/heart-state",
    response_model=PersonnelHeartStateResponse,
)
async def get_personnel_heart_state(
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="当前人员记录ID", examples=["personnel-201"]),
    authorization: str = Header(..., alias="Authorization"),
):
    """获取消息状态版本号"""
    return await service.get_heart_state(
        personnel_id=personnel_id,
        authorization=authorization,
    )

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
                    "remaining_mbti_test_count": 0,
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


@router.delete("/{personnel_id}", response_model=PersonnelDeleteResponse)
@log_operate(title="删除人员档案", business_type=3)
async def delete_personnel(
    request: Request,
    current_user: CurrentSuperUser,
    service: PersonnelUserServiceDep,
    personnel_id: str = Path(..., description="人员记录ID", examples=["personnel-201"]),
):
    """软删除人员档案"""
    return await service.delete_personnel(personnel_id)
