import requests, json
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

# Fetch top 50 USDT pairs
r = requests.get('https://api.coindcx.com/exchange/ticker', timeout=10)
tickers = r.json()
usdt = [t for t in tickers if t.get('market', '').endswith('USDT')]
usdt.sort(key=lambda x: abs(float(x.get('volume', 0))), reverse=True)
coins = [t['market'].replace('USDT', '') for t in usdt[:50]]

print('Scanning {} coins on 4H...'.format(len(coins)))

hits = []
for coin in coins:
    pair = to_candle_pair(coin + 'USDT')
    try:
        r = requests.get(PUBLIC + '/market_data/candles', params={'pair': pair, 'interval': '4h', 'limit': 200}, timeout=10)
        raw = r.json()
    except:
        continue
    
    if not raw or len(raw) < 200:
        continue
    
    raw_rev = list(reversed(raw))
    
    closes = np.array([float(c['close']) for c in raw_rev])
    highs = np.array([float(c['high']) for c in raw_rev])
    lows = np.array([float(c['low']) for c in raw_rev])
    volumes = np.array([float(c['volume']) for c in raw_rev])
    
    price = closes[-1]
    latest_raw = raw_rev[-1]
    prev_raw = raw_rev[-2]
    
    ema20 = ind.ema(closes, 20)
    ema50 = ind.ema(closes, 50)
    ema200 = ind.ema(closes, 200)
    vwap_arr = ind.vwap(highs, lows, closes, volumes)
    rsi_arr = ind.rsi(closes, 14)
    macd_line, sig_line, macd_hist = ind.macd(closes)
    sk, sd = ind.stoch_rsi(closes)
    vol_sma = ind.volume_sma(volumes, 20)
    
    d_ema = abs(price - ema20[-1]) / ema20[-1] * 100
    d_vwap = abs(price - vwap_arr[-1]) / vwap_arr[-1] * 100
    
    patterns = ind.detect_candle_pattern(
        float(latest_raw['open']), float(latest_raw['high']), float(latest_raw['low']), float(latest_raw['close']),
        float(prev_raw['open']), float(prev_raw['high']), float(prev_raw['low']), float(prev_raw['close']),
    )
    
    long_pass = sum([
        price > vwap_arr[-1],
        ema20[-1] > ema50[-1] > ema200[-1],
        d_ema < 3 or d_vwap < 3,
        patterns.get('bullish_engulfing', False) or patterns.get('hammer', False) or patterns.get('strong_bull', False),
        rsi_arr[-1] > 50,
        macd_line[-1] > sig_line[-1],
        sk[-2] < sd[-2] and sk[-1] > sd[-1],
        True,
        volumes[-1] > vol_sma[-1],
    ])
    
    short_pass = sum([
        price < vwap_arr[-1],
        ema20[-1] < ema50[-1] < ema200[-1],
        d_ema < 3 or d_vwap < 3,
        patterns.get('bearish_engulfing', False) or patterns.get('shooting_star', False) or patterns.get('strong_bear', False),
        rsi_arr[-1] < 50,
        macd_line[-1] < sig_line[-1],
        sk[-2] > sd[-2] and sk[-1] < sd[-1],
        True,
        volumes[-1] > vol_sma[-1],
    ])
    
    if long_pass >= 8 or short_pass >= 8:
        hits.append((coin, long_pass, short_pass, price, rsi_arr[-1], list(patterns.keys())))
        dir_str = 'LONG' if long_pass >= 8 else 'SHORT'
        print('{} PASSES! {} | Price={:.4f} RSI={:.1f} L={}/9 S={}/9 Pat={}'.format(coin, dir_str, price, rsi_arr[-1], long_pass, short_pass, list(patterns.keys())))

if not hits:
    print('No coin passes 8/9 on 4H.')
    
    # Show closest ones
    best = []
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
        
        de = abs(price - e20) / e20 * 100
        dv = abs(price - vwap) / vwap * 100
        pat = ind.detect_candle_pattern(
            float(lt_raw['open']), float(lt_raw['high']), float(lt_raw['low']), float(lt_raw['close']),
            float(pv_raw['open']), float(pv_raw['high']), float(pv_raw['low']), float(pv_raw['close']),
        )
        
        lp = sum([price > vwap, e20 > e50 > e200, de < 3 or dv < 3,
                  pat.get('bullish_engulfing') or pat.get('hammer') or pat.get('strong_bull'),
                  rsi > 50, ml[-1] > ms[-1], stk[-2] < std[-2] and stk[-1] > std[-1], True, vols_arr[-1] > vsma])
        sp = sum([price < vwap, e20 < e50 < e200, de < 3 or dv < 3,
                  pat.get('bearish_engulfing') or pat.get('shooting_star') or pat.get('strong_bear'),
                  rsi < 50, ml[-1] < ms[-1], stk[-2] > std[-2] and stk[-1] < std[-1], True, vols_arr[-1] > vsma])
        
        best.append((max(lp, sp), lp, sp, coin, price, rsi, list(pat.keys())))
    
    best.sort(key=lambda x: x[0], reverse=True)
    print()
    print('Closest on 4H (top 10):')
    for score, lp, sp, coin, price, rsi, pat in best[:10]:
        dir_s = 'LONG' if lp == score else 'SHORT'
        print('  {}: {}/9 {} | Price={:.4f} RSI={:.1f} Pat={}'.format(coin, score, dir_s, price, rsi, pat))
