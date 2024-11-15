from fastapi import FastAPI

from app.models import User

app = FastAPI()

user1 = User(id=1, name="Andrea", surname="Cavallo")
user2 = User(id=2, name="Mardsdaianna", surname="Cavallo")
users: list[User] = []
users.append(user1)
users.append(user2)


@app.get("/users", response_model=list[User])
async def read_items():
    return users

@app.get("/")
def read_root():
    return {"message": "hbhbhjbh"}