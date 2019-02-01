#! python3
# coding: utf-8
import datetime as dt
import json, math, os, time
import numpy as np

RECENT_SIX_PATH = './recent6'
STATIONS_TOTAL = 76
RESULT_PATH = './dtw_table'
PM2P5_BASE = 500
current_time = dt.datetime.utcnow() + dt.timedelta(hours=8)


if __name__ == "__main__":
    t_start = time.time()
    print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
    print('Time:', current_time.strftime('%Y-%m-%d %H:%M:%S'))

    result_table = np.zeros(STATIONS_TOTAL)
    try:
        for idx in range(STATIONS_TOTAL):
            station_id = idx + 1
            file_path = '{}/{}/{}.json'.format(RECENT_SIX_PATH, 'PM2.5', station_id)
            with open(file_path, 'r') as f:
                data = json.load(f)
                for datum in reversed(data):
                    if datum['hr_v'] >= 0:
                        recent_value = datum['hr_v']
                        break
                result_table[idx] = recent_value
                f.close()
        print('Success.')
    except Exception as e:
        print('Exception type: {}, exception message: {}'.format(type(e).__name__, e))
    finally:
        if not os.path.isdir(RESULT_PATH):
            os.mkdir(RESULT_PATH)
        result_table = result_table / PM2P5_BASE
        np.save('{}/dtw_table.npy'.format(RESULT_PATH), result_table)
        t_end = time.time()
        print('Elapsed time:', t_end - t_start, 'sec')
        


