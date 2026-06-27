import requests, json
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

# Verify ordering: index 0 = newest
r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '4h', 'limit': 5}, timeout=8)
d = r.json()
for i in range(len(d)):
    dt = datetime.fromtimestamp(int(d[i]['time']) / 1000)
    print('  [{}] time={} close={}'.format(i, dt, d[i]['close']))
print('-> Index 0 is NEWEST, index -1 is OLDEST')
