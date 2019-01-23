#! python3
# coding: utf-8
import math, json, time
import numpy as np

tStart = time.time()
RECENT_SIX_PATH = './recent6'
RESULT_PATH = './lstm_input'
KNN_K = 3   # "k" of k-NN
STATIONS_TOTAL = 76
# 註: PM2.5有兩個，第一個是PM2.5差值（當前-上一小時），第二個是PM2.5值；
# PASS為預留給風向資料拆成cos和sin的位置，會於迴圈中略過
FEAT_LIST = ["PM2.5","PM2.5","PM10","WS_HR","WD_HR","PASS","WIND_SPEED","WIND_DIREC","PASS","AMB_TEMP","RH"]
FEAT_BASE = [500,500,500,30,1,1,30,1,1,50,100]

with open('./knn_dtw.json', 'r') as f:
    knn_dtw_data = json.load(f)
    f.close()
with open('./knn_ed.json', 'r') as f:
    knn_ed_data = json.load(f)
    f.close()

def countDeltaOfPollutionValue(pollution_list):
    delta_list = [-1.0 for i in range(6)]
    for i in range(len(delta_list)):
        if i > 0:
            if pollution_list[i] != -1 and pollution_list[i-1] != -1:
                delta_list[i] = pollution_list[i] - pollution_list[i-1]
    return delta_list

def getSelfAndKNNList(station_id):
    station_id = str(station_id)
    station_list = [station_id]
    for i in range(KNN_K):
        station_list.append(knn_dtw_data[station_id][i])
        station_list.append(knn_ed_data[station_id][i])
    return [int(sid) for sid in station_list]

def getRecentSixHourValues(station_id, feature):
    try:
        path = '{}/{}/{}.json'.format(RECENT_SIX_PATH, feature, station_id)
        with open(path, 'r') as f:
            data = f.readlines()
            recent_six_list = data[0].split()[-6:]
            for i, val in enumerate(recent_six_list):
                recent_six_list[i] = float(val)
            f.close()
        return recent_six_list
    except FileNotFoundError:
        return [-1.0 for i in range(6)]

def getCosNormalizedValue(x):
    if x == -1:
        return -1.0
    else:
        # normalize cos sin from [-1,1] to [0,1]
        return (math.cos(x*math.pi/180)+1)/2

def getSinNormalizedValue(x):
    if x == -1:
        return -1.0
    else:
        # normalize cos sin from [-1,1] to [0,1]
        return (math.sin(x*math.pi/180)+1)/2


if __name__ == "__main__":
    for station in range(1, STATIONS_TOTAL+1):
        seven_stations = getSelfAndKNNList(station)
        '''
        result_table => 7*11*6 3-dim array to store the result.
        first dimension: # of stations (i.e. self + dtw + ed)
        second dimension: # of features
        third dimension: # of recent 6 hour values we used
        '''
        result_table = np.zeros((7, 11, 6), dtype=float)
        for i, stn_id in enumerate(seven_stations):
            for j, feat in enumerate(FEAT_LIST):
                if feat != 'PASS':
                    recent_six_list = getRecentSixHourValues(stn_id, feat)
                    # 第一個PM2.5為計算PM2.5差值
                    if j == 0:
                        recent_six_list = countDeltaOfPollutionValue(recent_six_list)
                    
                    # 遇到風向資料時，須特殊處理（拆成cos和sin兩個資料）
                    if feat == 'WD_HR' or feat == 'WIND_DIREC':
                        # 轉為cos和sin兩項資料的同時也已完成normalize
                        cos_list = [getCosNormalizedValue(x) for x in recent_six_list]
                        sin_list = [getSinNormalizedValue(x) for x in recent_six_list]
                        result_table[i, j] = np.array(cos_list)
                        result_table[i, j+1] = np.array(sin_list)
                        # 將缺值者由-1改為NaN
                        result_table[i, j:j+2][result_table[i, j:j+2] == -1] = np.nan
                    else:
                        result_table[i, j] = np.array(recent_six_list)
                        # 將缺值者由-1改為NaN後，再進行normalize
                        result_table[i, j][result_table[i, j] == -1] = np.nan
                        result_table[i, j] = result_table[i, j] / FEAT_BASE[j]
                else: continue
        result_table = result_table.reshape((77, 6))
        np.save('{}/{}.npy'.format(RESULT_PATH, station), result_table)
        # print('Current station:', station, '/', STATIONS_TOTAL)

        ### Console test output
        # for i in range(7):
        #     for j in range(11):
        #         print(11*i+j+1, result_table[i, j])
        ###
tEnd = time.time()
print('Elapsed time:', tEnd - tStart, 'sec')
