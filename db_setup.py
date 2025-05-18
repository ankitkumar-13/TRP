import mysql.connector
from mysql.connector import errorcode
import datetime

import requests

from db_backups.city_state import states

def get_lat_long(place_name):
    """
        Send a request(GET Request) to API.
        Response is in a format format like -> [ {'lat': 12.45324, 'long': 54.56577} ] 
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json"
    }
    headers = {
        "User-Agent": "TRP/get-long-lat-script/1.0"  # Required by OSM's usage policy
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return float(lat), float(lon)
    else:
        return None

class City:
    def __init__(self, name, culture, unique, image_path=None):
        self.name = name
        self.lat = None
        self.long = None
        self.culture = culture
        self.unique = unique
        self.image_path = image_path
    def _setLatLong(self):
        data = get_lat_long(self.name)
        if data==None:
            raise Exception("Unknown Service Error while fetching coordinates !")
        else:
            self.lat, self.long = data
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name


def get_time(format_12_hour=False) -> str:
    """Return string of current date in (YYYY-MM-DD ~ 21:19:59) by default.
        If format_12_hour=True, then in (YYYY-MM-DD ~ 09:19:59) format.
    """
    date_time_obj = datetime.datetime.now()
    if(format_12_hour):
        return date_time_obj.strftime("%Y-%m-%d ~ %I:%M:%S %p")
    return date_time_obj.strftime("%Y-%m-%d ~ %H:%M:%S")


def log(message :str, level=0, file_name = "database_logs.txt", format_12_hour=False) -> None:
    """Logging all logs into a file. By default logs into database_logs.txt
        Logs with time in the front. level defines the number of tabs preceeding the message.
    """
    with open(file_name, mode='a') as f:
        # [ DATE ~ TIME ] (tabs) + message + newline
        f.write("[" + get_time(format_12_hour) + "] " + "\t"*level + message + "\n")


def establish_default_con(database:str = None, user="root", password="", host="127.0.0.1") -> mysql.connector.MySQLConnection|None:
    """Connects to a mysql database and returns the connection object if connected successfull, otherwise None.
        By default doesn't connect to any database.
        Can use (database = 'database_name')   ->  for connection to a specific database.
    """
    log("Entered the establish_default_con() function...")
    try:
        if(database==None):
            con = mysql.connector.connect(user=user, password=password, host=host)
        else:
            con = mysql.connector.connect(user=user, password=password, host=host, database=database)
    except mysql.connector.Error as err:
        if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
            msg = "Either username or password is wrong."
            print(msg); log(msg)
        elif (err.errno == errorcode.ER_BAD_DB_ERROR):
            msg = f"No Database named '{{database}}' found on the MySQL server."
            print(msg); log(msg)
        else:
            msg = "Unknown Error : " + err
            print(msg); log(msg)
    else:
        log("Returned MySQLConnection object.")
        return con
    finally:
        log("Exiting the establish_default_con() function...", 1)
    return None


def create_db(con: mysql.connector.MySQLConnection, database_state="trp_state_db"):
    """
    trp_state_db -> database storing data related to info about location in a State.
    trp_state_table. -> all States in India.
    trp_state_(state_name)_table -> all major cities and districts in state_name.
    """
    cur = con.cursor()
    cur.execute(f"CREATE DATABASE {database_state}")
    cur.execute(f"USE {database_state}")
    state_table_command = """
        CREATE TABLE IF NOT EXISTS trp_state_table (
            state_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )"""
    cur.execute(state_table_command)
    for state in states:
        cur.execute(f"""INSERT INTO trp_state_table (name) VALUES ("{state[0]}")""")
    curr_state = states[0][0].lower()
    specific_state_table_command = f"""
        CREATE TABLE IF NOT EXISTS trp_state_{curr_state}_table (
            city_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            culture TEXT,
            unique_features TEXT,
            image_path VARCHAR(255)
        )"""
    cur.execute(specific_state_table_command)
    
    for state in states:
        if state[0]=='Uttarakhand':
            s_name_lower = state[0].lower()
            for (name, data) in state[1].items():
                image_path = data['image_path']
                if (image_path==None):
                    image_path="N/A"
                cur.execute(f"""INSERT INTO trp_state_{s_name_lower}_table (name, culture, unique_features, image_path) 
                        VALUES ("{name}", "{data['culture']}", "{data['unique']}", "{image_path}")""")
    con.commit()
    cur.close()


def check_if_con_active(con :mysql.connector.MySQLConnection) -> bool:
    return con.is_connected()


def getAllCities(state = "Uttarakhand"):
    con = establish_default_con("trp_state_db")
    if con==None:
        con = establish_default_con()
        create_db(con)    
    cities = []
    cur = con.cursor()
    cur.execute(f"""SELECT name, culture, unique_features, image_path from trp_state_{state.lower()}_table""")
    for (name, culture, unique, image_path) in cur:
        cities.append(City(name, culture, unique, image_path))
    cur.close()
    con.close()
    return cities