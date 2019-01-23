import os
import json
import requests
from bs4 import BeautifulSoup
from time import strftime
from datetime import datetime, timedelta
import urllib
from crawler_config import *
from pymongo import MongoClient
client = MongoClient("140.116.164.187")
client.test.authenticate("ryuk","kidlab95400")
db = client.AirP
coll = db.pred1

def get_st_id(st_name):
    st_list = []
    with open('location_encode.json','r') as f:
        for line in f:
            st_list.append(line)
    for st in st_list:
        st_info = json.loads(st)
        if(st_info['Sitename']==st_name):
            return st_info['id']

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return -1

def check_flag(val):
    flag = 0
    t = num(val)
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
        return 6
    if(val=='NA'):
        return -1
    if(t>=0):
        return 0
    return 5

data=[]
data_ = []
site_list=[11,16,12,14,15,64,13,51,58,49,54,52,56,57,47,71,53,50,48,1,24,30,32,29,31,28,42,45,44,43,46,67,5,70,2,9,6,10,8,4,7,3,66,65,18,68,20,17,21,19,23,22,27,26,25,35,33,34,69,36,72,37,83,41,40,39,59,61,60,62,80,63,78,75,408,77]
param=33

url = 'https://taqm.epa.gov.tw/pm25/tw/HourlyData.aspx'

date_ = (datetime.now()+timedelta(hours=-1)).strftime("%Y/%m/%d")
hr = (datetime.now()+timedelta(hours=-1)).strftime("%H")
print(date_)
print(hr)

start_date = date_
end_date = date_
for ii in range(1,2,1):
    res_initial=requests.post(url,verify=False)
    payload = {
    'ScriptManager1':'ctl08$UpdatePanel1|ctl08$btnQuery',
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
	'__VIEWSTATE':PM25_VIEWSTATE,
	'__VIEWSTATEGENERATOR':PM25_VIEWSTATEGENERATOR,
	'__EVENTVALIDATION':PM25_EVENTVALIDATION,
    'ctl08$lbSite':site_list, #觀測站
    'ctl08$lbParam':param, #參數
    'ctl08$txtDateS':start_date,
    'ctl08$txtDateE':end_date,
    'ctl08$__endRequest_DownloadReport':'',
    'ctl08$btnQuery':'查詢即時值.'
    }

    res=requests.post(url, data = payload, verify=False)
    content=BeautifulSoup(res.text,'lxml')
    result=content.select('#divGrids > div')
    round_dict={}
    for i in range(0,len(result)+1,2):
        try:
            info=result[i].text.replace('，','').replace('：',':').split()
    
            round_dict['YM']=info[0][9:]
            round_dict['station']=info[1][3:]
            round_dict['feature']=info[2][3:8]

            json_str = ''
            st_id_ = str(get_st_id(round_dict['station'])) 
            #json_str = '{"id":"' + st_id_ + '",'
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
                if(hr_d == hr):
                    flag = check_flag(hr_data[hr_d])
                    json_str = ''
                    if(flag!=-1):
                        if(flag==0):
                            json_str = hr_data[hr_d]
                        else:
                            json_str = str(-1)
                        if(flag==6):
                            json_str = str(0)
                    else:
                        json_str = str(-1)
                    dir_n = './recent6/' + round_dict['feature'] + '/'
                    if not os.path.exists(dir_n):
                        os.makedirs(dir_n)
                    f_n = st_id_+'.json'
                    with open(dir_n+f_n,'r') as s_f:
                        for line in s_f:
                            list_ = line.split(" ")
                            list_5 = list_[-5:]
                        s_f.close()
                    if(json_str=='-1'):
                        yr_pr = date_.split("/")[0]
                        mth_pr = date_.split("/")[1]
                        day_pr = date_.split("/")[2]
                        hr_pr = hr

                        query = {
                            "id" : str(st_id_),
                            "time.year" : int(yr_pr),
                            "time.month" : int(mth_pr),
                            "time.day" : int(day_pr),
                            "time.hour" : int(hr_pr),
                            "feature" : "PM2.5"
                        }
                        print(query)
                        q_result = db.pred1.find(query)
                        for doc in q_result:
                            t_doc = doc
                            print(doc["hr_v"])
                            json_str = doc["hr_v"]
                            json_str = str(int(doc["hr_v"]))
                            break
                        del q_result
                    print(json_str)

                    with open(dir_n+f_n,'a') as o_f:
                        o_f.write(json_str)
                        o_f.write(" ")
                        o_f.close()
                
        except IndexError:
            continue


