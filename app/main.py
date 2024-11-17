from fastapi import FastAPI, Depends

from app.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db

app = FastAPI()


@app.get("/users", response_model=list[User])
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@app.post("/users", response_model=User)
async def create_user(user: User, db: AsyncSession = Depends(get_db)):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@app.get("/")
def read_root():
    return {"message": "hbhbhjbh"}