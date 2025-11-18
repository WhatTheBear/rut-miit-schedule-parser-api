from hashlib import sha256
from uuid_utils import uuid7
from datetime import datetime as dt, timedelta as td


class Users:
    def __init__(self, client) -> None:
        self.client = client

    def _remove_expired_tokens(self) -> None:
        from datetime import datetime

        self.client.journal.users.update_many(
            {"loginData.auth_tokens.endDate": {"$lt": datetime.now()}},
            {"$pull": {"loginData.auth_tokens": {"endDate": {"$lt": datetime.now()}}}},
        )

    def _hash(self, string: str) -> str:
        encoded_string = string.encode("utf-8")

        return sha256(encoded_string).hexdigest()

    def _generate_auth_token(self, login: str) -> str:
        return self._hash(login + str(uuid7()))

    def getUserGroupId(self, userId: int) -> int:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)["groupId"]

    def getUserByLogin(self, login: str):
        query = {"loginData.login": login}

        return self.client.journal.users.find_one(query)

    def getUserByUserId(self, userId: int) -> dict:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)

    def register(self, login: str, password: str) -> dict:
        if self.getUserByLogin(login) is not None:
            return {"status": "err", "name": "Пользователь существует!"}

        login_data: dict = {
            "login": login,
            "password": self._hash(password),
            "auth_tokens": [],
        }

        user_id = str(uuid7())

        user: dict = {
            "userId": user_id,
            "userName": "",  # Потом задать
            "groupName": "",  # Выбора группы не будет на этапе регистрации, он будет далее
            "loginData": login_data,
        }

        self.client.journal.users.insert_one(user)
        return {"status": "success"}

    def login(self, login: str, password: str) -> dict:
        user = self.getUserByLogin(login)
        if user is None:
            return {"status": "err", "name": "Пользователь не существует!"}
        if not user["loginData"]["password"] == self._hash(password):
            return {"status": "err", "name": "Неверный пароль!"}
        auth_token = self._generate_auth_token

        self.client.journal.users.update_one(
            {"_id": user["_id"]},
            {
                "$push": {
                    "loginData.auth_tokens": {
                        "endDate": dt.now() + td(days=20),
                        "token": auth_token,
                    }
                }
            },
        )

        return {"status": "success", "auth_token": auth_token}

    def auth_token_validator(self, auth_token: str) -> dict:
        self._remove_expired_tokens()
        user = self.client.journal.users.find_one(
            {"loginData.auth_tokens.token": auth_token}
        )

        if user is None:
            return {"status": "err", "name": "Токен не существует!"}

        for token in user["loginData"]["auth_tokens"]:
            if not token["token"] == auth_token:
                continue

            return {"status": "success", "user": user}
        return {"status": "err", "name": "Как ты это сделал..."}

    def setUserNameByLogin(self, login: str, new_name: str):
        user = self.getUserByLogin(login)
        self.client.journal.users.update_one(
            {"_id": user["_id"]}, {"$set": {"userName": new_name}}
        )
        return {"status": "success", "user": self.getUserByLogin(login)}
