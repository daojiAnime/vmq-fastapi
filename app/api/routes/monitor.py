from typing import Any

from fastapi import APIRouter

from app import schemas
from app.api.deps import CurrentUser
from app.core import settings
from app.core.client import REDIS_MANAGER

router = APIRouter()


@router.get("/state", response_model=schemas.MonitorState)
def monitor_order(current_user: CurrentUser) -> Any:
    """
    监控状态
    """
    last_heartbeat = REDIS_MANAGER.get_last_heartbeat(str(current_user.id))
    last_payment = REDIS_MANAGER.get_last_payment(str(current_user.id))
    state = REDIS_MANAGER.is_client_online(str(current_user.id))
    monitor_state = schemas.MonitorState(
        state=state,
        last_heartbeat=last_heartbeat or None,
        last_payment=last_payment or None,
        config_address=f"{settings.FRONTEND_HOST}{settings.API_V1_STR}",
    )
    return monitor_state
