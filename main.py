import os
from fastapi import FastAPI
from src.journal import Journal
# import uvicorn
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()


@app.get("/")
def home_page() -> dict[str, str]:
    return "Продам гараж"


# @app.get("/api/get_schedule")
# def get_schedule_endpoint(group: str):
#     return DBUtils.get_parsed_api_dict(group)


if __name__ == "__main__":
    # uvicorn.run(app=app)
    # ParseUtils.update_parsed_schedule_by_id("189103")
    jr = Journal(os.getenv("DB_CON_STR"))
    jr._update_group_schedule("202181")
