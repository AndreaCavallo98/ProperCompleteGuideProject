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
    is_admin: bool = Field(default=False, sa_column=Column(server_default="false", nullable=False))
    hashed_password: str | None = Field(default=None, nullable=True, index=True)
    addresses: list["Address"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})


class UpdateUser(SQLModel):
    name: str | None = None
    email: EmailStr | None = None
    age: int | None = None


class UserRead(BaseUser):
    id: UUID
    addresses: list["AddressRead"]


class BaseAddress(SQLModel):
    name: str
    number: int


class Address(BaseUUIDModel,BaseAddress, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="addresses", sa_relationship_kwargs={"lazy": "joined"})


class AddressRead(BaseAddress):
    id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str
