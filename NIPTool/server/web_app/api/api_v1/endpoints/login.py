from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from NIPTool.schemas.server.login import Token

from NIPTool.server.web_app.api.deps import get_current_active_user, authenticate_user, create_access_token, \
    temp_get_config
from datetime import timedelta

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), config: dict = Depends(temp_get_config)):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/authorization")
def get_authorization(token: Token = Depends(login_for_access_token)):
    if token:
        headers = {'Authorization': f"{token.get('token_type')} {token.get('access_token')}",
                   "accept": "application/json"}
        return Response(headers=headers)


@router.post("/login")
def login(auth: str = Depends(get_authorization)):
    return RedirectResponse('../batches')