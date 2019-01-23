import os
import json
import requests
from bs4 import BeautifulSoup
from time import strftime
from datetime import datetime, timedelta
from crawler_config import *


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
        return 5
    if(val=='NA'):
        return -1
    if(t>=0):
        return 0

data=[]
data_ = []
site_list=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,75,77,78,80,83]

param=[10]#1,2,3,4,5,6,7,8,9,10,11,14,21,22,23,31,34,36,38,143,144]

url = 'https://taqm.epa.gov.tw/taqm/tw/HourlyData.aspx'

date_ = (datetime.now()+timedelta(hours=-1)).strftime("%Y/%m/%d")
hr = (datetime.now()+timedelta(hours=-1)).strftime("%H")
print(date_)
print(hr)
#hrt = int(hr)+1
#ht_1 = int(hr)-1
#print(datetime.now() + timedelta(hours=-hrt))


#start_date='2017/05/19' #起始日期
#end_date='2017/05/19'   #結束日期

start_date = date_
end_date = date_
for par in param:
    for ii in range(1,2,1):#site in site_list:
        res_initial=requests.post(url,verify=False)
        payload = {
        'ScriptManager1':'ctl04$UpdatePanel1|ctl04$btnQuery',
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
    	'__VIEWSTATE':TAQM_VIEWSTATE,
    	'__VIEWSTATEGENERATOR':TAQM_VIEWSTATEGENERATOR,
    	'__EVENTVALIDATION':TAQM_EVENTVALIDATION,
        'ctl04$lbSite':site_list, #觀測站
        'ctl04$lbParam':par, #參數
        'ctl04$txtDateS':start_date,
        'ctl04$txtDateE':end_date,
        'ctl04$__endRequest_DownloadReport':'',
        'SearchBox1$txtKeyword':'',
        'ctl04$btnQuery':'查詢即時值.'
        }

        res=requests.post(url, data = payload,verify=False)
        content=BeautifulSoup(res.text,'lxml')
        result=content.select('#divGrids > div')
        round_dict={}
        for i in range(0,len(result)+1,2):
            try:    
                info=result[i].text.replace('，','').replace('：',':').split()
    
                round_dict['YM']=info[0][5:]
                round_dict['station']=info[1][3:]
                round_dict['feature']=info[2][3:]

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
    
            #json_str = json_str + '"date":{"year":' + str(int(round_dict['YM'].split('/')[0])) + ','
            #json_str = json_str + '"month":' + str(int(round_dict['MD'].split('/')[0])) + ','
            #json_str = json_str + '"day":' + str(int(round_dict['MD'].split('/')[1])) + '},'
            #json_str = json_str + '"station":' + json.dumps(round_dict['station']) + ','
#    json_str = json_str + '"station":' + round_dict['station'] + ','
#    json_str = json_str + '"feature":' + round_dict['feature'] + ','
            #json_str = json_str + '"feature":'+ json.dumps(round_dict['feature']).split("\\")[0] + '",'
            #json_str = json_str + '"hr_data":['

            #hr_data_list = []
                for hr_d in sorted(hr_data):#.items():
                    if(hr_d == hr):
                        flag = check_flag(hr_data[hr_d])
                        json_str = ''
                        if(flag!=-1):
                        #hr_v = 0
                        #json_str = json_str + '{"hr_t":' + str(int(hr_d)) + ','
                            if(flag==0):
                            #json_str = json_str + '"hr_v":' + hr_data[hr_d] + ',' 
                            #hr_v = hr_data[hr_d]
                                json_str = hr_data[hr_d]
                            else:
                            #json_str = json_str + '"hr_v":' + str(-1) + ','
                            #hr_v = -1
                                json_str = str(-1)
                        #json_str = json_str + '"hr_flag":' + str(flag) + '},'
                        #hr_t_v_f = {
                        #    "hr_t" : int(hr_d),
                        #    "hr_v" : num(hr_v),
                        #    "hr_flag": flag
                        #    }
                        #hr_data_list.append(hr_t_v_f)
                        else:
                            json_str = str(-1)
                        dir_n = './recent6/' + json.dumps(round_dict['feature']).split("\\")[0].split('"')[1] + '/'
                        if not os.path.exists(dir_n):
                            os.makedirs(dir_n)
                        f_n = st_id_+'.json' #date_ymd + '_' + st_id_ + '.json'
                        with open(dir_n+f_n,'a') as o_f:
                            o_f.write(json_str)
                            o_f.write(" ")
                            o_f.close()
                        '''
            json_str = json_str[:-1]
            json_str = json_str + ']}'
            data.append(round_dict)
#    print(get_st_id(round_dict['station']))
#    print(int(round_dict['YM'].split('/')[0]))
#    print(int(round_dict['MD'].split('/')[0]))
#    print(int(round_dict['MD'].split('/')[1]))
            yr_ = int(round_dict['YM'].split('/')[0])
            mth_ = int(round_dict['MD'].split('/')[0])
            day_ = int(round_dict['MD'].split('/')[1])
            date_ymd = str(int(round_dict['YM'].split('/')[0]))+'-'+str(int(round_dict['MD'].split('/')[0]))+'-'+str(int(round_dict['MD'].split('/')[1]))

#            print(json_str)

            dir_n = './collect_recent/' + json.dumps(round_dict['feature']).split("\\")[0].split('"')[1] + '/'
            if not os.path.exists(dir_n):
                os.makedirs(dir_n)

            f_n = date_ymd + '_' + st_id_ + '.json'
            with open(dir_n+f_n,'w') as o_f:
                o_f.write(json_str)
                o_f.write("\n")
                o_f.close()

            query = {
                    "id" : str(st_id_),
                    "date.year" : yr_,
                    "date.month" : mth_,
                    "date.day" : day_,
                    "feature" : json.dumps(round_dict['feature']).split("\\")[0].split('"')[1]# round_dict['feature']
                }

            update_data = {
                        "id" : str(st_id_),
                        "date" : {
                                "year" : yr_,
                                "month" : mth_,
                                "day" : day_
                        },
                        "station" : round_dict['station'],
                        "feature" : json.dumps(round_dict['feature']).split("\\")[0].split('"')[1],#round_dict['feature'],
                        "hr_data" : hr_data_list
                }
            print(query)
            print(str(st_id_))
#        print(json_str)
#        json_import = json.loads(json_str)
#        print(json_import)
            result = db.record5.update_one(query,{'$set':update_data},upsert=True)
            print(result)
                        '''	    	
			
#with open('data.json', 'w') as outfile:
#    json.dump(data_, outfile,ensure_ascii=True,sort_keys=True)
            except IndexError:
                continue



