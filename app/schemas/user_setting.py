import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer
from sqlmodel import Field, SQLModel


def trans_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


TransDatetime = Annotated[datetime, PlainSerializer(trans_datetime, when_used="json")]


class UserSettingBase(SQLModel):
    id: int | None = Field(default=None, description="用户设置ID")
    uid: uuid.UUID | None = Field(default=None, description="用户ID")
    secret_key: str | None = Field(default=None, description="密钥", max_length=32)
    wechat_qrcode: str | None = Field(default=None, description="微信二维码")
    alipay_qrcode: str | None = Field(default=None, description="支付宝二维码")
    notify_url: str | None = Field(default=None, description="异步回调地址")
    return_url: str | None = Field(default=None, description="同步回调地址")
    app_id: str | None = Field(default=None, description="应用ID", max_length=64)
    order_interval: int | None = Field(default=None, description="订单创建间隔时间")
    is_order_price_increase: bool | None = Field(default=None, description="是否开启订单真实金额递增/递减")
    order_real_price_step: Decimal | None = Field(default=None, description="订单真实金额递增/递减的步长")


class UserSettingCreate(UserSettingBase):
    ...


class UserSettingList(SQLModel):
    items: list[UserSettingBase]
    total: int


class MultiUserSettingPayload(UserSettingBase):
    ids: list[int]
