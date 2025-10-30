from dataclasses import dataclass, asdict
from datetime import datetime as dt


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
    def __init__(self):
        pass

    @staticmethod
    def parse_schedule_json(schedule_json: str, groupId: str) -> dict:
        group_week_events: list = schedule_json["periodicContent"]["events"]

        schedule_table: dict = {"groupId": groupId}
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

        for w in weeks:
            schedule_table[w] = {d: [] for d in week_days}

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
                    schedule_table[week][week_days[event_start.weekday()]].append(
                        asdict(event)
                    )

            elif interval == 2:
                period: int = event_data["periodNumber"]
                schedule_table[weeks[period - 1]][
                    week_days[event_start.weekday()]
                ].append(asdict(event))

        return schedule_table
    # def parse_groups()
