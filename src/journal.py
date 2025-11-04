from pymongo import MongoClient, UpdateOne
from pymongo.errors import ServerSelectionTimeoutError

import requests
from datetime import datetime as dt

from src.formatter import Formatter


class Journal:
    def __init__(self, connection_string, timeout_ms=5000) -> None:
        self.client: MongoClient = MongoClient(
            connection_string,
            serverselectiontimeoutms=timeout_ms,
        )

        try:

            self.client.admin.command("ping")

        except ServerSelectionTimeoutError as e:
            print(f"{e}\n Ошибка подключения к базе данных")

    def _update_groups_list(self) -> None:
        schedule_url: str = "https://rut-miit.ru/data-service/data/timetable/groups-catalog"

        headers = {"User-Agent": "Mozilla/5.0"}
        institutes_list: dict = requests.get(
            url=schedule_url,
            headers=headers,
        ).json()

        groups_list = Formatter.format_groups_list(institutes_list['institutes'])

        operations = [
            UpdateOne(
                {"groupId": group["groupId"]},
                {"$set": group},
                upsert=True
            )
            for group in groups_list
        ]

        if operations:
            self.client.journal.groups.bulk_write(operations)


    def _update_group_schedule(self, groupId: int) -> None:
        schedule_url: str = "https://rut-miit.ru/data-service/data/timetable/v2/group/"
        headers = {"User-Agent": "Mozilla/5.0"}
        group_time_table_id: dict = requests.get(
            url=f"{schedule_url}{groupId}",
            headers=headers,
        ).json()

        if len(group_time_table_id["timetables"]) == 0:
            raise ValueError("Группа не обнаружена")

        schedule_raw: dict = requests.get(
            url=f"{schedule_url}{groupId}/{group_time_table_id['timetables'][0]['id']}",
            headers=headers,
        ).json()

        new_schedule: dict = Formatter.format_schedule_json(schedule_raw, groupId)

        self.client.journal.timetables.update_one(
            {"groupId": groupId}, {"$set": new_schedule}, upsert=True
        )

    def getScheduleById(self, groupId:int) -> dict:
        query = {"groupId": groupId}

        if self.client.journal.timetables.find_one(query) is None:
            self._update_group_schedule(groupId)

        return self.client.journal.timetables.find_one(query)["schedule_table"]

    def getGroupNameById(self, groupId: int) -> str:
        query = {"groupId": groupId}

        return self.client.journal.groups.find_one(query)["groupName"]

    def getGroupIdByName(self, groupName: str) -> str:
        query = {"groupName": groupName}

        return self.client.journal.groups.find_one(query)["groupId"]

    def createUser(self, loginData: dict) -> dict:

        user_id = 0

        latest_user_id = [user for user in self.client.journal.users.find().sort({"userId":-1}).limit(1)]

        if len(latest_user_id) != 0:

            user_id = latest_user_id[0]["userId"] + 1

        user = {
            "userId": user_id,
            "groupName":"", #Выбора группы не будет на этапе регистрации, он будет далее
            "loginData":loginData 
        }
        
        self.client.journal.users.insert_one(user)

    def getUserGroupId(self, userId: int) -> int:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)["groupId"]
    
    def getUserByLogin(self, login: str):
        query = {"loginData.login": login}

        return self.client.journal.users.find_one(query)
    
    def getUserByUserId(self, userId: int) -> dict:
        query = {"userId": userId}

        return self.client.journal.users.find_one(query)

