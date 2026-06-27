import requests
PUBLIC = 'https://public.coindcx.com'

for coin in ['SUI', 'NEAR', 'BTC']:
    pair = 'B-' + coin + '_USDT'
    r = requests.get(PUBLIC + '/market_data/candles', params={'pair': pair, 'interval': '4h', 'limit': 3}, timeout=8)
    d = r.json()
    if d and len(d) > 0:
        t = int(d[-1]['time'])
        from datetime import datetime
        dt = datetime.utcfromtimestamp(t / 1000)
        print('{} latest: close={}, time={} UTC'.format(coin, d[-1]['close'], dt))
