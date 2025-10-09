import requests
import json
from datetime import datetime as dt

schledule_api_url = "https://rut-miit.ru/data-service/data/timetable/v2/group/"

class Parser:
	def __init__(self, group):
		self.group = group
		pass

	def get_schledule_json(self):

		group_time_table_id = requests.get(
											url=str(schledule_api_url+self.group), 
											headers = {'User-Agent': 'Mozilla/5.0'}
											).json()
		
		group_schledule_raw = requests.get(
											url=str(schledule_api_url+self.group+"/"+group_time_table_id["timetables"][0]["id"]),
											headers = {'User-Agent': 'Mozilla/5.0'}
											).json()
		
		group_week_events = group_schledule_raw["periodicContent"]["events"]

		new_schledule_table:dict = {}
		week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
		for week in range(1, 3):
			new_schledule_table[week] = {}
			for day in week_days:
				new_schledule_table[week][day] = []
		
		for event_number in range(len(group_week_events)):
			event_start = dt.fromisoformat(group_week_events[event_number]["startDatetime"])
			event_info = {
								"name": group_week_events[event_number]["name"],
								"type": group_week_events[event_number]["typeName"],
								"start": group_week_events[event_number]["startDatetime"],
								"end": group_week_events[event_number]["endDatetime"],
								"slot": group_week_events[event_number]["timeSlotName"],
								"audience": group_week_events[event_number]["rooms"],
								"groups": group_week_events[event_number]["groups"]
							}
			if int(group_week_events[event_number]["recurrenceRule"]["interval"]) == 1:
				new_schledule_table[1][week_days[event_start.weekday()]].append(event_info)
				new_schledule_table[2][week_days[event_start.weekday()]].append(event_info)
			elif int(group_week_events[event_number]["recurrenceRule"]["interval"]) == 2:
					new_schledule_table[group_week_events[event_number]["periodNumber"]][week_days[event_start.weekday()]].append(event_info)
				
		return new_schledule_table
	
	''' получаеться 
	{1st_week:
			{monday:[
						{
							start:
							end:
							name:...
							type:...
							dayslot:...
							Audience:...
						}
						]
				}
	}
	'''