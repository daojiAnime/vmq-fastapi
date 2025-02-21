from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import and_, col, delete, select, update

from app.api.deps import CurrentUser, SessionDep
from app.enums import OrderStatus, OrderType
from app.models.order import Order
from app.schemas.order import MultiOrderPayload, OrderCreate, OrderList
from app.utils.math_tools import find_next_price

router = APIRouter()


@router.get("", response_model=OrderList)
def read_orders(
    session: SessionDep,
    current_user: CurrentUser,
    pay_id: str | None = Query(default=None, description="商户订单ID"),
    order_type: OrderType | None = Query(default=None, description="订单类型"),
    state: OrderStatus | None = Query(default=None, description="订单状态"),
    price: Decimal | None = Query(default=None, description="订单金额"),
    real_price: Decimal | None = Query(default=None, description="实际支付金额"),
    start: date | None = Query(default=None, description="开始时间"),
    end: date | None = Query(default=None, description="结束时间"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve orders.
    """
    # 用户权限条件
    # 修改后的过滤条件构建方式, 使用列表来构建查询条件
    conditions = [Order.uid == current_user.id]

    # 动态添加有效过滤条件
    if pay_id is not None:
        conditions.append(Order.pay_id == pay_id)
    if order_type is not None:
        conditions.append(Order.type == order_type)
    if state is not None:
        conditions.append(Order.state == state)
    if price is not None:
        conditions.append(Order.price == price)
    if real_price is not None:
        conditions.append(Order.real_price == real_price)
    if start is not None:
        conditions.append(Order.created_at >= start)
    if end is not None:
        conditions.append(Order.created_at <= end)

    # 构建基础查询
    base_query = select(Order).where(and_(*conditions))

    # 分页处理
    paginated_query = base_query.offset(skip).limit(limit)
    count_query = select(func.count()).select_from(base_query)

    # 执行查询
    count = session.exec(count_query).one()
    items = session.exec(paginated_query).all()

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
