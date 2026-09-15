from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.user import UserProfileSchema

class LoginPayload(BaseModel):
    email: str
    password: str
    remember: Optional[bool] = False

class PhoneLoginPayload(BaseModel):
    phone: str
    otp: str

class SendOtpPayload(BaseModel):
    phone: str

class RegisterPayload(BaseModel):
    name: str
    username: str
    email: str
    password: str

class ForgotPasswordPayload(BaseModel):
    email: str

class ResetPasswordPayload(BaseModel):
    token: str
    password: str

class AuthResponse(BaseModel):
    accessToken: str = Field(alias="access_token")
    user: UserProfileSchema

    class Config:
        populate_by_name = True
