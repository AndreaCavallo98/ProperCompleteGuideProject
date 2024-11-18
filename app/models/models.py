import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel
from sqlalchemy import Column, Integer
from sqlmodel import SQLModel, Relationship, Field
from uuid import uuid4, UUID


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class BaseUser(SQLModel):
    name: str
    email: EmailStr
    age: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))


class User(BaseUUIDModel, BaseUser, table=True):
    hashed_password: str | None = Field(default=None, nullable=True, index=True)
    addresses: list["Address"] = Relationship(back_populates="user")


class Address(BaseUUIDModel, table=True):
    name: str
    number: int
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="addresses")


class Token(BaseModel):
    access_token: str
    token_type: str
