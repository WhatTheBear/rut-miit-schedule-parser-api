# from src.schemes import EventInfo
from datetime import datetime as dt, timedelta, date
from zoneinfo import ZoneInfo as zi


class Formatter:
    def __init__(self):
        pass

    @staticmethod
    def format_schedule_json(schedule_json: dict, groupId: int) -> list:
        schedule_start: date = dt.fromisoformat(
            schedule_json["timetable"]["startDate"]
        ).date()
        schedule_end: date = dt.fromisoformat(
            schedule_json["timetable"]["endDate"]
        ).date()
        group_week_events: list = schedule_json["periodicContent"]["events"]
        tz = zi("Europe/Moscow")

        all_days: dict = {}
        current = schedule_start
        while current <= schedule_end:
            all_days[current.isoformat()] = []
            current += timedelta(days=1)

        for event_data in group_week_events:
            event_start_dt: dt = dt.fromisoformat(event_data["startDatetime"])
            event_end_dt: dt = dt.fromisoformat(event_data["endDatetime"])

            event_start_local = event_start_dt.astimezone(tz)
            event_end_local = event_end_dt.astimezone(tz)

            event = {
                "subject": event_data["name"],
                "type": event_data["typeName"],
                "start": event_start_local.isoformat(),
                "end": event_end_local.isoformat(),
                "slot": event_data["timeSlotName"],
                "audience": event_data["rooms"],
                "groups": event_data["groups"],
                "lecturers": event_data["lecturers"],
            }

            interval = int(event_data["recurrenceRule"]["interval"])
            weekday = event_start_dt.weekday()
            period_number = event_data.get("periodNumber", 1)

            current = schedule_start
            while current <= schedule_end:
                if current.weekday() == weekday:
                    if interval == 1:
                        all_days[current.isoformat()].append(event)
                    elif interval == 2:
                        week_index_from_start = (current - schedule_start).days // 7
                        if (week_index_from_start % 2) == (period_number - 1):
                            all_days[current.isoformat()].append(event)
                current += timedelta(days=1)

        documents = []
        for date_str, lessons in all_days.items():
            date_obj = dt.fromisoformat(date_str).replace(tzinfo=tz)
            documents.append({"groupId": groupId, "date": date_obj, "lessons": lessons})

        return documents

    @staticmethod
    def format_session_json(session_json: dict, groupId: int):
        pass

    @staticmethod
    def format_groups_list(institutes_list: list) -> list:
        new_groups_list: list = []

        for institute in institutes_list:
            institute_name = institute["name"]
            for course in institute["courses"]:
                for specialty in course["specialties"]:
                    for group in specialty["groups"]:
                        new_groups_list.append(
                            {
                                "instituteName": institute_name,
                                "specialtyName": specialty["name"],
                                "groupName": group["name"],
                                "groupId": int(group["id"]),
                            }
                        )
        return new_groups_list
