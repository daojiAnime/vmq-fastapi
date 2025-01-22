from sqlmodel import Field, SQLModel


class UserInfo(SQLModel):
    roles: list[str] = Field(default=[], description="The user's roles")
    real_name: str = Field(default="", alias="realName", description="The user's real name")
