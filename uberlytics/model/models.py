import re

from peewee import *

DB = 'uberlytics/uber.db'

database = SqliteDatabase(DB, threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    user_id = CharField(primary_key=True)
    email = CharField(index=True)
    session_key = CharField()
    session_sig = CharField()
    update_date = DateTimeField()

class UberTrip(BaseModel):
    trip_id = CharField(primary_key=True)
    user_id = CharField(index=True)
    date = DateTimeField()
    duration = IntegerField()
    subtotal = IntegerField()
    surge_rate = IntegerField()
    map_img_src = CharField()
    start_address = CharField()
    end_address = CharField()
    start_lat = CharField()
    start_long = CharField()
    end_lat = CharField()
    end_long = CharField()
    car_type = CharField()
    distance = FloatField()

    def get_trip_coordinates(self):
        if not self.map_img_src:
            return []
        coordinates = []
        path = None
        components = self.map_img_src.split('&')
        for c in components:
            if c.find('path') == 0:
                path = c
                break
        if not path:
            return []
        combined_lat_long = re.findall(r'(-?\d+\.\d+)', path)
        coordinates = []
        for i in range(0, len(combined_lat_long), 2):
            coordinates.append((combined_lat_long[0], combined_lat_long[1]))
        return coordinates

def create_tables():
    database.connect()
    database.create_table(User)
    database.create_table(UberTrip)

def drop_tables():
    database.connect()
    database.drop_table(User)
    database.drop_table(UberTrip)

def init():
    database.connect()
