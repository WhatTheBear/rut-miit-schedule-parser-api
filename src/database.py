from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from src.journal import Journal
from src.users import Users

class DataBase:

    def __init__(self, connection_string, timeout_ms=5000) -> None:
        self.client: MongoClient = MongoClient(
            connection_string,
            serverselectiontimeoutms=timeout_ms,
        )

        try:
            self.client.admin.command("ping")

        except ServerSelectionTimeoutError as e:
            print(f"{e}\n Ошибка подключения к базе данных")

        self.journal: Journal = Journal(self.client)
        self.users: Users = Users(self.client)