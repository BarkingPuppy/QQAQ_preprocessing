#%%
import os
import datetime as dt
import json
from pymongo import MongoClient
from pprint import pprint

FILE_PATH = './recent6/{feature}/{id}.json'
STATIONS_TOTAL = 76
FEATURE_LIST = ["PM2.5","PM10","WS_HR","WD_HR","WIND_SPEED","WIND_DIREC","AMB_TEMP","RH"]

with open('config/db_config.json', 'r') as f:
    info = json.load(f)
    DB_USERNAME = info['username']
    DB_PASSWORD = info['password']
    DB_HOST = info['database_host']
    f.close()

db_conn = MongoClient('mongodb://{uid}:{psd}@{db_host}'
    .format(uid=DB_USERNAME, psd=DB_PASSWORD, db_host=DB_HOST))
db = db_conn['AirP']['record3']

current_time = dt.datetime.utcnow() + dt.timedelta(hours=8)
epa_time = current_time + dt.timedelta(hours=-1)

def updateJsonFile(feat, station_id, data=None):
    if data is None:
        data = {
            'date': current_time.strftime('%Y-%m-%d'),
            'hour': current_time.hour,
            'value': -2
        }
    try:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'r', encoding='utf-8') as fr:
            station_data = json.load(fr)
            fr.close()
        if len(station_data) == 24:
            del station_data[0]
        station_data.append(data)
    except FileNotFoundError:
        station_data = [data]
    finally:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'w', encoding='utf-8') as fw:
            json.dump(station_data, fw, indent=4, separators=(',', ':'))
            fw.close()


#%%
for feat in FEATURE_LIST:
    stations_checklist = [False for i in range(STATIONS_TOTAL)]
    query = {
        'date.year': epa_time.year,
        'date.month': epa_time.month,
        'date.day': epa_time.day,
        'feature': feat,
        'id': {'$ne': 'None'}
    }
    results = db.find(query)
    for result in results:
        hr_data_dict = {
            'date': current_time.strftime('%Y-%m-%d'),
            'hour': current_time.hour
        }
        station_id = int(result['id'])
        if result.get('hr_data'):
            hr_data = result['hr_data'][-1]
            if hr_data['hr_flag'] == 0 and hr_data['hr_t'] == epa_time.hour:
                hr_data_dict['value'] = hr_data['hr_v']
            elif hr_data['hr_flag'] != 0:
                hr_data_dict['value'] = -1
            elif hr_data['hr_t'] != epa_time.hour:
                hr_data_dict['value'] = -2
            stations_checklist[station_id-1] = True            
            updateJsonFile(feat, station_id, hr_data_dict)
    for station_idx, status in enumerate(stations_checklist):
        if status == False:
            updateJsonFile(feat, station_idx+1)

#%%
query = {
    # 'date.year': epa_time.year,
    # 'date.month': epa_time.month,
    # 'date.day': epa_time.day,
    'date.year': {'$gte': 2017},
    # 'feature': 'PM2.5',
    'hr_data': {'$elemMatch': {'hr_flag': -1}}
}
result = db.find_one(query)
pprint(result)

#%%
db_pred = db_conn['AirP']['pred1']
results = db_pred.find({
    'time.year': epa_time.year,
    'time.month': epa_time.month,
    'time.day': epa_time.day,
    'feature': 'PM2.5',
    'id': station_id
})
for r in results:
    term = {
        'time': r['time'],
        'hr_v': r['hr_v']
    }
    pprint(term)
    print(" ")

#%%
def hrflag_query(hr_flag):
    return {'feature': 'PM2.5', 'hr_data': {'$elemMatch': {'hr_flag': hr_flag}}}
db.find_one({'feature': 'PM2.5', 'hr_data': {'$elemMatch': {'hr_flag': 0, 'hr_t': 21}}})

#%%
