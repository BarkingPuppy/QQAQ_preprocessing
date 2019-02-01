#! python3
# coding: utf-8
import datetime as dt
import json, math, os, time
import numpy as np

RECENT_SIX_PATH = './recent6'
RESULT_PATH = './lstm_table'
KNN_K = 3   # "k" of k-NN
STATIONS_TOTAL = 76
# 註: PM2.5有兩個，一個是PM2.5差值（當前-上一小時），另一個是PM2.5值；
# PASS為預留給風向資料拆成cos和sin的位置，會於迴圈中略過
# FEATURE_LIST = ['AMB_TEMP', 'PM10', 'PM2.5', 'RH', 'WIND_DIREC', 'PASS', 'WIND_SPEED', 'WD_HR', 'PASS', 'WS_HR', 'PM2.5_delta']
FEATURE_LIST = ['AMB_TEMP', 'PM10', 'PM2.5', 'RH', 'WIND_SPEED', 'WS_HR', 'WIND_DIREC', 'PASS', 'WD_HR', 'PASS', 'PM2.5_delta']
FEATURE_BASE = {
    'PM2.5': 500,
    'PM2.5_delta': 500,
    'PM10': 500,
    'WS_HR': 30,
    'WD_HR': 1,
    'WIND_SPEED': 30,
    'WIND_DIREC': 1,
    'AMB_TEMP': 50,
    'RH': 100,
    'PASS': 1
}

with open('./knn_dtw.json', 'r') as f:
    knn_dtw_data = json.load(f)
    f.close()
with open('./knn_ed.json', 'r') as f:
    knn_ed_data = json.load(f)
    f.close()
current_time = dt.datetime.utcnow() + dt.timedelta(hours=8)

def getDeltaOfPollutionValue(station_id):
    try:
        file_path = '{}/{}/{}.json'.format(RECENT_SIX_PATH, 'PM2.5', station_id)
        with open(file_path, 'r') as f:
            data = json.load(f)
            recent_seven_list = [datum['hr_v'] for datum in data[-7:]]
            for i, val in enumerate(recent_seven_list):
                if i == 0 and val < 0:
                    recent_seven_list[i] = 0
                if i < len(recent_seven_list) - 1 and recent_seven_list[i+1] < 0:
                    recent_seven_list[i+1] = recent_seven_list[i]
                recent_seven_list[i] = float(val)
            delta_list = np.zeros(6, dtype=float)
            for i in range(delta_list.size):
                delta_list[i] = recent_seven_list[i+1] - recent_seven_list[i]
            f.close()
    except FileNotFoundError:
        delta_list = np.zeros(6, dtype=float)
    finally:
        return delta_list

def getSelfAndKNNList(station_id):
    station_list = [station_id]
    for i in range(KNN_K):
        station_list.append(int(knn_dtw_data[str(station_id)][i]))
        station_list.append(int(knn_ed_data[str(station_id)][i]))
    return station_list

def getRecentSixHourValues(station_id, feature):
    try:
        file_path = '{}/{}/{}.json'.format(RECENT_SIX_PATH, feature, station_id)
        with open(file_path, 'r') as f:
            data = json.load(f)
            recent_six_list = [datum['hr_v'] for datum in data[-6:]]
            for i, val in enumerate(recent_six_list):
                if i == 0 and val < 0:
                    recent_six2twelve = [datum['hr_v'] for datum in data[-7:-13:-1]]
                    for substitute in recent_six2twelve:
                        if substitute >= 0:
                            recent_six_list[i] = substitute
                            break
                    else:
                        recent_six_list[i] = -1
                if i < len(recent_six_list) - 1 and recent_six_list[i+1] < 0:
                    recent_six_list[i+1] = recent_six_list[i]
                recent_six_list[i] = float(val)
            f.close()
        return np.array(recent_six_list, dtype=float)
    except FileNotFoundError:
        return np.zeros(6, dtype=float)-1

def getCosSinNormalizedValues(recent_six_list):
    cos_list = np.zeros(6, dtype=float)
    sin_list = np.zeros(6, dtype=float)
    for i, val in enumerate(recent_six_list):
        if val < 0:
            cos_list[i] = 0
            sin_list[i] = 0
        else:
            # normalize cos sin from [-1,1] to [0,1]
            cos_list[i] = math.cos(val * math.pi / 180)
            sin_list[i] = math.sin(val * math.pi / 180)
            # cos_list[i] = (math.cos(val*math.pi/180)+1)/2
            # sin_list[i] = (math.sin(val*math.pi/180)+1)/2
    return cos_list, sin_list


if __name__ == "__main__":

    t_start = time.time()
    print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
    print('Time:', current_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('Stations:', end=' ')
    station_recent_six_table = np.zeros((STATIONS_TOTAL, 11, 6), dtype=float)
    for station_idx in range(STATIONS_TOTAL):
        station_id = station_idx + 1
        print(station_id, end=' ')
        for feat_idx, feat in enumerate(FEATURE_LIST):
            if feat == 'PASS':
                continue
            # 第一個PM2.5為計算PM2.5差值            
            elif feat == 'PM2.5_delta':
                recent_six_list = getDeltaOfPollutionValue(station_id)
                station_recent_six_table[station_idx, feat_idx] = recent_six_list
            # 遇到風向資料時，須特殊處理（拆成cos和sin兩個資料）
            elif feat == 'WD_HR' or feat == 'WIND_DIREC':
                recent_six_list = getRecentSixHourValues(station_id, feat)
                cos_list, sin_list = getCosSinNormalizedValues(recent_six_list)
                station_recent_six_table[station_idx, feat_idx] = cos_list
                station_recent_six_table[station_idx, feat_idx+1] = sin_list
            else:
                recent_six_list = getRecentSixHourValues(station_id, feat)
                # 將缺值者由-1改為0
                recent_six_list[recent_six_list == -1] = 0
                station_recent_six_table[station_idx, feat_idx] = recent_six_list
            station_recent_six_table[station_idx, feat_idx] = station_recent_six_table[station_idx, feat_idx] / FEATURE_BASE[feat]

    if not os.path.isdir(RESULT_PATH):
        os.mkdir(RESULT_PATH)
    for station_idx in range(STATIONS_TOTAL):
        station_id = station_idx + 1
        seven_near_stations = getSelfAndKNNList(station_id)
        '''
        result_table => 7*11*6 3-dim array to store the result.
        First dimension: # of stations (i.e. self + dtw + ed)
        second dimension: # of features
        third dimension: # of recent 6 hour values we used
        '''
        result_table = np.zeros((7, 11, 6), dtype=float)
        for i, near_stn_id in enumerate(seven_near_stations):
            result_table[i] = station_recent_six_table[near_stn_id - 1]
        np.save('{}/{}.npy'.format(RESULT_PATH, station_id), result_table.reshape(7*11, 6))
        
t_end = time.time()
print('\nElapsed time:', t_end - t_start, 'sec')
