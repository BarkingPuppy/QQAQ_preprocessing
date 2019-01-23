#! python3
import datetime as dt
import json, os
from pprint import pprint
from pymongo import MongoClient

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
            'value': -3
        }
    try:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'r', encoding='utf-8') as fr:
            station_data = json.load(fr)
            fr.close()
        if len(station_data) == 24:
            del station_data[0]
        if station_data[-1]['hour'] != current_time.hour:
            station_data.append(data)
        else:
            station_data[-1]['value'] = data['value']
            station_data[-1]['multiple_execution'] = True
    except FileNotFoundError:
        station_data = [data]
    finally:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'w', encoding='utf-8') as fw:
            json.dump(station_data, fw, sort_keys=True, indent=4, separators=(',', ':'))
            fw.close()


if __name__ == "__main__":

    if not os.path.isdir('./recent6'):
        os.mkdir('recent6')
    print('*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*')
    print('Time:', current_time.strftime('%Y-%m-%d %H:%M:%S'))
    for feat in FEATURE_LIST:
        print('Feature:', feat)
        if not os.path.isdir('./recent6/'+feat):
            os.mkdir('./recent6/'+feat)
        stations_checklist = [False for i in range(STATIONS_TOTAL)]
        query = {
            'date.year': epa_time.year,
            'date.month': epa_time.month,
            'date.day': epa_time.day,
            'feature': feat,
            'id': {'$ne': 'None'}
        }
        counter = 0
        results = db.find(query)
        for result in results:
            hr_data_dict = {
                'date': current_time.strftime('%Y-%m-%d'),
                'hour': current_time.hour
            }
            station_id = int(result['id'])
            # print('Current station:', station_id)
            if result.get('hr_data'):
                hr_data = result['hr_data'][-1]
                if hr_data['hr_flag'] == 0 and hr_data['hr_t'] == epa_time.hour:
                    hr_data_dict['value'] = hr_data['hr_v']
                    counter += 1
                elif hr_data['hr_flag'] != 0 and hr_data['hr_t'] == epa_time.hour:
                    hr_data_dict['value'] = -1
                    counter += 1
                elif hr_data['hr_t'] != epa_time.hour:
                    hr_data_dict['value'] = -2
                    stations_checklist[station_id-1] = True            
                    updateJsonFile(feat, station_id, hr_data_dict)
        print('Station counter:', counter)
        for station_idx, status in enumerate(stations_checklist):
            if status == False:
                updateJsonFile(feat, station_idx+1)
