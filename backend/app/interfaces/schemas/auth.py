from pydantic import BaseModel, Field, constr


CedulaStr = constr(pattern=r"^[0-9]{6,12}$")
NitStr = constr(pattern=r"^[0-9]{9,15}(-[0-9])?$")


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    cedula: CedulaStr
    enterprise_name: str = Field(min_length=2, max_length=160)
    nit: NitStr
    password: str = Field(min_length=8, max_length=64)


class LoginRequest(BaseModel):
    cedula: CedulaStr
    password: str = Field(min_length=8, max_length=64)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    cedula: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    cedula: str
    enterprise_id: int
