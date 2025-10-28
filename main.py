from fastapi import FastAPI
from src.utils import Parser
import uvicorn


app = FastAPI()


@app.get("/")
def home_page() -> dict[str, str]:
    return {"hello": "world!"}


@app.get("/api/get_schedule")
def get_schedule_endpoint(group: str):
    return Parser.get_parsed_api_dict(group)


if __name__ == "__main__":
    uvicorn.run(app=app)
