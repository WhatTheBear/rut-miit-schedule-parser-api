import requests
from pymongo import UpdateOne
from datetime import datetime as dt, timedelta as td
from zoneinfo import ZoneInfo as zi

from src.formatter import Formatter


class Journal:
    def __init__(self, client) -> None:
        self.client = client

    def _update_groups(self) -> None:
        schedule_url: str = (
            "https://rut-miit.ru/data-service/data/timetable/groups-catalog"
        )

        headers = {"User-Agent": "Mozilla/5.0"}
        institutes_list: dict = requests.get(
            url=schedule_url,
            headers=headers,
        ).json()

        groups_list = Formatter.format_groups_list(institutes_list["institutes"])
        operations = [
            UpdateOne({"groupId": group["groupId"]}, {"$set": group}, upsert=True)
            for group in groups_list
        ]

        if operations:
            self.client.journal.groups.bulk_write(operations)

    def _update_group_schedule(self, groupId: int) -> None:
        schedule_url: str = "https://rut-miit.ru/data-service/data/timetable/v2/group/"
        headers = {"User-Agent": "Mozilla/5.0"}

        response1 = requests.get(url=f"{schedule_url}{groupId}", headers=headers)
        response1.raise_for_status()
        group_time_table_id = response1.json()

        if not group_time_table_id.get("timetables"):
            raise ValueError("Группа не обнаружена")

        timetable_id = group_time_table_id["timetables"][0]["id"]
        response2 = requests.get(
            url=f"{schedule_url}{groupId}/{timetable_id}", headers=headers
        )
        response2.raise_for_status()
        schedule_raw = response2.json()

        new_schedule_docs = Formatter.format_schedule_json(schedule_raw, groupId)

        self.client.journal.schedule.delete_many({"groupId": groupId})

        if new_schedule_docs:
            self.client.journal.schedule.insert_many(new_schedule_docs)

        self.client.journal.schedule.create_index([("groupId", 1), ("date", 1)])

    def getScheduleById(self, groupId: int) -> dict:
        query = {
            "groupId": groupId,
        }
        cursor = self.client.journal.schedule.find(query).sort("date", 1)
        if cursor is None:
            self._update_group_schedule(groupId)
        cursor = self.client.journal.schedule.find(query).sort("date", 1)
        return list(cursor)

    def getGroupNameById(self, groupId: int) -> str:
        query = {"groupId": groupId}

        return self.client.journal.groups.find_one(query)["groupName"]

    def getGroupIdByName(self, groupName: str) -> str:
        query = {"groupName": groupName}

        return self.client.journal.groups.find_one(query)["groupId"]

    def setHomeworkByGroupAndDate(
        self, userId: str, groupId: int, homework: str, date: dt
    ) -> dict:
        date_str = date.isoformat()

        schedule_doc = self.client.journal.schedule.find_one(
            {"groupId": groupId, "lessons.start": date_str}
        )

        if not schedule_doc:
            return {"status": "err", "name": "Расписание не найдено"}

        updated_lessons = []
        homework_added = False
        for lesson in schedule_doc["lessons"]:
            if lesson["start"] == date_str:
                lesson["homework"] = homework
                lesson["homeworkUserId"] = userId
                homework_added = True
            updated_lessons.append(lesson)

        if not homework_added:
            return {"status": "err", "name": "Занятие не найдено"}

        self.client.journal.schedule.update_one(
            {"_id": schedule_doc["_id"]}, {"$set": {"lessons": updated_lessons}}
        )

        return {"status": "success"}

    def getWeekScheduleByDate(self, start_date: dt, groupId: int) -> list:
        tz = zi("Europe/Moscow")
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=tz)
        start_norm = start_date.astimezone(tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_norm = start_norm + td(days=7)

        query = {"groupId": groupId, "date": {"$gte": start_norm, "$lt": end_norm}}
        cursor = self.client.journal.schedule.find(query).sort("date", 1)
        return list(cursor)
