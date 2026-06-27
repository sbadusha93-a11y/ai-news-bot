import requests, json
import numpy as np
from datetime import datetime
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

coins = ['ONDO', 'ZEC', 'UNI', 'XRP', 'LINK', 'ENA', 'SUI', 'NEAR', 'WLD', 'PEPE', 'ADA', 'AAVE', 'BNB', 'BTC', 'SOL', 'ETH', 'TRX', 'FET', 'DOGE']

for coin in coins:
    pair = to_candle_pair(coin + 'USDT')
    try:
        r = requests.get(PUBLIC + '/market_data/candles', params={'pair': pair, 'interval': '4h', 'limit': 200}, timeout=10)
        raw = r.json()
    except:
        continue
    
    if not raw or len(raw) < 200:
        continue
    
    # raw[0] is newest, raw[-1] is oldest
    # Reverse to oldest-first for indicator computation
    raw_rev = list(reversed(raw))
    
    closes = np.array([float(c['close']) for c in raw_rev])
    highs = np.array([float(c['high']) for c in raw_rev])
    lows = np.array([float(c['low']) for c in raw_rev])
    volumes = np.array([float(c['volume']) for c in raw_rev])
    
    # Latest values (last in reversed array)
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
    
    long_checks = [
        price > vwap_arr[-1],
        ema20[-1] > ema50[-1] > ema200[-1],
        d_ema < 3 or d_vwap < 3,
        patterns.get('bullish_engulfing', False) or patterns.get('hammer', False) or patterns.get('strong_bull', False),
        rsi_arr[-1] > 50,
        macd_line[-1] > sig_line[-1],
        sk[-2] < sd[-2] and sk[-1] > sd[-1],
        True,
        volumes[-1] > vol_sma[-1],
    ]
    long_pass = sum(1 for v in long_checks if v)
    
    short_checks = [
        price < vwap_arr[-1],
        ema20[-1] < ema50[-1] < ema200[-1],
        d_ema < 3 or d_vwap < 3,
        patterns.get('bearish_engulfing', False) or patterns.get('shooting_star', False) or patterns.get('strong_bear', False),
        rsi_arr[-1] < 50,
        macd_line[-1] < sig_line[-1],
        sk[-2] > sd[-2] and sk[-1] < sd[-1],
        True,
        volumes[-1] > vol_sma[-1],
    ]
    short_pass = sum(1 for v in short_checks if v)
    
    if long_pass >= 8 or short_pass >= 8 or coin in ['ONDO', 'SUI', 'NEAR', 'ZEC', 'UNI', 'XRP']:
        dir_str = 'LONG' if long_pass >= 8 else ('SHORT' if short_pass >= 8 else 'NONE')
        ts = datetime.fromtimestamp(int(latest_raw['time']) / 1000)
        print('{:6s} | {:.4f} | RSI={:.1f} | EMAs={:.4f}/{:.4f}/{:.4f} | L={}/9 S={}/9 | Dir={} | Pat={} | {} UTC'.format(
            coin, price, rsi_arr[-1], ema20[-1], ema50[-1], ema200[-1], long_pass, short_pass, dir_str, 
            list(patterns.keys()), ts.strftime('%H:%M')))
        print('  LONG> {}'.format(' '.join(['+' if v else '-' for v in long_checks])))
        print('  SHRT> {}'.format(' '.join(['+' if v else '-' for v in short_checks])))
