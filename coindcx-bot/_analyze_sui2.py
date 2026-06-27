import requests, json
import numpy as np
import sys
sys.path.insert(0, '.')
import indicators as ind

PUBLIC = 'https://public.coindcx.com'
BASE = 'https://api.coindcx.com'

# Fetch SUI 4h candles with various limits
for lim in [3, 50, 200]:
    r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '4h', 'limit': lim}, timeout=8)
    d = r.json()
    if d and len(d) > 0:
        closestr = d[-1].get('close', '?')
        timestr = d[-1].get('time', '?')
        print('limit={}: {} candles, latest close={}, time={}'.format(lim, len(d), closestr, timestr))
    else:
        print('limit={}: empty'.format(lim))

# Now use limit=200 and check if data is current
r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '4h', 'limit': 200}, timeout=8)
c4h = r.json()

if c4h and len(c4h) >= 50:
    closes = np.array([float(c['close']) for c in c4h])
    highs = np.array([float(c['high']) for c in c4h])
    lows = np.array([float(c['low']) for c in c4h])
    volumes = np.array([float(c['volume']) for c in c4h])
    
    print('\nLatest candle timestamp: {}'.format(c4h[-1]['time']))
    print('Latest close: {}'.format(c4h[-1]['close']))
    
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
    
    print('\n=== SUI 4H (limit=200) ===')
    print('Price: {:.4f}'.format(price))
    print('EMA20: {:.4f}  EMA50: {:.4f}  EMA200: {:.4f}'.format(ema20[-1], ema50[-1], ema200[-1]))
    print('VWAP: {:.4f}'.format(vwap_arr[-1]))
    print('RSI: {:.1f}'.format(rsi_arr[-1]))
    print('MACD: {:.4f}  Signal: {:.4f}'.format(macd_line[-1], sig_line[-1]))
    print('StochRSI K: {:.1f}  D: {:.1f}'.format(sk[-1], sd[-1]))
    print('K_prev: {:.1f}  D_prev: {:.1f}'.format(sk[-2], sd[-2]))
    print('Patterns: {}'.format(patterns))
    print('d_EMA: {:.2f}%  d_VWAP: {:.2f}%'.format(d_ema, d_vwap))
    
    print('\n=== LONG CHECKS ===')
    chk = [
        ('P > VWAP  ', price > vwap_arr[-1]),
        ('EMA Ord   ', ema20[-1] > ema50[-1] > ema200[-1]),
        ('Pullback  ', d_ema < 3 or d_vwap < 3),
        ('Candle    ', patterns.get('bullish_engulfing', False) or patterns.get('hammer', False) or patterns.get('strong_bull', False)),
        ('RSI > 50  ', rsi_arr[-1] > 50),
        ('MACD Bull ', macd_line[-1] > sig_line[-1]),
        ('Stoch Up  ', sk[-2] < sd[-2] and sk[-1] > sd[-1]),
        ('BTC Neut  ', True),
        ('Vol Up    ', volumes[-1] > vol_sma[-1]),
    ]
    p = 0
    for n, v in chk:
        m = '+' if v else '-'
        if v: p += 1
        print('  [{}] {} {}'.format(m, n, v))
    print('  PASSED: {}/9'.format(p))
    
    print('\n=== SHORT CHECKS ===')
    chk2 = [
        ('P < VWAP  ', price < vwap_arr[-1]),
        ('EMA Ord   ', ema20[-1] < ema50[-1] < ema200[-1]),
        ('Pullback  ', d_ema < 3 or d_vwap < 3),
        ('Candle    ', patterns.get('bearish_engulfing', False) or patterns.get('shooting_star', False) or patterns.get('strong_bear', False)),
        ('RSI < 50  ', rsi_arr[-1] < 50),
        ('MACD Bear ', macd_line[-1] < sig_line[-1]),
        ('Stoch Down', sk[-2] > sd[-2] and sk[-1] < sd[-1]),
        ('BTC Neut  ', True),
        ('Vol Up    ', volumes[-1] > vol_sma[-1]),
    ]
    p2 = 0
    for n2, v2 in chk2:
        m2 = '+' if v2 else '-'
        if v2: p2 += 1
        print('  [{}] {} {}'.format(m2, n2, v2))
    print('  PASSED: {}/9'.format(p2))
else:
    print('Not enough candles: {}'.format(len(c4h) if c4h else 0))
