from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

import requests

from src.utils import Parser

# DB_CONNECTION_FAILED = 0
# DB_CONNECTION_SUCCEED = 1
# DB_DATA_GET_FAILED = 2
# DB_DATA_GET_SUCCEED = 3
# DB_DATA_WRITE_FAILED = 4
# DB_DATA_WRITE_SUCCEED = 5
# DB_DATA_DELETE_FAILED = 6
# DB_DATA_DELETE_SUCCEED = 7


class Journal:
    def __init__(self, connection_string, timeout_ms=5000) -> None:
        self.client: MongoClient = MongoClient(
            connection_string,
            serverselectiontimeoutms=timeout_ms,
        )

        try:
            self.client.admin.command("ping")

        except ServerSelectionTimeoutError as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def _update_groups_list(self):
        pass

    def _update_group_schedule(self, groupId: int):
        schedule_url: str = "https://rut-miit.ru/data-service/data/timetable/v2/group/"
        headers = {"User-Agent": "Mozilla/5.0"}
        group_time_table_id: dict = requests.get(
            url=f"{schedule_url}{groupId}",
            headers=headers,
        ).json()

        if len(group_time_table_id["timetables"]) == 0:
            raise ValueError("Группа не обнаружена")

        schedule_raw: dict = requests.get(
            url=f"{schedule_url}{groupId}/{group_time_table_id['timetables'][-1]['id']}",
            headers=headers,
        ).json()

        new_schedule: dict = Parser.parse_schedule_json(schedule_raw, groupId)

        self.client.journal.timetables.update_one(
            {"groupId": f"{groupId}"}, {"$set": new_schedule}, upsert=True
        )

    # def connect_db(self) -> int:

    #     try:
    #         self.client = MongoClient(self.connection_string)
    #         return DB_CONNECTION_SUCCEED

    #     except ServerSelectionTimeoutError:
    #         return DB_CONNECTION_FAILED

    def getGroupNameById(self, groupId: int) -> str:
        query = {"groupId": groupId}

        return self.client.journal.groups.find_one(query)["groupName"]

    def getGroupIdByName(self, groupName: str) -> str:
        query = {"groupName": groupName}

        return self.client.journal.groups.find_one(query)["groupId"]

    def getUserGroupId(self, userId: int) -> int:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)["groupId"]
