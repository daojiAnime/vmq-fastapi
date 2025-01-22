from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from sqlmodel import and_, col, delete, select, update

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models.order import Order
from app.schemas.order import MultiOrderPayload, OrderCreate, OrderList

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
        .where(and_(Order.uid == current_user.id, Order.real_price == order_in.real_price))
        .order_by(col(Order.id).desc())
    )
    order = session.exec(statement).first()
    if order and order.created_at > datetime.now() - timedelta(seconds=settings.ORDER_INTERVAL):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

    order_create = OrderCreate.model_validate(order_in, update={"uid": current_user.id})
    order = Order.model_validate(order_create)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.put("")
def update_order(session: SessionDep, payload: MultiOrderPayload, current_user: CurrentUser) -> Any:
    """
    Update orders by ids.
    """
    whereclause = [col(Order.id).in_(payload.ids)]
    if not current_user.is_superuser:
        whereclause.append(col(Order.uid) == current_user.id)
    statement = update(Order).where(*whereclause).values(payload.model_dump(exclude_unset=True))
    session.exec(statement)
    session.commit()


@router.delete("")
def delete_order(session: SessionDep, payload: MultiOrderPayload, current_user: CurrentUser) -> Any:
    """
    Delete orders by ids.
    """

    whereclause = [col(Order.id).in_(payload.ids)]
    if not current_user.is_superuser:
        whereclause.append(col(Order.uid) == current_user.id)
    statement = delete(Order).where(*whereclause)
    session.exec(statement)
    session.commit()
