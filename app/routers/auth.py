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
from app.services.otp_service import otp_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/send-otp")
def send_otp(payload: SendOtpPayload, db: Session = Depends(get_db)):
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    if len(clean_phone) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit phone number")
    
    # Send OTP via MSG91
    result = otp_service.send_otp(clean_phone)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to send OTP"))

    # Track / create user record if doesn't exist
    user = db.query(User).filter(User.phone == clean_phone).first()
    if not user:
        user = User(
            id=f"u_{uuid.uuid4().hex[:8]}",
            phone=clean_phone,
            username=f"bhojpuri_{clean_phone[-4:]}",
            name=f"Viewer +91 {clean_phone[:5]} {clean_phone[5:]}",
            email=f"{clean_phone}@echoreels.in"
        )
        db.add(user)
        db.commit()

    return {"success": True, "message": result.get("message", f"OTP sent to +91 {clean_phone}")}

@router.post("/login-phone", response_model=AuthResponse)
def login_phone(payload: PhoneLoginPayload, db: Session = Depends(get_db)):
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    if len(clean_phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    if not payload.otp:
        raise HTTPException(status_code=400, detail="OTP is required")

    # Verify OTP via MSG91
    is_valid, msg = otp_service.verify_otp(clean_phone, payload.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg or "Invalid or expired OTP")

    user = db.query(User).filter(User.phone == clean_phone).first()
    if not user:
        user = User(
            id=f"u_{uuid.uuid4().hex[:8]}",
            phone=clean_phone,
            username=f"bhojpuri_{clean_phone[-4:]}",
            name=f"Viewer +91 {clean_phone[:5]} {clean_phone[5:]}",
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
            phone=user.phone or clean_phone,
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
            phone=user.phone or "",
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
            phone=user.phone or "",
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
        phone=current_user.phone or "",
        bio=current_user.bio or "",
        followers=current_user.followers or 0,
        following=current_user.following or 0,
        totalLikes=current_user.total_likes or 0,
        isFollowing=False
    )

@router.post("/logout")
def logout():
    return {"success": True}
