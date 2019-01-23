import os
import json
import requests
from bs4 import BeautifulSoup
from time import strftime
from datetime import datetime, timedelta
from crawler_config import *

with open('location_encode.json', 'r', encoding='utf-8') as f:
    station_list = json.load(f)
    f.close()
def get_st_id(st_name):
    for st in station_list:
        if st['Sitename'] == st_name:
            return st['id']

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return -1

def check_flag(val):
    if(val=='#'):
        return 1
    if(val=='*'):
        return 2
    if(val=='x'):
        return 3
    if(val=='X'):
        return 3
    if(val=='NR'):
        return 4
    if(val=='null'):
        return 5
    if(val==''):
        return 5
    if(val=='ND'):
        return 5
    if(val=='NA'):
        return -1
    if(num(val) >= 0):
        return 0

data_ = []
site_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,75,77,78,80,83]
# parameter ID of feature??
param = 144

url = 'https://taqm.epa.gov.tw/taqm/tw/HourlyData.aspx'
eta_date = (datetime.now()+timedelta(hours=-1)).strftime("%Y/%m/%d")
eta_hr = (datetime.now()+timedelta(hours=-1)).strftime("%H")
print(eta_date)
print(eta_hr)

res_initial = requests.post(url, verify=False)
payload = {
    'ScriptManager1':'ctl04$UpdatePanel1|ctl04$btnQuery',
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__VIEWSTATE': TAQM_VIEWSTATE,
    '__VIEWSTATEGENERATOR':TAQM_VIEWSTATEGENERATOR,
    '__EVENTVALIDATION': TAQM_EVENTVALIDATION,
    'ctl04$lbSite': site_list, #觀測站
    'ctl04$lbParam': param, #參數
    'ctl04$txtDateS': eta_date,
    'ctl04$txtDateE': eta_date,
    'ctl04$__endRequest_DownloadReport':'',
    'SearchBox1$txtKeyword':'',
    'ctl04$btnQuery':'查詢即時值.'
}

res = requests.post(url, data=payload, verify=False)
content = BeautifulSoup(res.text, 'lxml')
result = content.select('#divGrids > div')
round_dict={}
for i in range(0,len(result)+1,2):
    try:    
        info=result[i].text.replace('，','').replace('：',':').split()

        round_dict['YM']=info[0][5:]
        round_dict['station']=info[1][3:]
        round_dict['feature']=info[2][3:]

        json_str = ''
        st_id_ = str(get_st_id(round_dict['station'])) 
        data_.append(round_dict)
        result_sub=result[i+1].find("table",{"class" : "TABLE_G"})
        round_len=len(result_sub.findAll('th'))
        round_=0
        hr_data = {}
        while round_ < round_len:
            if(round_==0):
                round_dict['MD'] = result_sub.findAll('td')[round_].text
            else:
                round_dict[result_sub.findAll('th')[round_].text] = result_sub.findAll('td')[round_].text
                hr_data[result_sub.findAll('th')[round_].text] = result_sub.findAll('td')[round_].text
            round_=round_+1

        for hr_d in sorted(hr_data):
            if(hr_d == eta_hr):
                flag = check_flag(hr_data[hr_d])
                json_str = ''
                if(flag!=-1):
                    if(flag==0):
                        json_str = hr_data[hr_d]
                    else:
                        json_str = str(-1)
                else:
                    json_str = str(-1)
                dir_n = './recent6/' + json.dumps(round_dict['feature']).split("\\")[0].split('"')[1] + '/'
                if not os.path.exists(dir_n):
                    os.makedirs(dir_n)
                f_n = st_id_+'.json'
                with open(dir_n+f_n,'a') as o_f:
                    o_f.write(json_str)
                    o_f.write(" ")
                    o_f.close()
    except IndexError:
        continue



