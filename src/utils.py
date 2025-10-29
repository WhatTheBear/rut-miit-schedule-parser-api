from dataclasses import dataclass, asdict
from typing_extensions import ContextManager
import requests, os
from pymongo import MongoClient
from contextlib import contextmanager
from datetime import datetime as dt

schedule_api_url: str = "https://rut-miit.ru/data-service/data/timetable/v2/group/"


@contextmanager
def get_db_client(connection_string: str):
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        yield client

    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise

    finally:
        client.close()


@dataclass
class EventInfo:
    name: str
    type: str
    start: str
    end: str
    slot: str
    audience: list
    groups: list
    lecturers: list


class ParseUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def update_parsed_schedule_by_id(group: str) -> None:
        group_time_table_id: dict = requests.get(
            url=str(schedule_api_url + group),
            headers={"User-Agent": "Mozilla/5.0"},
        ).json()

        group_schledule_raw: dict = requests.get(
            url=str(
                schedule_api_url
                + group
                + "/"
                + group_time_table_id["timetables"][0]["id"]
            ),
            headers={"User-Agent": "Mozilla/5.0"},
        ).json()

        if not group_schledule_raw["periodicContent"]["events"]:
            raise ValueError("Группа не обнаружена")
        group_week_events: list = group_schledule_raw["periodicContent"]["events"]

        new_schledule_table: dict = {"groupId": group}
        week_days: list = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        weeks: list = ["first_week", "second_week"]

        for week in weeks:
            new_schledule_table[week]: dict = {}

            for day in week_days:
                new_schledule_table[week][day]: list = []

        for event_number in range(len(group_week_events)):
            event_data: dict = group_week_events[event_number]
            event_start: dt = dt.fromisoformat(event_data["startDatetime"])

            event = EventInfo(
                name=event_data["name"],
                type=event_data["typeName"],
                start=event_data["startDatetime"],
                end=event_data["endDatetime"],
                slot=event_data["timeSlotName"],
                audience=event_data["rooms"],
                groups=event_data["groups"],
                lecturers=event_data["lecturers"],
            )

            interval = int(event_data["recurrenceRule"]["interval"])

            if interval == 1:
                for week in weeks:
                    new_schledule_table[week][week_days[event_start.weekday()]].append(
                        asdict(event)
                    )

            elif interval == 2:
                period: int = event_data["periodNumber"]
                new_schledule_table[weeks[period - 1]][
                    week_days[event_start.weekday()]
                ].append(asdict(event))

            with get_db_client(str(os.getenv("DB_CON_STR"))) as client:
                client.journal.timetables.update_one(
                    {"groupId": f"{group}"}, {"$set": new_schledule_table}, upsert=True
                )
