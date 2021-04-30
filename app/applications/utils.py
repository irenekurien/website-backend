"""
Application Utils
"""
from sqlalchemy.orm import Session
from app.users import crud as user_crud
from app.users.roles import Roles
from app.users.schemas import UserCreate


def create_user_from_application(database: Session, application):
    """Create user after application has been approved"""
    user = UserCreate(
        role=Roles.USER,
        # Ensure this password is >= 8 characters
        password="password",
        email=application.email,
        name=application.name
    )

    user_crud.create_user(database=database, user=user)