#%%
import os
import datetime as dt
import json
from pymongo import MongoClient
from pprint import pprint

#%%
with open('config/db_config.json', 'r') as f:
    info = json.load(f)
    DB_USERNAME = info['username']
    DB_PASSWORD = info['password']
    DB_HOST = info['database_host']
    f.close()

db_conn = MongoClient('mongodb://{uid}:{psd}@{db_host}'
    .format(uid=DB_USERNAME, psd=DB_PASSWORD, db_host=DB_HOST))
db = db_conn['AirP']['pred1']

#%%
db.find_one(
    {
        'id': '76',
        'time.year': 2019,
        'time.month': 2,
        'time.day': 8,
        'time.hour': 12
    }
)

#%%
