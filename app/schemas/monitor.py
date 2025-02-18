from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer
from sqlmodel import Field, SQLModel


def trans_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


TransDatetime = Annotated[datetime, PlainSerializer(trans_datetime, when_used="json")]


class MonitorState(SQLModel):
    state: bool = Field(default=False, description="监控端的状态")
    last_heartbeat: TransDatetime | None = Field(default=None, description="最后一次心跳时间")
    last_payment: TransDatetime | None = Field(default=None, description="最后一次支付时间")
    config_address: str | None = Field(default=None, description="配置地址")
