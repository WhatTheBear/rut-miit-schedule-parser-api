import os
from fastapi import FastAPI

from src.journal import Journal
from src.login import Login
from src.schemes import *

from pydantic import BaseModel

import uvicorn
from dotenv import load_dotenv

load_dotenv()

jr = Journal(os.getenv("DB_CON_STR"))
lg = Login(jr)

app = FastAPI()


@app.get("/")
def home_page() -> str:
    return "Продам гараж"


@app.get("/api/get_schedule")
def get_schedule_endpoint(group: int) -> dict:
    return jr.getScheduleById(group)
    # jr._update_groups_list()

@app.post("/api/register")
def register(registerData: RegisterData) -> str:

    status = lg.register(registerData.userName, registerData.login, registerData.password)

    return status



if __name__ == "__main__":
    uvicorn.run(app=app)
    # ParseUtils.update_parsed_schedule_by_id("189103")
