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
volumes = np.array([float(c['volume']) for c in raw_rev])
price = closes[-1]
lt = raw_rev[-1]; pv = raw_rev[-2]

e20 = ind.ema(closes, 20)[-1]; e50 = ind.ema(closes, 50)[-1]; e200 = ind.ema(closes, 200)[-1]
vwap = ind.vwap(highs, lows, closes, volumes)[-1]
rsi = ind.rsi(closes, 14)[-1]
ml, ms, mh = ind.macd(closes)
stk, std = ind.stoch_rsi(closes)
vsma = ind.volume_sma(volumes, 20)[-1]
de = abs(price - e20) / e20 * 100; dv = abs(price - vwap) / vwap * 100
pat = ind.detect_candle_pattern(
    float(lt['open']), float(lt['high']), float(lt['low']), float(lt['close']),
    float(pv['open']), float(pv['high']), float(pv['low']), float(pv['close']),
)

print('UNI 4H - 7/9 SHORT (needs 8)')
print('Price={:.4f} RSI={:.1f} EMA20={:.4f} EMA50={:.4f} EMA200={:.4f} VWAP={:.4f}'.format(price, rsi, e20, e50, e200, vwap))
print('MACD={:.4f} Signal={:.4f} StochK={:.1f} StochD={:.1f} K_prev={:.1f} D_prev={:.1f}'.format(ml[-1], ms[-1], stk[-1], std[-1], stk[-2], std[-2]))
print('Vol={:.0f} VolSMA={:.0f} d_EMA={:.2f}% d_VWAP={:.2f}%'.format(volumes[-1], vsma, de, dv))
print('Pattern: {}'.format(pat))
print()
print('SHORT checks:')
checks = [
    ('P < VWAP   ', price < vwap),
    ('EMA Ord    ', e20 < e50 < e200),
    ('Pullback   ', de < 3 or dv < 3),
    ('Candle     ', pat.get('bearish_engulfing') or pat.get('shooting_star') or pat.get('strong_bear')),
    ('RSI < 50   ', rsi < 50),
    ('MACD Bear  ', ml[-1] < ms[-1]),
    ('Stoch Down ', stk[-2] > std[-2] and stk[-1] < std[-1]),
    ('BTC Neutral', True),
    ('Vol Up     ', volumes[-1] > vsma),
]
for nm, vl in checks:
    print('  [{}] {}'.format('+' if vl else '-', nm))
