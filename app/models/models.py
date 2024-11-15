from typing import Optional
from sqlmodel import SQLModel, Relationship, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    surname: str
    addresses: list["Address"] = Relationship(back_populates="user")


class Address(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    number: int
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="addresses")
