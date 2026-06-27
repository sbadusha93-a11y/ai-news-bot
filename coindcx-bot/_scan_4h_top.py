import requests, json
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

r = requests.get('https://api.coindcx.com/exchange/ticker', timeout=10)
tickers = r.json()
usdt = [t for t in tickers if t.get('market', '').endswith('USDT')]
usdt.sort(key=lambda x: abs(float(x.get('volume', 0))), reverse=True)
coins = [t['market'].replace('USDT', '') for t in usdt[:50]]

print('Closest to 8/9 on 4H:')
results = []
for coin in coins:
    pair = to_candle_pair(coin + 'USDT')
    try:
        raw = requests.get(PUBLIC + '/market_data/candles', params={'pair': pair, 'interval': '4h', 'limit': 200}, timeout=10).json()
    except:
        continue
    if not raw or len(raw) < 200:
        continue
    raw_rev = list(reversed(raw))
    closes_arr = np.array([float(c['close']) for c in raw_rev])
    highs_arr = np.array([float(c['high']) for c in raw_rev])
    lows_arr = np.array([float(c['low']) for c in raw_rev])
    vols_arr = np.array([float(c['volume']) for c in raw_rev])
    price = closes_arr[-1]
    lt_raw = raw_rev[-1]
    pv_raw = raw_rev[-2]
    
    e20 = ind.ema(closes_arr, 20)[-1]
    e50 = ind.ema(closes_arr, 50)[-1]
    e200 = ind.ema(closes_arr, 200)[-1]
    vwap = ind.vwap(highs_arr, lows_arr, closes_arr, vols_arr)[-1]
    rsi = ind.rsi(closes_arr, 14)[-1]
    ml, ms, mh = ind.macd(closes_arr)
    stk, std = ind.stoch_rsi(closes_arr)
    vsma = ind.volume_sma(vols_arr, 20)[-1]
    vol = vols_arr[-1]
    
    de = abs(price - e20) / e20 * 100
    dv = abs(price - vwap) / vwap * 100
    pat = ind.detect_candle_pattern(
        float(lt_raw['open']), float(lt_raw['high']), float(lt_raw['low']), float(lt_raw['close']),
        float(pv_raw['open']), float(pv_raw['high']), float(pv_raw['low']), float(pv_raw['close']),
    )
    
    mlv = float(ml[-1]) if ml is not None else 0
    msv = float(ms[-1]) if ms is not None else 0
    stk_v = float(stk[-1]) if stk is not None else 0
    std_v = float(std[-1]) if std is not None else 0
    stk2 = float(stk[-2]) if stk is not None and len(stk) > 1 else 0
    std2 = float(std[-2]) if std is not None and len(std) > 1 else 0
    
    lp = sum([price > vwap, e20 > e50 > e200, de < 3 or dv < 3,
              bool(pat.get('bullish_engulfing') or pat.get('hammer') or pat.get('strong_bull')),
              rsi > 50, mlv > msv, stk2 < std2 and stk_v > std_v, True, vol > vsma])
    sp = sum([price < vwap, e20 < e50 < e200, de < 3 or dv < 3,
              bool(pat.get('bearish_engulfing') or pat.get('shooting_star') or pat.get('strong_bear')),
              rsi < 50, mlv < msv, stk2 > std2 and stk_v < std_v, True, vol > vsma])
    
    results.append((max(lp, sp), lp, sp, coin, price, rsi, list(pat.keys())))

results.sort(key=lambda x: x[0], reverse=True)
for score, lp, sp, coin, price, rsi, pat in results[:15]:
    dir_s = 'LONG' if lp >= sp else 'SHORT'
    print('  {:6s} | {}/9 {} | Price={:.4f} RSI={:.1f} Pat={}'.format(coin, score, dir_s, price, rsi, pat))
