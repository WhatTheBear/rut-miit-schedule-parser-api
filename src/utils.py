from dataclasses import dataclass, asdict
import requests
from datetime import datetime as dt

schedule_api_url: str = "https://rut-miit.ru/data-service/data/timetable/v2/group/"


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


class Parser:
    def __init__(self, group: int) -> None:
        self.group: str = str(group)
        pass

    def get_parsed_api_dict(self):
        group_time_table_id: dict = requests.get(
            url=str(schedule_api_url + self.group),
            headers={"User-Agent": "Mozilla/5.0"},
        ).json()

        group_schledule_raw: dict = requests.get(
            url=str(
                schedule_api_url
                + self.group
                + "/"
                + group_time_table_id["timetables"][0]["id"]
            ),
            headers={"User-Agent": "Mozilla/5.0"},
        ).json()
        group_week_events: list = group_schledule_raw["periodicContent"]["events"]
        new_schledule_table: dict = {}
        week_days: list = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for week in range(1, 3):
            new_schledule_table[week]: dict = {}
            for day in week_days:
                new_schledule_table[week][day]: list = []
        for event_number in range(len(group_week_events)):
            event_data: dict = group_week_events[event_number]
            event_start: dt = dt.fromisoformat(event_data["startDatetime"])

            # Создаём экземпляр EventInfo
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
                for n in range(1, 3):
                    new_schledule_table[n][week_days[event_start.weekday()]].append(
                        asdict(event)
                    )
            elif interval == 2:
                period: int = event_data["periodNumber"]
                new_schledule_table[period][week_days[event_start.weekday()]].append(
                    asdict(event)
                )

        return new_schledule_table
