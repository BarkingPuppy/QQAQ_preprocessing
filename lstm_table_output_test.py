import numpy as np
import sys

RESULT_PATH = './lstm_table'

if __name__ == "__main__":
    station_id = sys.argv[1]
    with open('{}/{}.npy'.format(RESULT_PATH, station_id), 'rb') as f:
        test_data = np.load(f)
        f.close()
    print(test_data)
