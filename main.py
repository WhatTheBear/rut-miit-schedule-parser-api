import os
from litestar import Litestar, get, post

from src.schemes import RegisterData
from src.database import DataBase

import uvicorn
from dotenv import load_dotenv

load_dotenv()

db = DataBase(os.getenv("DB_CON_STR"))


@get("/")
async def home_page() -> str:
    return "Продам гараж"


@get("/api/get_schedule")
async def get_schedule_endpoint(group: int) -> dict:
    return db.journal.getScheduleById(group)

@post("/api/register")
async def register(data: RegisterData) -> dict:
    status = db.users.register(data.userName, data.login, data.password)
    return status


app = Litestar([home_page, get_schedule_endpoint, register])

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0")
