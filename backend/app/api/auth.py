from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db import get_session
from ..repository.users import UserRepository
from ..core.security import hash_password, verify_password, create_access_token

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    existing = await repo.get_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await repo.create(email=req.email, hashed_password=hash_password(req.password))
    token = create_access_token(user.email)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    user = await repo.get_by_email(req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email)
    return TokenResponse(access_token=token)
