from pydantic import BaseModel, ConfigDict, Field


class LoginPayload(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str = Field(default=..., alias="accessToken", description="The access token")
    token_type: str = Field(default=..., alias="tokenType", description="The type of the token")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class RefreshResponse(BaseModel):
    data: str = Field(default=..., description="The new access token")
    status: int = Field(default=0, description="The status unused")
