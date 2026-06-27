import requests, json
import numpy as np
import sys
sys.path.insert(0, '.')
import indicators as ind

PUBLIC = 'https://public.coindcx.com'

# Fetch 15m candles - try different limits
r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '15m', 'limit': 3}, timeout=8)
c15m = r.json()
if c15m and len(c15m) >= 2:
    print('Latest 15m close: {}, time: {}'.format(c15m[-1]['close'], c15m[-1]['time']))
    
r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '15m', 'limit': 1000}, timeout=8)
c15m = r.json()
print('15m candles with limit=1000: {}'.format(len(c15m) if c15m else 0))

if c15m and len(c15m) >= 200:
    closes = np.array([float(c['close']) for c in c15m])
    highs = np.array([float(c['high']) for c in c15m])
    lows = np.array([float(c['low']) for c in c15m])
    volumes = np.array([float(c['volume']) for c in c15m])
    opens = np.array([float(c['open']) for c in c15m])
    
    latest_time = c15m[-1]['time']
    print('Latest 15m close: {}, time: {}'.format(closes[-1], latest_time))
    
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
    
    curr, prev = c15m[-1], c15m[-2]
    patterns = ind.detect_candle_pattern(
        float(curr['open']), float(curr['high']), float(curr['low']), float(curr['close']),
        float(prev['open']), float(prev['high']), float(prev['low']), float(prev['close']),
    )
    
    print('\n=== SUI 15M ANALYSIS ===')
    print('Price: {:.4f}'.format(price))
    print('EMA20: {:.4f}  EMA50: {:.4f}  EMA200: {:.4f}'.format(ema20[-1], ema50[-1], ema200[-1]))
    print('VWAP: {:.4f}'.format(vwap_arr[-1]))
    print('RSI: {:.1f}'.format(rsi_arr[-1]))
    print('MACD: {:.4f}  Signal: {:.4f}'.format(macd_line[-1], sig_line[-1]))
    print('StochRSI K: {:.1f}  D: {:.1f}'.format(sk[-1], sd[-1]))
    print('K_prev: {:.1f}  D_prev: {:.1f}'.format(sk[-2], sd[-2]))
    print('Patterns: {}'.format(patterns))
    print('d_EMA: {:.2f}%  d_VWAP: {:.2f}%'.format(d_ema, d_vwap))
    print('Vol: {:.0f}  VolSMA: {:.0f}'.format(volumes[-1], vol_sma[-1]))
    
    print('\n' + '='*50)
    print('LONG CHECKS (need 8/9)')
    print('='*50)
    chk = [
        ('P > VWAP   ', price > vwap_arr[-1]),
        ('EMA Ord    ', ema20[-1] > ema50[-1] > ema200[-1]),
        ('Pullback   ', d_ema < 3 or d_vwap < 3),
        ('Candle     ', patterns.get('bullish_engulfing', False) or patterns.get('hammer', False) or patterns.get('strong_bull', False)),
        ('RSI > 50   ', rsi_arr[-1] > 50),
        ('MACD Bull  ', macd_line[-1] > sig_line[-1]),
        ('Stoch Up   ', sk[-2] < sd[-2] and sk[-1] > sd[-1]),
        ('BTC Neutral', True),
        ('Vol Up     ', volumes[-1] > vol_sma[-1]),
    ]
    passed = 0
    for n, v in chk:
        sym = '+' if v else '-'
        if v: passed += 1
        print('  [{}] {} -> {}'.format(sym, n, v))
    print('  -> {} / 9 passed'.format(passed))
    if passed >= 8:
        print('  ** WOULD BE LONG SIGNAL **')
    else:
        print('  ** {} more check(s) needed for LONG **'.format(8 - passed))
    
    print('\n' + '='*50)
    print('SHORT CHECKS (need 8/9)')
    print('='*50)
    chk2 = [
        ('P < VWAP   ', price < vwap_arr[-1]),
        ('EMA Ord    ', ema20[-1] < ema50[-1] < ema200[-1]),
        ('Pullback   ', d_ema < 3 or d_vwap < 3),
        ('Candle     ', patterns.get('bearish_engulfing', False) or patterns.get('shooting_star', False) or patterns.get('strong_bear', False)),
        ('RSI < 50   ', rsi_arr[-1] < 50),
        ('MACD Bear  ', macd_line[-1] < sig_line[-1]),
        ('Stoch Down ', sk[-2] > sd[-2] and sk[-1] < sd[-1]),
        ('BTC Neutral', True),
        ('Vol Up     ', volumes[-1] > vol_sma[-1]),
    ]
    passed2 = 0
    for n2, v2 in chk2:
        sym2 = '+' if v2 else '-'
        if v2: passed2 += 1
        print('  [{}] {} -> {}'.format(sym2, n2, v2))
    print('  -> {} / 9 passed'.format(passed2))
    if passed2 >= 8:
        print('  ** WOULD BE SHORT SIGNAL **')
    else:
        print('  ** {} more check(s) needed for SHORT **'.format(8 - passed2))
else:
    print('Not enough 15m data, trying 4h with limit=50...')
    r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '4h', 'limit': 50}, timeout=8)
    c4h = r.json()
    print('4h candles: {}'.format(len(c4h) if c4h else 0))
    if c4h and len(c4h) > 2:
        print('Latest: close={}, time={}'.format(c4h[-1]['close'], c4h[-1]['time']))
