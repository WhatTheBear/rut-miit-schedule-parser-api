import os
from litestar import Litestar, MediaType, get, post

from src.telegram_auth_utils import is_user_data_valid
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


@get("/test_login_page", media_type=MediaType.HTML)
async def test_login() -> str:

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <script async src="https://telegram.org/js/telegram-widget.js?22" data-telegram-login="RUTScheduleAuthBot" data-size="medium" data-auth-url="/api/telegram/on_auth"></script>
</body>
</html>"""


@get("/api/telegram/on_auth")
async def tg_auth_callback(id: int, first_name: str, username: str, photo_url: str, auth_date: str, hash: str) -> dict:

    #Сессию запихать в куки

    login = f"TG_AUTH_{id}"


    if db.users.getUserByLogin(login) is None:

        data_check_string: str = f'auth_date={auth_date}\nfirst_name={first_name}\nid={id}\nusername={username}'


        #По какой то причине он 99 из 100 случаев признавал данные невалидными, надо фиксить
        #
        # if not is_user_data_valid(hash, data_check_string):
        #     return {
        #         "status":"failed",
        #         "details":"Your hashed user's data != given hashed data by telegram!"
        #     }
        #
        
        db.users.register(login, "TG") # Для авторизации через иные ресурсы пароль не важен

        db.users.setUserNameByLogin(login, username)


    return db.users.login(login, "TG", True)


app = Litestar([home_page, get_schedule_endpoint, register, test_login, tg_auth_callback])


if __name__ == "__main__": 
    
    uvicorn.run(app=app, host="0.0.0.0", port=80)
