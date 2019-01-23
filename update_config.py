import os
import json
import requests
from bs4 import BeautifulSoup
from time import strftime
from datetime import datetime, timedelta
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

config_filename = "crawler_config.py"

pm25_url = 'https://taqm.epa.gov.tw/pm25/tw/HourlyData.aspx'
taqm_url = 'https://taqm.epa.gov.tw/taqm/tw/HourlyData.aspx'

res = requests.get(pm25_url,verify=False)
res.encoding = 'utf8'
content=BeautifulSoup(res.text,'lxml')
PM25_VIEWSTATE = (content.find(id="__VIEWSTATE"))['value']
PM25_VIEWSTATEGENERATOR = (content.find(id="__VIEWSTATEGENERATOR"))['value']
PM25_EVENTVALIDATION = (content.find(id="__EVENTVALIDATION"))['value']

res = requests.get(taqm_url,verify=False)
res.encoding = 'utf8'
content=BeautifulSoup(res.text,'lxml')
TAQM_VIEWSTATE = (content.find(id="__VIEWSTATE"))['value']
TAQM_VIEWSTATEGENERATOR = (content.find(id="__VIEWSTATEGENERATOR"))['value']
TAQM_EVENTVALIDATION = (content.find(id="__EVENTVALIDATION"))['value']

print(PM25_VIEWSTATE)
print(PM25_VIEWSTATEGENERATOR)
print(PM25_EVENTVALIDATION)
print(TAQM_VIEWSTATE)
print(TAQM_VIEWSTATEGENERATOR)
print(TAQM_EVENTVALIDATION)

with open(config_filename,'w') as f_o:
    f_o.write("PM25_VIEWSTATE = '{}'\n".format(PM25_VIEWSTATE))
    f_o.write("PM25_VIEWSTATEGENERATOR = '{}'\n".format(PM25_VIEWSTATEGENERATOR))
    f_o.write("PM25_EVENTVALIDATION = '{}'\n".format(PM25_EVENTVALIDATION))
    f_o.write("TAQM_VIEWSTATE = '{}'\n".format(TAQM_VIEWSTATE))
    f_o.write("TAQM_VIEWSTATEGENERATOR = '{}'\n".format(TAQM_VIEWSTATEGENERATOR))
    f_o.write("TAQM_EVENTVALIDATION = '{}'\n".format(TAQM_EVENTVALIDATION))
    f_o.close()

