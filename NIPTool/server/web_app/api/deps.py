from NIPTool.adapter.plugin import NiptAdapter
from pymongo import MongoClient
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from NIPTool.schemas.server.login import User, UserInDB, TokenData
from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt


def temp_get_config():
    return {'DB_URI': 'mongodb://localhost:27030', 'DB_NAME': 'nipt-stage',
            "SECRET_KEY": "97f30d198c86a604f12c22c74077a22cc223009f78fbb8de2065c26cca68e9a5",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30
            }


def get_nipt_adapter():
    config = temp_get_config()
    client = MongoClient(config['DB_URI'])
    return NiptAdapter(client, db_name=config['DB_NAME'])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(token: str = Depends(oauth2_scheme), adapter: NiptAdapter = Depends(get_nipt_adapter),
                     config: dict = Depends(temp_get_config)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.get("SECRET_KEY"), algorithms=[config.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = adapter.user(token_data.username)
    if not user:
        raise credentials_exception
    return User(**user)


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    adapter = get_nipt_adapter()
    user_dict = adapter.user(username)
    if not user_dict:
        return False
    user = UserInDB(**user_dict)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    config: dict = temp_get_config()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.get("SECRET_KEY"), algorithm=config.get("ALGORITHM"))
    return encoded_jwt