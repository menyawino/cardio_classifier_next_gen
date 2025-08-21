from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.db import get_session
from ..repository.users import UserRepository
from ..config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"


def get_secret():
    return get_settings().jwt_secret


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: str, expires_minutes: int = 60 * 24) -> str:
    to_encode = {"sub": subject, "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(to_encode, get_secret(), algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")  # type: ignore
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    repo = UserRepository(session)
    user = await repo.get_by_email(email)
    if not user:
        raise credentials_exception
    return user
