from io import BytesIO
from typing import Any, Literal

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas import UserSettingBase
from app.utils.qrcode_parser import parse_qrcode

router = APIRouter()


@router.get("", response_model=UserSettingBase)
def get_user_setting(current_user: CurrentUser) -> Any:
    if not current_user.setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User setting not found")
    return current_user.setting


@router.put("", response_model=UserSettingBase)
def update_user_setting(session: SessionDep, user_setting_in: UserSettingBase, current_user: CurrentUser) -> Any:
    if not current_user.setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User setting not found")
    current_user.setting.sqlmodel_update(user_setting_in, update={"uid": current_user.id})
    session.add(current_user.setting)
    session.commit()
    session.refresh(current_user.setting)
    return current_user.setting


@router.post("/qrcode")
def upload_qrcode(
    session: SessionDep,
    current_user: CurrentUser,
    code_type: Literal["wechat", "alipay"] = Query(default="wechat"),
    file: UploadFile = File(...),
) -> Any:
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code image not found")
    qrcode_img_path = BytesIO(file.file.read())
    code = parse_qrcode(qrcode_img_path)
    if code_type == "wechat":
        # 解析微信二维码
        current_user.setting.wechat_qrcode = code
    elif code_type == "alipay":
        # 解析支付宝二维码
        current_user.setting.alipay_qrcode = code
    session.add(current_user.setting)
    session.commit()
    session.refresh(current_user.setting)
    return current_user.setting
