import requests

from src.formatter import Formatter

class Journal:
    def __init__(self, client) -> None:
        self.client = client

    def _update_groups_list(self) -> None:
        schedule_url: str = (
            "https://rut-miit.ru/data-service/data/timetable/groups-catalog"
        )

        headers = {"User-Agent": "Mozilla/5.0"}
        institutes_list: dict = requests.get(
            url=schedule_url,
            headers=headers,
        ).json()

        groups_list = Formatter.format_groups_list(institutes_list["institutes"])
        for group in groups_list:
            self.client.journal.groups.update_one(
            {"groupId": group["groupId"]}, {"$set": groups_list}, upsert=True
        )


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

    def getScheduleById(self, groupId: int) -> dict:
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

    def setHomework(self, userId:int, homework: dict):
        pass

