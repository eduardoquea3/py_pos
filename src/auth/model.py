from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class UserModel(BaseModel):
    id: int
    username: str
    password: str
    first_name: str = Field(alias="first_name")
    last_name: str = Field(alias="last_name")
