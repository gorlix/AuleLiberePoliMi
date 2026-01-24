from email.policy import default
from .find_classrooms import find_classrooms
from collections import defaultdict
from pprint import pprint
from logging import root
import datetime
import json 

MAX_TIME = 20

def _is_room_free(lessons, starting_time, ending_time):
    until = MAX_TIME
    
    if len(lessons) == 0:
        return (True, until)

    for lesson in lessons:
        start = float(lesson['from'])
        end = float(lesson['to'])

        if starting_time <= start and start < ending_time:
            return (False, None)

        if start <= starting_time and end > starting_time:
            return (False, None)

        if ending_time <= start and until == MAX_TIME:
            until = start

    return (True, until)




def find_free_room(starting_time , ending_time , location , day , month , year):
    # Load opening hours
    try:
        with open('json/opening_hours.json') as json_file:
            all_opening_hours = json.load(json_file)
    except FileNotFoundError:
        all_opening_hours = {}

    # Identify campus key (MIA, MIB, or default)
    # location_dict maps "Milano Città Studi" to "MIA", etc.
    # The input 'location' is already the code (e.g. "MIA")
    campus_rules = all_opening_hours.get(location, all_opening_hours.get("default_campus", {}))
    
    # Calculate day of week (0=Monday, 6=Sunday)
    weekday = str(datetime.date(year, month, day).weekday())
    
    free_rooms = defaultdict(list)
    infos = find_classrooms(location , day , month , year)

    for building in infos:
        # Determine opening hours for this specific building
        # 1. Search for specific building rule
        building_rule = None
        for key in campus_rules:
            if key in building: # Substring match (e.g. "Edificio 11" in " Edificio 11 ")
                building_rule = campus_rules[key]
                break
        
        # 2. Fallback to campus default
        if building_rule is None:
            building_rule = campus_rules.get("default", {})

        # Get hours for today
        # Check "0-4" range for Mon-Fri
        if weekday in ["0", "1", "2", "3", "4"]:
            day_hours = building_rule.get("0-4", [])
        else:
            day_hours = building_rule.get(weekday, [])

        if not day_hours:
            # Closed today
            continue

        campus_open, campus_close = day_hours
        
        # If search is completely outside opening hours, skip
        if ending_time <= campus_open or starting_time >= campus_close:
            continue

        for room in infos[building]:
            lessons = infos[building][room]['lessons']
            free, until = _is_room_free(lessons , starting_time , ending_time)
            if free:
                # Cap the 'until' time to the closing time
                if until > campus_close:
                    until = campus_close
                
                room_info = {
                    'name' : room , 
                    'link':infos[building][room]['link'], 
                    'until': until,
                    'powerPlugs': infos[building][room]['powerPlugs']
                }
                
                free_rooms[building].append(room_info)
    
    return free_rooms


if __name__ == "__main__":
    now = datetime.datetime.now()
    info = find_free_room(9.25 , 12.25 , 'MIA', 25 , 10 , 2021)
    with open('infos_a.json' , 'w') as outfile:
        json.dump(info , outfile)