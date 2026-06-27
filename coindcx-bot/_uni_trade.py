import requests, json
import numpy as np
import sys
sys.path.insert(0, '.')
import indicators as ind
from data_fetcher import to_candle_pair

PUBLIC = 'https://public.coindcx.com'

raw = requests.get(PUBLIC + '/market_data/candles', params={'pair': to_candle_pair('UNIUSDT'), 'interval': '4h', 'limit': 200}, timeout=10).json()
raw_rev = list(reversed(raw))

closes = np.array([float(c['close']) for c in raw_rev])
highs = np.array([float(c['high']) for c in raw_rev])
lows = np.array([float(c['low']) for c in raw_rev])

price = closes[-1]
e20 = ind.ema(closes, 20)[-1]
atr_arr = ind.atr(highs, lows, closes, 14)
atr_val = atr_arr[-1]
high_10_arr = ind.highest(highs, 10)
low_10_arr = ind.lowest(lows, 10)
high_10 = high_10_arr[-1]
low_10 = low_10_arr[-1]

print('UNI 4H TRADE SETUP')
print('==================')
print('Entry:     {:.4f} (current close)'.format(price))
print('Direction: SHORT')
print('ATR:       {:.4f}'.format(atr_val))
print('High_10:   {:.4f}'.format(high_10))
print('Low_10:    {:.4f}'.format(low_10))
print('EMA20:     {:.4f}'.format(e20))
print()

# Bot's SL/Target calculation
sl_distance = max(atr_val * 1.5, price * 0.008)
sl = high_10 + sl_distance
target = price - (sl - price) * 3.0
rr = abs((price - target) / (sl - price))

print('Using bot formula:')
print('  SL distance: max(ATR*1.5, entry*0.008) = max({:.4f}, {:.4f}) = {:.4f}'.format(atr_val*1.5, price*0.008, sl_distance))
print('  SL:    {:.4f} (high_10 {:.4f} + distance {:.4f})'.format(sl, high_10, sl_distance))
print('  TP:    {:.4f}'.format(target))
print('  R:R:   {:.2f}'.format(rr))
print()

# Also show a simpler manual calculation
print('Manual (simpler):')
sl_manual = round(price * 1.02, 4)  # 2% above entry
tp_manual = round(price * 0.94, 4)  # 6% below entry (R:R 3)
rr_manual = round(abs(price - tp_manual) / abs(sl_manual - price), 2)
print('  SL: {:.4f} (2% above)'.format(sl_manual))
print('  TP: {:.4f} (6% below)'.format(tp_manual))
print('  R:R: {:.2f}'.format(rr_manual))
