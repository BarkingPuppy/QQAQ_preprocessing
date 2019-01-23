import datetime as dt
import json
import os
import requests
import sys
from bs4 import BeautifulSoup
from crawler_config import *
from time import time
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

with open('location_encode.json', 'r', encoding='utf-8') as f:
    STATION_LIST = json.load(f)
    f.close()
STATION_NAME_LIST = [station['Sitename'] for station in STATION_LIST]
'''
Type in the TAQM feature name you want to crawl (except PM2.5) in the CLI. 
The feature name will be considered a parameter passed to this program.
'''
FEATURE_NAME = sys.argv[1]
FILE_PATH = './recent6/{feature}/{id}.json'
RETRY_LIMIT = 10

url = 'https://taqm.epa.gov.tw/taqm/tw/HourlyData.aspx'
current_time = dt.datetime.utcnow() + dt.timedelta(hours=8)
eta_time = current_time + dt.timedelta(hours=-1)

def checkValueValidity(val):
    try:
        if '.' in val:
            hr_v = float(val)
        else:
            hr_v = int(val)
        hr_flag = 0
    except ValueError:
        if '#' in val:
            hr_flag = 1
        elif '*' in val: 
            hr_flag = 2
        elif 'x' in val: 
            hr_flag = 3
        elif 'X' in val: 
            hr_flag = 3
        elif val == 'NR': 
            hr_flag = 4
        elif val == 'null': 
            hr_flag = 5
        elif val == '': 
            hr_flag = 5
        elif val == 'NA': 
            hr_flag = -1
        elif val == 'ND':
            hr_v = 1
            hr_flag = 0
        else:
            hr_flag = 6
    finally:
        if hr_flag != 0:
            hr_v = -1
        return hr_flag, hr_v

def updateJsonFile(feat, station_id, data=None):
    if data is None:
        data = {
            'date': current_time.strftime('%Y-%m-%d'),
            'hour': current_time.hour,
            'hr_flag': -2,
            'hr_v': -2
        }
    try:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'r', encoding='utf-8') as fr:
            station_data = json.load(fr)
            fr.close()
        if len(station_data) == 24*7:
            del station_data[0]
        if station_data[-1]['hour'] != current_time.hour:
            station_data.append(data)
        else:
            station_data[-1]['hr_flag'] = data['hr_flag']
            station_data[-1]['hr_v'] = data['hr_v']
            station_data[-1]['multiple_execution'] = True
    except FileNotFoundError:
        station_data = [data]
    finally:
        with open(FILE_PATH.format(feature=feat, id=station_id), 'w', encoding='utf-8') as fw:
            json.dump(station_data, fw, sort_keys=True, indent=4, separators=(',', ':'))
            fw.close()


if __name__ == "__main__":
    t_start = time()
    if not os.path.isdir('./recent6'):
        os.mkdir('recent6')
    if not os.path.isdir('./recent6/'+FEATURE_NAME):
        os.mkdir('./recent6/'+FEATURE_NAME)
    print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
    print('Time:', current_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('Feature:', FEATURE_NAME)
    
    for retry_ctr in range(RETRY_LIMIT+1):
        try:
            res_initial = requests.get(url)
            break
        except:
            continue
    else:
        for station_idx in range(len(STATION_LIST)):
            updateJsonFile(FEATURE_NAME, station_idx+1)
        t_end = time()
        print('Retry limit has been reached while requesting data from EPA website.')
        print('Elapsed time: {:.0f} sec'.format(t_end - t_start))
        exit()

    soup_initial = BeautifulSoup(res_initial.text, 'lxml')
    query_site_sect = soup_initial.select('select#ctl04_lbSite > option')
    query_site_list = [int(term['value']) for term in query_site_sect]
    query_feature_sect = soup_initial.select('select#ctl04_lbParam > option')
    query_feature_dict = {term.text: int(term['value']) for term in query_feature_sect}
    feature_param = query_feature_dict[FEATURE_NAME]
    stations_checklist = [False for i in range(len(STATION_LIST))]

    payload = {
        'ScriptManager1':'ctl04$UpdatePanel1|ctl04$btnQuery',
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        '__VIEWSTATE': TAQM_VIEWSTATE,
        '__VIEWSTATEGENERATOR':TAQM_VIEWSTATEGENERATOR,
        '__EVENTVALIDATION': TAQM_EVENTVALIDATION,
        'ctl04$lbSite': query_site_list, #觀測站
        'ctl04$lbParam': feature_param, #feature參數
        'ctl04$txtDateS': eta_time.strftime("%Y/%m/%d"),
        'ctl04$txtDateE': eta_time.strftime("%Y/%m/%d"),
        'ctl04$__endRequest_DownloadReport':'',
        'SearchBox1$txtKeyword':'',
        'ctl04$btnQuery':'查詢即時值.'
    }
    for retry_ctr in range(RETRY_LIMIT+1):
        try:
            res = requests.post(url, data=payload, verify=False)
            break
        except:
            continue
    else:
        for station_idx in range(len(STATION_LIST)):
            updateJsonFile(FEATURE_NAME, station_idx+1)
        t_end = time()
        print('Retry limit has been reached while requesting data from EPA website.')
        print('Elapsed time: {:.0f} sec'.format(t_end - t_start))
        exit()

    soup = BeautifulSoup(res.text, 'lxml')
    results = soup.select('div#divGrids > div')
    if len(results) > 0:
        for i, result in enumerate(results):
            if i % 2 == 0:
                st_info = result.text.replace('\r', '').replace('\n', '').split('，')
                st_name = st_info[1][3:]
                if st_name in STATION_NAME_LIST:
                    st_id = STATION_NAME_LIST.index(st_name)+1
                    stations_checklist[st_id-1] = True
                    val_table = results[i+1].select('tr:nth-of-type(2) > td')
                    hr_flag, hr_v = checkValueValidity(val_table[eta_time.hour+1].text)
                    hr_data = {
                        'date': current_time.strftime('%Y-%m-%d'),
                        'hour': current_time.hour,
                        'hr_flag': hr_flag,
                        'hr_v': hr_v
                    }
                    updateJsonFile(FEATURE_NAME, st_id, hr_data)
    station_not_exist_str = 'Stations not exist:'
    for station_idx, status in enumerate(stations_checklist):
        if status == False:
            updateJsonFile(FEATURE_NAME, station_idx+1)
            station_not_exist_str += (' ({} {})'.format(station_idx+1, STATION_NAME_LIST[station_idx]))
    t_end = time()
    print(station_not_exist_str)
    print('Elapsed time: {:.0f} sec'.format(t_end - t_start))
