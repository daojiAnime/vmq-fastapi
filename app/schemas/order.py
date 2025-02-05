import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import PlainSerializer
from sqlmodel import Field, SQLModel

from app.enums import OrderStatus, OrderType


def trans_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


TransDatetime = Annotated[datetime, PlainSerializer(trans_datetime, when_used="json")]


class OrderBase(SQLModel):
    id: int | None = Field(default=None, description="订单ID")
    uid: uuid.UUID | None = Field(default=None, description="用户ID")
    type: OrderType | None = Field(default=None, description="订单类型")
    state: OrderStatus | None = Field(default=None, description="订单状态")
    pay_id: str | None = Field(default=None, description="商户订单ID")
    price: Decimal | None = Field(default=None, description="订单金额")
    real_price: Decimal | None = Field(default=None, description="实际支付金额")
    notify_url: str | None = Field(default=None, description="异步回调地址")
    return_url: str | None = Field(default=None, description="同步回调地址")
    callback_args: dict[str, Any] | None = Field(default=None, description="回调参数")
    created_at: TransDatetime | None = Field(default=None, description="创建时间")
    updated_at: TransDatetime | None = Field(default=None, description="更新时间")


class OrderCreate(OrderBase):
    type: OrderType | None = Field(default=None, description="订单类型")
    pay_id: str | None = Field(default=None, description="商户订单ID")
    price: Decimal | None = Field(default=None, description="订单金额")
    real_price: Decimal | None = Field(default=None, description="实际支付金额")
    notify_url: str | None = Field(default=None, description="异步回调地址")
    return_url: str | None = Field(default=None, description="同步回调地址")
    callback_args: dict[str, Any] | None = Field(default=None, description="回调参数")


class OrderList(SQLModel):
    items: list[OrderBase]
    total: int


class MultiOrderPayload(OrderBase):
    ids: list[int]
