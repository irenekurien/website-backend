"""
Dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.users.schemas import TokenData, UserInDB
from app.database.config_db import SessionLocal
from app.database.config_test_db import TESTING_SESSION_LOCAL
from app.users.crud import get_user_by_email
from app.settings import SECRET_KEY, JWT_HASH_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    """
    Get the current db session
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def get_test_db():
    """The test db dependency"""
    database = TESTING_SESSION_LOCAL()
    try:
        yield database
    finally:
        database.close()


def get_current_user(database: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    :return: schemas.UserInDB
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as jwt_exception:
        raise credentials_exception from jwt_exception
    user = get_user_by_email(database=database, email=token_data.email)
    if user is None:
        raise credentials_exception
    return UserInDB(**user.__dict__)
