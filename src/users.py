from hashlib import sha256
from uuid_utils import uuid7


class Users:
    def __init__(self, client) -> None:
        self.client = client

    def _hash_password(self, password: str) -> str:
        encoded_password_string = password.encode("utf-8")

        return sha256(encoded_password_string).hexdigest()

    def _generate_auth_token(self) -> str:
        pass

    def getUserGroupId(self, userId: int) -> int:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)["groupId"]

    def getUserByLogin(self, login: str):
        query = {"loginData.login": login}

        return self.client.journal.users.find_one(query)

    def getUserByUserId(self, userId: int) -> dict:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)

    def register(self, userName: str, login: str, password: str) -> dict:
        if self.getUserByLogin(login) is not None:
            return {"status": "err",
                    "name": "Пользователь существует!"}

        login_data: dict = {
            "login": login,
            "password": self._hash_password(password),
        }

        user_id = str(uuid7())

        user: dict = {
            "userId": user_id,
            "userName": userName,
            "groupName": "",  # Выбора группы не будет на этапе регистрации, он будет далее
            "loginData": login_data,
        }

        self.client.journal.users.insert_one(user)
        return {"staus" : "succses"}
