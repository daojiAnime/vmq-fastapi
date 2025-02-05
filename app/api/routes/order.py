from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from sqlmodel import and_, col, delete, select, update

from app.api.deps import CurrentUser, SessionDep
from app.enums import OrderStatus
from app.models.order import Order
from app.schemas.order import MultiOrderPayload, OrderCreate, OrderList
from app.utils.math import find_next_price

router = APIRouter()


@router.get("", response_model=OrderList)
def read_orders(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve orders.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Order)
        count = session.exec(count_statement).one()
        statement = select(Order).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = select(func.count()).select_from(Order).where(Order.uid == current_user.id)
        count = session.exec(count_statement).one()
        statement = select(Order).where(Order.uid == current_user.id).offset(skip).limit(limit)
        items = session.exec(statement).all()

    return OrderList(items=items, total=count)


@router.post("", response_model=Order)
def create_order(session: SessionDep, order_in: OrderCreate, current_user: CurrentUser) -> Any:
    """
    Create new order.
    """
    statement = (
        select(Order)
        .where(and_(Order.uid == current_user.id, Order.price == order_in.price))
        .order_by(col(Order.id).desc())
    )
    real_price = order_in.price

    us = current_user.setting
    if us.is_order_price_increase:
        # 筛选出状态为 PENDING 的订单
        order = session.exec(statement.where(Order.state == OrderStatus.PENDING)).all()
        # 筛选出 ORDER_INTERVAL 间隔时间之内创建的订单
        order = [item for item in order if item.created_at > datetime.now() - timedelta(seconds=us.order_interval)]
        order = sorted(order, key=lambda x: x.real_price)
        # 找出连续的 real_price + order_real_price_step 不存在于订单中的 real_price 的金额
        real_price = find_next_price(order, order_in.price, us.order_real_price_step)
    else:
        order = session.exec(statement).one()
        if order and order.created_at > datetime.now() - timedelta(seconds=us.order_interval):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

    order_create = OrderCreate.model_validate(order_in)
    order = Order.model_validate(order_create, update={"real_price": real_price, "uid": current_user.id})
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.put("")
def update_order(session: SessionDep, payload: MultiOrderPayload, current_user: CurrentUser) -> Any:
    """
    Update orders by ids.
    """
    where_clause = [col(Order.id).in_(payload.ids)]
    if not current_user.is_superuser:
        where_clause.append(col(Order.uid) == current_user.id)
    statement = update(Order).where(*where_clause).values(payload.model_dump(exclude_unset=True))
    session.exec(statement)
    session.commit()


@router.delete("")
def delete_order(session: SessionDep, payload: MultiOrderPayload, current_user: CurrentUser) -> Any:
    """
    Delete orders by ids.
    """
    where_clause = [col(Order.id).in_(payload.ids)]
    if not current_user.is_superuser:
        where_clause.append(col(Order.uid) == current_user.id)
    statement = delete(Order).where(*where_clause)
    session.exec(statement)
    session.commit()
