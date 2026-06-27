import sys
sys.path.insert(0, 'coindcx-bot')
import indicators as ind
import numpy as np

from data_fetcher import get_candles, to_candle_pair
pair = to_candle_pair('SUIUSDT')
c4h = get_candles(pair, '4h', 500)

if not c4h or len(c4h) < 200:
    print('Not enough candle data')
    exit()

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

i = -1
price = closes[i]
print(f'=== SUI 4H ANALYSIS ===')
print(f'Price: {price:.4f}')
print(f'EMA20: {ema20[i]:.4f}  EMA50: {ema50[i]:.4f}  EMA200: {ema200[i]:.4f}')
print(f'VWAP: {vwap_arr[i]:.4f}')
print(f'RSI: {rsi_arr[i]:.1f}')
print(f'MACD: {macd_line[i]:.4f}  Signal: {sig_line[i]:.4f}')
print(f'StochRSI K: {sk[i]:.1f}  D: {sd[i]:.1f}')
print(f'StochRSI K_prev: {sk[i-1]:.1f}  D_prev: {sd[i-1]:.1f}')

curr = c4h[-1]
prev = c4h[-2]
patterns = ind.detect_candle_pattern(
    float(curr['open']), float(curr['high']), float(curr['low']), float(curr['close']),
    float(prev['open']), float(prev['high']), float(prev['low']), float(prev['close']),
)
print(f'Candle patterns: {patterns}')

d_ema = abs(price - ema20[i]) / ema20[i] * 100
d_vwap = abs(price - vwap_arr[i]) / vwap_arr[i] * 100
print(f'Pullback: d_EMA={d_ema:.2f}%  d_VWAP={d_vwap:.2f}%')

print()
print('=== LONG CHECKS (need 8/9) ===')
lchecks = [
    ('P > VWAP  ', price > vwap_arr[i]),
    ('EMA Ord   ', ema20[i] > ema50[i] > ema200[i]),
    ('Pullback  ', d_ema < 3 or d_vwap < 3),
    ('Candle    ', patterns.get('bullish_engulfing', False) or patterns.get('hammer', False) or patterns.get('strong_bull', False)),
    ('RSI > 50  ', rsi_arr[i] > 50),
    ('MACD Bull ', macd_line[i] > sig_line[i]),
    ('Stoch Up  ', sk[i-1] < sd[i-1] and sk[i] > sd[i]),
    ('BTC Neut  ', True),
    ('Vol Up    ', volumes[i] > vol_sma[i]),
]
lp = 0
for nm, vl in lchecks:
    m = '+' if vl else '-'
    if vl: lp += 1
    print(f'  [{m}] {nm} {vl}')
print(f'  PASSED: {lp}/9')

print()
print('=== SHORT CHECKS (need 8/9) ===')
schecks = [
    ('P < VWAP  ', price < vwap_arr[i]),
    ('EMA Ord   ', ema20[i] < ema50[i] < ema200[i]),
    ('Pullback  ', d_ema < 3 or d_vwap < 3),
    ('Candle    ', patterns.get('bearish_engulfing', False) or patterns.get('shooting_star', False) or patterns.get('strong_bear', False)),
    ('RSI < 50  ', rsi_arr[i] < 50),
    ('MACD Bear ', macd_line[i] < sig_line[i]),
    ('Stoch Down', sk[i-1] > sd[i-1] and sk[i] < sd[i]),
    ('BTC Neut  ', True),
    ('Vol Up    ', volumes[i] > vol_sma[i]),
]
sp = 0
for nm2, vl2 in schecks:
    m2 = '+' if vl2 else '-'
    if vl2: sp += 1
    print(f'  [{m2}] {nm2} {vl2}')
print(f'  PASSED: {sp}/9')
