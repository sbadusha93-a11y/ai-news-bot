import requests
PUBLIC = 'https://public.coindcx.com'

for lim in [3, 50, 100, 150, 200]:
    r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '4h', 'limit': lim}, timeout=8)
    d = r.json()
    if d and len(d) > 0:
        from datetime import datetime
        t_start = int(d[0]['time'])
        t_end = int(d[-1]['time'])
        dt_start = datetime.fromtimestamp(t_start / 1000)
        dt_end = datetime.fromtimestamp(t_end / 1000)
        print('limit={}: {} candles, {} to {} UTC, close={}'.format(lim, len(d), dt_start, dt_end, d[-1]['close']))
