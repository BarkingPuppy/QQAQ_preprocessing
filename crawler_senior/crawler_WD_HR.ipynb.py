#%%
import os
os.chdir('e:/QQAQ_project/test/QQAQ_preprocessing/crawler_senior')
import json
import requests
import sys
from bs4 import BeautifulSoup
from time import strftime
import datetime as dt
from crawler_config import *

#%%
with open('location_encode.json', 'r', encoding='utf-8') as f:
    STATION_LIST = json.load(f)
    f.close()
STATION_NAME_LIST = [station['Sitename'] for station in STATION_LIST]
# Type in the feature name you want to crawl (except PM2.5)
FEATURE_NAME = 'WD_HR'
FILE_PATH = './recent6/{feature}/{id}.json'

url = 'https://taqm.epa.gov.tw/taqm/tw/HourlyData.aspx'
current_time = dt.datetime.utcnow() + dt.timedelta(hours=8)
eta_time = current_time + dt.timedelta(hours=-1)

# def get_st_id(st_name):
#     for st_name in STATION_LIST:
#         if st['Sitename'] == st_name:
#             return st['id']

# def num(s):
#     try:
#         return int(s)
#     except ValueError:
#         try:
#             return float(s)
#         except ValueError:
#             return -1            

# def check_flag(val):
#     if(val=='#'):
#         return 1
#     if(val=='*'):
#         return 2
#     if(val=='x'):
#         return 3
#     if(val=='X'):
#         return 3
#     if(val=='NR'):
#         return 4
#     if(val=='null'):
#         return 5
#     if(val==''):
#         return 5
#     if(val=='ND'):
#         return 5
#     if(val=='NA'):
#         return -1
#     if(num(val) >= 0):
#         return 0

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
        if len(station_data) == 24:
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


#%%
stations_checklist = [False for i in range(len(STATION_LIST))]
res_initial = requests.get(url)
soup_initial = BeautifulSoup(res_initial.text, 'lxml')
query_site_sect = soup_initial.select('select#ctl04_lbSite > option')
query_site_list = [int(term['value']) for term in query_site_sect]
query_feature_sect = soup_initial.select('select#ctl04_lbParam > option')
query_feature_dict = {term.text: int(term['value']) for term in query_feature_sect}
feature_param = query_feature_dict[FEATURE_NAME]
# query_site_list = 
# site_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,75,77,78,80,83]
# parameter ID of feature??
# feature_param = 144

#%%
# res_initial = requests.post(url, verify=False)
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

res = requests.post(url, data=payload, verify=False)
soup = BeautifulSoup(res.text, 'lxml')
results = soup.select('div#divGrids > div')
# print(soup.prettify())

#%%
# if __name__ == "__main__":

if not os.path.isdir('./recent6'):
    os.mkdir('recent6')
if not os.path.isdir('./recent6/'+FEATURE_NAME):
    os.mkdir('./recent6/'+FEATURE_NAME)
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
for station_idx, status in enumerate(stations_checklist):
    if status == False:
        updateJsonFile(FEATURE_NAME, station_idx+1)


#%%
