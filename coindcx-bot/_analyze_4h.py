import requests, json
import numpy as np
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

coins = ['ONDO', 'ZEC', 'UNI', 'XRP', 'LINK', 'ENA', 'SUI', 'NEAR', 'WLD', 'PEPE']

for coin in coins:
    pair = to_candle_pair(coin + 'USDT')
    try:
        r = requests.get(PUBLIC + '/market_data/candles', params={'pair': pair, 'interval': '4h', 'limit': 200}, timeout=8)
        c4h = r.json()
    except:
        print('{}: API error'.format(coin))
        continue

    if not c4h or len(c4h) < 200:
        print('{}: not enough data ({})'.format(coin, len(c4h) if c4h else 0))
        continue

    closes = np.array([float(c['close']) for c in c4h])
    highs = np.array([float(c['high']) for c in c4h])
    lows = np.array([float(c['low']) for c in c4h])
    volumes = np.array([float(c['volume']) for c in c4h])

    ema20 = ind.ema(closes, 20)
    ema50 = ind.ema(closes, 50)
    ema200 = ind.ema(closes, 200)
    vwap_arr = ind.vwap(highs, lows, closes, volumes)
    rsi_arr = ind.rsi(closes, 14)
    macd_line, sig_line, macd_hist = ind.macd(closes)
    sk, sd = ind.stoch_rsi(closes)
    vol_sma = ind.volume_sma(volumes, 20)

    price = closes[-1]
    d_ema = abs(price - ema20[-1]) / ema20[-1] * 100
    d_vwap = abs(price - vwap_arr[-1]) / vwap_arr[-1] * 100

    curr, prev = c4h[-1], c4h[-2]
    patterns = ind.detect_candle_pattern(
        float(curr['open']), float(curr['high']), float(curr['low']), float(curr['close']),
        float(prev['open']), float(prev['high']), float(prev['low']), float(prev['close']),
    )

    # LONG checks
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

    # SHORT checks
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

    dir_str = ''
    if long_pass >= 8 and short_pass >= 8:
        dir_str = 'BOTH'
    elif long_pass >= 8:
        dir_str = 'LONG'
    elif short_pass >= 8:
        dir_str = 'SHORT'
    else:
        dir_str = 'NONE'

    if dir_str != 'NONE' or coin in ['ONDO', 'ZEC', 'UNI', 'XRP', 'SUI', 'NEAR', 'WLD']:
        print('')
        print('{}  | Price: {:.4f} | RSI: {:.1f} | L: {}/9  S: {}/9 | Dir: {} {}'.format(coin, price, rsi_arr[-1], long_pass, short_pass, dir_str, patterns))
        print('  LONG:  P>VWAP={}, EMA={}, Pull={}, Cdl={}, RSI>50={}, MACD={}, Stoch={}, BTC={}, Vol={}'.format(*long_checks))
        print('  SHORT: P<VWAP={}, EMA={}, Pull={}, Cdl={}, RSI<50={}, MACD={}, Stoch={}, BTC={}, Vol={}'.format(*short_checks))
