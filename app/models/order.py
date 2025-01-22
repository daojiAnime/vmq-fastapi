import datetime
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

from app.enums import OrderStatus, OrderType
from app.models.user import User


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: int | None = Field(default=None, primary_key=True)
    uid: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="orders")

    type: OrderType = Field(description="订单类型")
    state: OrderStatus = Field(description="订单状态")
    pay_id: str = Field(unique=True, description="商户订单ID")
    price: Decimal = Field(description="订单金额")
    real_price: Decimal = Field(description="实际支付金额")
    notify_url: str | None = Field(default=None, description="异步回调地址")
    return_url: str | None = Field(default=None, description="同步回调地址")
    callback_args: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB), description="回调参数")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="更新时间",
        sa_column_kwargs={"onupdate": func.now()},
    )
