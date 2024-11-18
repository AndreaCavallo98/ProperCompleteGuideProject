from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.deps import get_current_user
from app.models import User


from sqlalchemy.future import select

from app.database import get_db
from app.models.models import Token, BaseUser
from app.security import verify_password, create_access_token, get_password_hash

app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 1


@app.get("/users", response_model=list[User], dependencies=[Depends(get_current_user)])
async def read_items(
        db: AsyncSession = Depends(get_db),
):
    result = await db.exec(select(User))
    return result.scalars().all()


# Potrei verificare se ha i permessi da admin
@app.post("/users", response_model=User, dependencies=[Depends(get_current_user)])
async def create_user(user: BaseUser, db: AsyncSession = Depends(get_db)):
    db_obj = User.model_validate(user)
    db_obj.hashed_password = get_password_hash("ciao")
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@app.get("/")
def read_root():
    return {"message": "Hello Papasito"}




@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> Token:

    result = await db.exec(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=jsonable_encoder({"id": user.id}), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")