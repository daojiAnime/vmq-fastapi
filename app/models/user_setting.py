import secrets
import uuid
from decimal import Decimal
from functools import partial

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User

generate_ramdon_secret = partial(secrets.token_urlsafe, 32)


class UserSetting(SQLModel, table=True):
    __tablename__ = "user_setting"

    id: int | None = Field(default=None, primary_key=True)
    uid: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="setting")

    secret_key: str = Field(default_factory=generate_ramdon_secret, description="密钥", max_length=64)
    wechat_qrcode: str | None = Field(default=None, description="微信二维码")
    alipay_qrcode: str | None = Field(default=None, description="支付宝二维码")
    notify_url: str | None = Field(default=None, description="异步回调地址")
    return_url: str | None = Field(default=None, description="同步回调地址")
    app_id: str | None = Field(default_factory=generate_ramdon_secret, description="应用ID", max_length=64)
    order_interval: int = Field(default=60, description="订单创建间隔时间")
    is_order_price_increase: bool = Field(default=False, description="是否开启订单真实金额递增/递减")
    order_real_price_step: Decimal = Field(default=Decimal("0.01"), description="订单真实金额递增/递减的步长")
