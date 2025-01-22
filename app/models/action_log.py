import datetime
import uuid

from sqlmodel import Field, SQLModel


class ActionLog(SQLModel, table=True):
    __tablename__ = "action_log"

    id: int | None = Field(default=None, primary_key=True)
    uid: uuid.UUID | None = Field(default=None, description="用户ID")
    message: str = Field(description="消息")
    extra: str | None = Field(default=None, description="额外信息")
    ip: str = Field(default="未知", description="IP地址")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="创建时间")
