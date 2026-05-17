from datetime import datetime, timedelta, timezone
from typing import Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "replace-with-a-secure-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
bearer_scheme = HTTPBearer()


class UserRecord(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    hashed_password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str


# Replace this with your persistent user store (SQLAlchemy/ORM layer).
USERS_BY_EMAIL: Dict[str, UserRecord] = {}
USERS_BY_ID: Dict[str, UserRecord] = {}


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: Literal["access", "refresh"], expires_delta: timedelta) -> str:
    expire_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _create_token_pair(user_id: str) -> TokenPairResponse:
    access_token = _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    payload = _decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    user_id: Optional[str] = payload.get("sub")
    if not user_id or user_id not in USERS_BY_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user_record = USERS_BY_ID[user_id]
    current_user = CurrentUser(
        id=user_record.id,
        email=user_record.email,
        full_name=user_record.full_name,
        role=user_record.role,
    )
    request.state.user = current_user
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = set(allowed_roles)

    async def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return current_user


@router.post("/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> TokenPairResponse:
    if payload.email in USERS_BY_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = UserRecord(
        id=str(uuid4()),
        email=payload.email,
        full_name=payload.full_name,
        role="learner",
        hashed_password=_hash_password(payload.password),
    )
    USERS_BY_EMAIL[user.email] = user
    USERS_BY_ID[user.id] = user

    return _create_token_pair(user.id)


@router.post("/login", response_model=TokenPairResponse)
async def login(payload: LoginRequest) -> TokenPairResponse:
    user = USERS_BY_EMAIL.get(payload.email)
    if not user or not _verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _create_token_pair(user.id)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest) -> AccessTokenResponse:
    token_payload = _decode_token(payload.refresh_token)
    if token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    user_id = token_payload.get("sub")
    if not user_id or user_id not in USERS_BY_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return AccessTokenResponse(access_token=new_access_token)


