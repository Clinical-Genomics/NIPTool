from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from starlette.responses import RedirectResponse

from NIPTool.config import get_nipt_adapter
from NIPTool.crud import find
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.exeptions import CredentialsError

from NIPTool.models.database import User
from passlib.context import CryptContext
from NIPTool.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
) -> User:
    """Decoding user from token stored in cookies."""

    try:
        payload = jwt.decode(
            request.cookies.get("token"),
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsError(message="Could not validate credentials")
    except JWTError:
        raise CredentialsError(message="Could not validate credentials")
    user: User = find.user(adapter=adapter, user_name=username)
    if not user:
        raise CredentialsError(message="User not found in database.")
    return user


def return_500_if_errors(f):
    print("haha")

    @wraps(f)
    def wrapper(*args, **kwargs):
        print("hehe")
        try:
            return f(*args, **kwargs)
        except:
            response = {"status_code": 500, "status": "Internal Server Error"}
            return RedirectResponse("../")

    return wrapper


def redirect_unauthorized(func):
    print("hoho")

    def inner_function(*args, **kwargs):
        print("hihi")
        try:
            func(*args, **kwargs)
        except:
            return RedirectResponse("../")

    return inner_function


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    adapter: NiptAdapter = get_nipt_adapter()
    user: User = find.user(adapter=adapter, user_name=username)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, form_data: OAuth2PasswordRequestForm, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = {"sub": username, "scopes": form_data.scopes}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
