from pydantic import Field
from sqlmodel import SQLModel


class UserInfo(SQLModel):
    roles: list[str] = Field(default=[], description="The user's roles")
    real_name: str = Field(default="", description="The user's real name")
    desc: str = Field(default="vben 用户自介绍", description="The user's description")
    home_path: str = Field(default="/dashboard", alias="homePath", description="The user's home path")
