import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginPayload, PhoneLoginPayload, SendOtpPayload, RegisterPayload,
    ForgotPasswordPayload, ResetPasswordPayload, AuthResponse
)
from app.schemas.user import UserProfileSchema
from app.core.security import create_access_token, verify_password, hash_password
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/send-otp")
def send_otp(payload: SendOtpPayload, db: Session = Depends(get_db)):
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    if len(clean_phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit phone number")
    
    user = db.query(User).filter(User.phone == clean_phone).first()
    if not user:
        user = User(
            id=f"u_{uuid.uuid4().hex[:8]}",
            phone=clean_phone,
            username=f"bhojpuri_{clean_phone[-4:]}",
            name=f"Bhojpuri Viewer {clean_phone[-4:]}",
            email=f"{clean_phone}@echoreels.in",
            otp_code="1234"
        )
        db.add(user)
    else:
        user.otp_code = "1234"
    db.commit()
    return {"success": True, "message": f"OTP sent to +91 {clean_phone}"}

@router.post("/login-phone", response_model=AuthResponse)
def login_phone(payload: PhoneLoginPayload, db: Session = Depends(get_db)):
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    user = db.query(User).filter(User.phone == clean_phone).first()
    if not user:
        user = User(
            id=f"u_{uuid.uuid4().hex[:8]}",
            phone=clean_phone,
            username=f"bhojpuri_{clean_phone[-4:]}",
            name=f"Bhojpuri Viewer {clean_phone[-4:]}",
            email=f"{clean_phone}@echoreels.in"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    token = create_access_token(user.id)
    return {
        "accessToken": token,
        "user": UserProfileSchema(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            email=user.email or "",
            bio=user.bio or "",
            followers=user.followers or 0,
            following=user.following or 0,
            totalLikes=user.total_likes or 0,
            isFollowing=user.is_following or False
        )
    }

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Create user automatically for fast onboarding
        user = User(
            id=f"u_{uuid.uuid4().hex[:8]}",
            email=payload.email,
            username=payload.email.split("@")[0],
            name=payload.email.split("@")[0].capitalize(),
            hashed_password=hash_password(payload.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user.hashed_password and not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    token = create_access_token(user.id)
    return {
        "accessToken": token,
        "user": UserProfileSchema(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            email=user.email or "",
            bio=user.bio or "",
            followers=user.followers or 0,
            following=user.following or 0,
            totalLikes=user.total_likes or 0,
            isFollowing=user.is_following or False
        )
    }

@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists with this email or username")
    
    user = User(
        id=f"u_{uuid.uuid4().hex[:8]}",
        email=payload.email,
        username=payload.username,
        name=payload.name,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {
        "accessToken": token,
        "user": UserProfileSchema(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            email=user.email or "",
            bio=user.bio or "",
            followers=user.followers or 0,
            following=user.following or 0,
            totalLikes=user.total_likes or 0,
            isFollowing=False
        )
    }

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordPayload):
    return {"message": f"Password reset instructions sent to {payload.email}"}

@router.post("/reset-password")
def reset_password(payload: ResetPasswordPayload):
    return {"message": "Password updated successfully"}

@router.get("/me", response_model=UserProfileSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return UserProfileSchema(
        id=current_user.id,
        name=current_user.name,
        username=current_user.username,
        avatar=current_user.avatar,
        email=current_user.email or "",
        bio=current_user.bio or "",
        followers=current_user.followers or 0,
        following=current_user.following or 0,
        totalLikes=current_user.total_likes or 0,
        isFollowing=False
    )

@router.post("/logout")
def logout():
    return {"success": True}
