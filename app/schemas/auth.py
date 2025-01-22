from sqlmodel import Field, SQLModel


class LoginPayload(SQLModel):
    username: str
    password: str


class LoginResponse(SQLModel):
    access_token: str = Field(default=..., alias="accessToken", description="The access token")
    token_type: str = Field(default=..., alias="tokenType", description="The type of the token")


class RefreshResponse(SQLModel):
    data: str = Field(default=..., description="The new access token")
    status: int = Field(default=0, description="The status unused")
