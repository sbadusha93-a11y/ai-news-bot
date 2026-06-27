import requests, json

BASE = 'https://api.coindcx.com'
PUBLIC = 'https://public.coindcx.com'

for pf in ['B-SUI_USDT', 'SUIUSDT']:
    try:
        r = requests.get(PUBLIC + '/market_data/candles', params={'pair': pf, 'interval': '4h', 'limit': 3}, timeout=8)
        if r.status_code == 200:
            d = r.json()
            if d and len(d) > 0:
                latest = d[-1]
                print('Format {}: {} candles, time={}, close={}'.format(pf, len(d), latest.get('time','?'), latest.get('close','?')))
            else:
                print('Format {}: empty'.format(pf))
        else:
            print('Format {}: status {}'.format(pf, r.status_code))
    except Exception as e:
        print('Format {}: error {}'.format(pf, e))

r = requests.get(BASE + '/exchange/ticker', timeout=8)
for t in r.json():
    if t.get('market') == 'SUIUSDT':
        print('Ticker: {}'.format(json.dumps(t)))
        break
