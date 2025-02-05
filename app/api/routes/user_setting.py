from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas import UserSettingBase

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
    current_user.setting.sqlmodel_update(user_setting_in)
    session.add(current_user.setting)
    session.commit()
    session.refresh(current_user.setting)
    return current_user.setting
