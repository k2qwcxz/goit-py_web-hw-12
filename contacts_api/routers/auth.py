from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from contacts_api.database import get_db
from contacts_api.schemas import UserCreate, UserLogin, UserResponse, TokenSchema
from contacts_api.crud import UserCRUD
from contacts_api.auth import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = await UserCRUD.get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    new_user = await UserCRUD.create_user(user, db)
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = await UserCRUD.get_user_by_email(form_data.username, db)
    if not db_user or not auth_service.verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth_service.create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires.total_seconds()
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenSchema)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    email = await auth_service.decode_refresh_token(refresh_token)
    user = await UserCRUD.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth_service.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires.total_seconds()
    )
    new_refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }