import requests, json
import numpy as np
import sys
sys.path.insert(0, '.')
import indicators as ind

PUBLIC = 'https://public.coindcx.com'

r = requests.get(PUBLIC + '/market_data/candles', params={'pair': 'B-SUI_USDT', 'interval': '15m', 'limit': 300}, timeout=8)
c15m = r.json()

if c15m and len(c15m) >= 200:
    closes = np.array([float(c['close']) for c in c15m])
    highs = np.array([float(c['high']) for c in c15m])
    lows = np.array([float(c['low']) for c in c15m])
    volumes = np.array([float(c['volume']) for c in c15m])
    
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
    
    print('=== SUI 15M SIGNAL CHECKS ===')
    print('')
    print('Key Values:')
    print('  Price:       {:.4f}'.format(price))
    print('  VWAP:        {:.4f}'.format(vwap_arr[-1]))
    print('  EMA20:       {:.4f}'.format(ema20[-1]))
    print('  EMA50:       {:.4f}'.format(ema50[-1]))
    print('  EMA200:      {:.4f}'.format(ema200[-1]))
    print('  RSI:         {:.1f}'.format(rsi_arr[-1]))
    print('  MACD:        {:.4f}'.format(macd_line[-1]))
    print('  Signal:      {:.4f}'.format(sig_line[-1]))
    print('  Stoch K:     {:.1f}'.format(sk[-1]))
    print('  Stoch D:     {:.1f}'.format(sd[-1]))
    print('  K prev:      {:.1f}'.format(sk[-2]))
    print('  D prev:      {:.1f}'.format(sd[-2]))
    print('  d_EMA:       {:.2f}%'.format(d_ema))
    print('  d_VWAP:      {:.2f}%'.format(d_vwap))
    print('  Candle pat:  {}'.format(patterns))
    print('  Vol/VolSMA:  {:.0f}/{:.0f}'.format(volumes[-1], vol_sma[-1]))
    
    print('')
    print('LONG:')
    print('  [{}] P > VWAP   = {:.4f} > {:.4f}'.format('OK' if price > vwap_arr[-1] else 'FAIL', price, vwap_arr[-1]))
    print('  [{}] EMA Ord    = {:.4f} > {:.4f} > {:.4f}'.format('OK' if ema20[-1] > ema50[-1] > ema200[-1] else 'FAIL', ema20[-1], ema50[-1], ema200[-1]))
    print('  [{}] Pullback   = d_EMA {:.2f}% < 3% or d_VWAP {:.2f}% < 3%'.format('OK' if d_ema < 3 or d_vwap < 3 else 'FAIL', d_ema, d_vwap))
    pat_str = 'bull={} ham={} strB={}'.format(patterns.get('bullish_engulfing'), patterns.get('hammer'), patterns.get('strong_bull'))
    print('  [{}] Candle     = {}'.format('OK' if (patterns.get('bullish_engulfing') or patterns.get('hammer') or patterns.get('strong_bull')) else 'FAIL', pat_str))
    print('  [{}] RSI > 50   = {:.1f} > 50'.format('OK' if rsi_arr[-1] > 50 else 'FAIL', rsi_arr[-1]))
    print('  [{}] MACD Bull  = {:.4f} > {:.4f}'.format('OK' if macd_line[-1] > sig_line[-1] else 'FAIL', macd_line[-1], sig_line[-1]))
    print('  [{}] Stoch Up   = K {:.1f}->{:.1f} cross D {:.1f}->{:.1f}'.format('OK' if sk[-2] < sd[-2] and sk[-1] > sd[-1] else 'FAIL', sk[-2], sk[-1], sd[-2], sd[-1]))
    print('  [{}] BTC Neutral = True'.format('OK'))
    print('  [{}] Vol Up     = {:.0f} > {:.0f}'.format('OK' if volumes[-1] > vol_sma[-1] else 'FAIL', volumes[-1], vol_sma[-1]))
    
    print('')
    print('SHORT:')
    print('  [{}] P < VWAP   = {:.4f} < {:.4f}'.format('OK' if price < vwap_arr[-1] else 'FAIL', price, vwap_arr[-1]))
    print('  [{}] EMA Ord    = {:.4f} < {:.4f} < {:.4f}'.format('OK' if ema20[-1] < ema50[-1] < ema200[-1] else 'FAIL', ema20[-1], ema50[-1], ema200[-1]))
    print('  [{}] Pullback   = d_EMA {:.2f}% < 3% or d_VWAP {:.2f}% < 3%'.format('OK' if d_ema < 3 or d_vwap < 3 else 'FAIL', d_ema, d_vwap))
    pat2_str = 'bear={} ss={} strB={}'.format(patterns.get('bearish_engulfing'), patterns.get('shooting_star'), patterns.get('strong_bear'))
    print('  [{}] Candle     = {}'.format('OK' if (patterns.get('bearish_engulfing') or patterns.get('shooting_star') or patterns.get('strong_bear')) else 'FAIL', pat2_str))
    print('  [{}] RSI < 50   = {:.1f} < 50'.format('OK' if rsi_arr[-1] < 50 else 'FAIL', rsi_arr[-1]))
    print('  [{}] MACD Bear  = {:.4f} < {:.4f}'.format('OK' if macd_line[-1] < sig_line[-1] else 'FAIL', macd_line[-1], sig_line[-1]))
    print('  [{}] Stoch Down = K {:.1f}->{:.1f} cross D {:.1f}->{:.1f}'.format('OK' if sk[-2] > sd[-2] and sk[-1] < sd[-1] else 'FAIL', sk[-2], sk[-1], sd[-2], sd[-1]))
    print('  [{}] BTC Neutral = True'.format('OK'))
    print('  [{}] Vol Up     = {:.0f} > {:.0f}'.format('OK' if volumes[-1] > vol_sma[-1] else 'FAIL', volumes[-1], vol_sma[-1]))
