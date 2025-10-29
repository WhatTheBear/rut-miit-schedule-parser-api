from fastapi import FastAPI
from src.utils import ParseUtils
import uvicorn
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
    uvicorn.run(app=app)
    # ParseUtils.update_parsed_schedule_by_id("189103")
