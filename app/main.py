from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.deps import get_current_user
from app.models import User


from sqlalchemy.future import select

from app.database import get_db
from app.models.models import Token, BaseUser, UpdateUser, UserRead, BaseAddress, Address
from app.security import verify_password, create_access_token, get_password_hash

app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 10


@app.get("/users", response_model=list[UserRead])
async def read_items(
        db: AsyncSession = Depends(get_db),
):
    result = await db.exec(select(User))
    return result.unique().scalars().all()

@app.get("/users/{user_id}", response_model=UserRead)
async def read_items(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
):
    result = await db.exec(select(User).where(User.id == user_id))
    return result.scalars().one_or_none()



@app.post("/users", response_model=User)
async def create_user(
        user: BaseUser, db: AsyncSession = Depends(get_db),
        get_current_user: User = Depends(get_current_user)
):
    if not get_current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db_obj = User.model_validate(user)
    db_obj.hashed_password = get_password_hash("ciao")
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@app.patch("/users/{item_id}", response_model=User)
async def update_user(
        item_id: UUID,
        user: UpdateUser,
        db: AsyncSession = Depends(get_db),
        get_current_user: User = Depends(get_current_user)
):
    update_obj = user.model_dump(exclude_unset=True)
    obj_to_update = await db.get(User, item_id)
    if not obj_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    if obj_to_update.id != get_current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden resource")
    obj_to_update.sqlmodel_update(update_obj)
    db.add(obj_to_update)
    await db.commit()
    await db.refresh(obj_to_update)
    return obj_to_update

@app.post("/address/{user_id}", response_model=UserRead)
async def assign_address(
        user_id: UUID, address: BaseAddress,
        db: AsyncSession = Depends(get_db),
        get_current_user: User = Depends(get_current_user)
):
    obj_to_update = await db.get(User, user_id)
    if not obj_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    if obj_to_update.id != get_current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden resource")

    obj_to_update.addresses.append(Address.model_validate(address))
    db.add(obj_to_update)
    await db.commit()
    await db.refresh(obj_to_update)
    return obj_to_update

@app.delete("/users/{item_id}", response_model=bool)
async def delete_user(
        item_id: UUID,
        db: AsyncSession = Depends(get_db),
        get_current_user: User = Depends(get_current_user)
):
    if not get_current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    usr_to_delete = await db.get(User, item_id)
    if usr_to_delete:
        await db.delete(usr_to_delete)
        await db.commit()
        return True
    return False



@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> Token:

    result = await db.exec(select(User).where(User.email == form_data.username))
    user: User = result.unique().scalar_one_or_none()

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
        data=jsonable_encoder({"id": user.id, "admin": user.is_admin}), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/")
def read_root():
    return {"message": "Hello Papasito"}
