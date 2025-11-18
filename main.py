import os
from litestar import Litestar, get, post

from src.schemes import RegisterData
from src.database import DataBase

from datetime import datetime as dt
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
    db.journal.getScheduleById(189103)
    print(db.journal.getWeekScheduleByDate(dt.now(), 189103))
    db.journal.setHomework(
        4, 189103, "test2", dt.fromisoformat("2025-11-25T08:30:00+03:00")
    )
    uvicorn.run(app=app, host="0.0.0.0")
