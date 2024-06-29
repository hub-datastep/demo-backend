from datetime import datetime, timedelta
from typing import Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from infra.database import get_session
from repository import user_repository
from scheme.auth.token_scheme import TokenData, Token
from scheme.user.user_scheme import User
from util.hashing import pwd_context

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign_in")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, username: str, password: str) -> User | bool:
    user_db = user_repository.get_user_by_username(session, username)
    if not verify_password(password, user_db.password):
        return False
    return user_db


def sign_in(session: Session, username: str, password: str) -> Token:
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return get_token(TokenData(user_id=user.id))


def get_token(token_data: TokenData) -> Token:
    access_token = create_token({"sub": str(token_data.user_id)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    # refresh_token = create_token({"sub": str(token_data.user_id)}, REFRESH_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=access_token,
        # refresh_token=refresh_token,
        token_type="bearer"
    )


# def get_refreshed_token(refresh_token) -> Token:
#     token_data = jwt_decode(refresh_token)
#     return get_token(token_data)


def create_token(data: dict, token_expires_mins: int) -> str:
    token_expires = timedelta(minutes=token_expires_mins)
    to_encode = data.copy()
    if token_expires:
        expire = datetime.utcnow() + token_expires
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def jwt_decode(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
        return token_data
    except JWTError:
        raise credentials_exception


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> Type[User]:
    token_data = jwt_decode(token)
    user_db = user_repository.get_user_by_id(session, token_data.user_id)
    return user_db
