import time
import requests
from bs4 import BeautifulSoup
import json
from logging import root

URL = "https://onlineservices.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
BASE_URL = "https://onlineservices.polimi.it/spazi/spazi/controller/"
BUILDING = 'innerEdificio'
ROOM = 'dove'
LECTURE = 'slot'
TIME_SHIFT = 0.25
MIN_TIME = 8
MAX_TIME = 20
CACHE_TTL = 1800 # 30 minutes in seconds
CACHE = {}

GARBAGE = ["PROVA_ASICT" , "2.2.1-D.I."]


"""
Clean the dict with all the class occupancies from rooms that don't exists or are unreacheable
"""
def clean_data(infos):
    for building in infos:
        for room in GARBAGE:
            if room in infos[building]:
                del infos[building][room]          
            
    return infos


"""
Return a dict with all the info about the classrooms for the chosen day , 
the function makes a get requests to the URL and then 
build a dict with the classes information stored on the html table (the code may not be perfect 🥲)
"""

def find_classrooms(location , day , month , year):
    
    # Cache check
    cache_key = (location, day, month, year)
    if cache_key in CACHE:
        if time.time() - CACHE[cache_key]['timestamp'] < CACHE_TTL:
            print(f"CACHE HIT for {cache_key}")
            return CACHE[cache_key]['data']
        else:
            print(f"CACHE EXPIRED for {cache_key}")
            del CACHE[cache_key]
    else:
        print(f"CACHE MISS for {cache_key}")

    info = {} 
    buildingName = '-' #defaul value for building
    info[buildingName] = {} #first initialization due to table format

    params = {'csic': location , 'categoria' : 'tutte', 'tipologia' : 'tutte', 'giorno_day' : day , 'giorno_month' : month, 'giorno_year' : year , 'jaf_giorno_date_format' : 'dd%2FMM%2Fyyyy'  , 'evn_visualizza' : ''}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        t_net_start = time.time()
        r = requests.get(URL , params= params, headers=headers) 
        t_net_end = time.time()
        print(f"Network request took: {t_net_end - t_net_start:.2f}s")
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}")
        return {}
    
    if r.status_code != 200:
        print(f"Error: Failed to fetch data. Status code: {r.status_code}")
        return {}
    
    soup = BeautifulSoup(r.text, 'html.parser')
    tableContainer = soup.find("div", {"id": "tableContainer"})
    tableRows = tableContainer.find_all('tr')[3:] #remove first three headers

    with open("json/roomsWithPower.json","r") as j:
        rwp = set(json.load(j))

    for row in tableRows:
        tds = row.find_all('td')
        if 'class' not in row.attrs:
            if BUILDING in tds[0].attrs['class']:
                buildingName = tds[0].string
                try:
                    # buildingName = re.search('(Edificio.*)' , buildingName).group(1) #take only the building name
                    buildingName = buildingName.split('-')[2]
                except:
                    print(buildingName)
                if buildingName not in info:
                    info[buildingName] = {}
        else:
            room = ''
            time_slot = 7.75
            for td in tds:
                if ROOM in td.attrs['class']:
                    room = td.find('a').string.replace(" ","")
                    link = td.find('a')['href']
                    id_aula = int(link.split("=")[-1])
                    
                    if room not in info[buildingName]:
                        info[buildingName][room] = {}
                        info[buildingName][room]['link'] = BASE_URL + link
                        info[buildingName][room]['lessons'] = []
                        info[buildingName][room]['powerPlugs'] = id_aula in rwp

                elif LECTURE in td.attrs['class'] and room != '':
                    duration = int(td.attrs['colspan'])
                    lesson_name = td.find('a').string
                    lesson = {}
                    lesson['name'] = lesson_name
                    lesson['from'] = time_slot
                    time_slot += duration/4
                    lesson['to'] = time_slot
                    info[buildingName][room]['lessons'].append(lesson)
                else:
                    time_slot += TIME_SHIFT
    
    data = clean_data(info)
    
    # Cache store
    CACHE[cache_key] = {
        'timestamp': time.time(),
        'data': data
    }
    
    return data




if __name__ == "__main__":
    infos =  find_classrooms('MIA' , 25 , 10 , 2021)
    with open('json/infos_a.json' , 'w') as outfile:
        json.dump(infos , outfile, indent=3)