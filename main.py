from fastapi import FastAPI
import uvicorn
import os
from utils.schledule_parser import Parser

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get('/')
def root():
	return "Продам гараж"

@app.get('/api/get_schedule')
def get_schedule(group:str):
	test = Parser(group)
	return test.get_schledule_json()


if __name__ == "__main__":
	uvicorn.run(
				app=app, 
				port=int(os.getenv('PORT')),
				host=str(os.getenv('IP'))
				)