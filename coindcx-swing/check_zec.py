import json
with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-swing\signals2.json') as f:
    d = json.load(f)
for r in d.get('rows', []):
    if r['coin'] == 'ZEC':
        print('ZEC:')
        for k, v in r.items():
            print(f'  {k}: {v}')
        print(f'  btc_trend: {d["stats"]["btc_trend"]}')
