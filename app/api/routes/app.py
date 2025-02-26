from datetime import datetime, timedelta
from hashlib import md5
from typing import Any

import httpx
import tenacity
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.core import logger, settings
from app.core.client import REDIS_MANAGER
from app.enums import OrderStatus, OrderType
from app.models.order import Order
from app.models.user_setting import UserSetting

router = APIRouter()


# Android APP
@router.get("/appHeart")
def app_heart(
    session: SessionDep,
    t: str = Query(default=..., description="时间戳"),
    sign: str = Query(default=..., description="签名"),
    app_id: str = Query(default=..., description="应用ID"),
) -> Any:
    """
    client heartbeat
    """
    statement = select(UserSetting).where(UserSetting.app_id == app_id)
    user_setting = session.exec(statement).first()
    if not user_setting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid App ID")

    # 10秒内有效
    if md5(f"{t}{user_setting.secret_key}".encode()).hexdigest() != sign:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Sign")

    REDIS_MANAGER.set_client_online(app_id, True)
    return user_setting


@router.post("/appPush")
def app_push(
    session: SessionDep,
    background_task: BackgroundTasks,
    pay_type: OrderType = Query(default=..., alias="type", description="支付类型"),
    price: float = Query(default=..., description="金额"),
    app_id: str = Query(default=..., description="应用ID"),
    sign: str = Query(default=..., description="签名"),
    t: int = Query(default=..., description="时间戳"),
) -> Any:
    """
    client push pay info
    """
    statement = select(UserSetting).where(UserSetting.app_id == app_id)
    user_setting = session.exec(statement).first()
    if not user_setting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid App ID")

    origin_text = f"{pay_type}{price}{t}{user_setting.secret_key}"
    if md5(origin_text.encode()).hexdigest() != sign:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Sign")

    # pay
    order_stmt = (
        select(Order)
        .where(Order.real_price == price)
        .where(Order.type == pay_type)
        .where(Order.created_at > datetime.fromtimestamp(t) - timedelta(seconds=user_setting.order_interval))
    )
    order = session.exec(order_stmt).first()
    if not order:
        # todo: 记录未知转账日志
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Order")

    order.state = OrderStatus.SUCCESS
    session.add(order)
    session.commit()
    session.refresh(order)

    notify_url = order.notify_url or user_setting.notify_url
    if notify_url:
        # 通知
        background_task.add_task(notify_order, order, OrderStatus.SUCCESS)
    background_task.add_task(REDIS_MANAGER.set_last_payment, app_id, order.created_at.isoformat())
    return order


@tenacity.retry(
    stop=tenacity.stop_after_attempt(settings.NOTIFY_RETRY_COUNT),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=15),
    before=tenacity.before_log(logger, logger.info),  # type: ignore
    after=tenacity.after_log(logger, logger.info),  # type: ignore
    retry_error_callback=lambda retry_state: logger.error(f"Notify Order Failed: {retry_state.outcome}"),
)
def notify_order(order: Order, state: OrderStatus) -> None:
    """通知回调方"""
    data = {
        "order_id": order.id,
        "pay_id": order.pay_id,
        "state": state.value,
        "type": order.type.value,
        "price": order.price,
        "real_price": order.real_price,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if order.callback_args:
        data.update(order.callback_args)
    if order.notify_url is None:
        raise Exception(f"Notify Order Failed: {order.id} | Notify URL is None")
    response = httpx.post(order.notify_url, json=data, timeout=30)
    if response.status_code != 200:
        # todo: 记录通知失败日志
        raise Exception(f"Notify Order Failed: {response.status_code} | {response.text}")

    logger.info(f"Notify Order Success: {order.id} | {response.text}")
