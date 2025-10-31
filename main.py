import os
from fastapi import FastAPI
from src.journal import Journal
import uvicorn
from dotenv import load_dotenv

load_dotenv()

jr = Journal(os.getenv("DB_CON_STR"))

app = FastAPI()


@app.get("/")
def home_page() -> str:
    return "Продам гараж"


@app.get("/api/get_schedule")
def get_schedule_endpoint(group: int) -> dict:
    return jr.getScheduleById(group)
    # jr._update_groups_list()


if __name__ == "__main__":
    uvicorn.run(app=app)
    # ParseUtils.update_parsed_schedule_by_id("189103")
