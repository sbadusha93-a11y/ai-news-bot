import json
import threading
import numpy as np
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


_data = {}
_live_prices = {}
_host = "127.0.0.1"
_port = 8081

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>4H Swing Scanner</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif; background:#0d1117; color:#c9d1d9; padding:20px; }
.header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px; }
.header h1 { color:#58a6ff; font-size:20px; }
.live-badge { background:#f85149; color:#fff; font-size:10px; padding:2px 8px; border-radius:10px; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%{opacity:1} 50%{opacity:0.4} 100%{opacity:1} }
.stats { display:flex; gap:12px; flex-wrap:wrap; }
.stat { background:#161b22; padding:6px 12px; border-radius:6px; font-size:12px; border:1px solid #30363d; }
.stat span { color:#8b949e; }
.stat .val { color:#f0f6fc; font-weight:600; }
.bull { color:#3fb950 !important; }
.bear { color:#f85149 !important; }
.neutral { color:#d29922 !important; }
table { width:100%; border-collapse:collapse; background:#161b22; border-radius:8px; overflow:hidden; font-size:12px; margin-bottom:12px; }
th { background:#1c2128; color:#8b949e; padding:8px 6px; text-align:left; font-weight:600; white-space:nowrap; border-bottom:1px solid #30363d; position:sticky; top:0; }
td { padding:6px; border-bottom:1px solid #21262d; white-space:nowrap; }
tr:hover { background:#1c2128; }
tr.signal-long { background:rgba(63,185,80,0.08); }
tr.signal-short { background:rgba(248,81,69,0.08); }
tr.exited { opacity:0.5; }
.coin { color:#58a6ff; font-weight:600; }
.dir { text-align:center; font-weight:700; font-size:11px; }
.dir.LONG { color:#3fb950; }
.dir.SHORT { color:#f85149; }
.dir.NONE { color:#8b949e; }
.num { font-family:'JetBrains Mono','Consolas',monospace; text-align:left; }
.price-up { color:#3fb950; }
.price-down { color:#f85149; }
.price-same { color:#f0f6fc; }
.pnl-pos { color:#3fb950; }
.pnl-neg { color:#f85149; }
.check-y { color:#3fb950; font-weight:600; }
.check-n { color:#484f58; }
.loading { text-align:center; padding:40px; color:#484f58; }
.error { color:#f85149; }
.footer { margin-top:10px; text-align:center; color:#484f58; font-size:11px; }
@media (max-width:768px) {
  .header { flex-direction:column; align-items:flex-start; }
  table { font-size:10px; }
  th, td { padding:4px 3px; }
}
</style>
</head>
<body>
<div class="header">
  <h1>4H Swing Scanner <span class="live-badge">LIVE</span></h1>
  <div class="stats" id="stats"></div>
</div>
<div id="content"><div class="loading">Loading data...</div></div>
<div class="footer">4H swing signals &middot; Updates every 60s</div>
<script>
let prevPrices={};
async function load(){try{
  const r=await fetch('/data');
  if(!r.ok) throw new Error('HTTP '+r.status);
  const d=await r.json();
  if(!d||!d.rows){document.getElementById('content').innerHTML='<div class="error">No data</div>';return}
  const rows=d.rows||[], st=d.stats||{}, ts=d.timestamp||'', lp=d.live_prices||{};
  document.getElementById('stats').innerHTML=
    '<div class="stat"><span>BTC:</span> <span class="val '+st.btc_trend+'">'+st.btc_trend?.toUpperCase()+'</span></div>'+
    '<div class="stat"><span>Candle:</span> <span class="val">'+(st.next_candle||'-')+'</span></div>'+
    '<div class="stat"><span>Pairs:</span> <span class="val">'+rows.length+'</span></div>'+
    '<div class="stat"><span>Signals:</span> <span class="val">'+(st.signals||0)+'</span></div>'+
    '<div class="stat"><span>'+ts+'</span></div>';
  renderTable(rows, lp);
}catch(e){document.getElementById('content').innerHTML='<div class="error">Error: '+e.message+'</div>'}}

function renderTable(rows, lp){
  if(!rows.length){document.getElementById('content').innerHTML='<div class="loading">Waiting for data...</div>';return}
  let html='<table><thead><tr>'+
    '<th>Coin</th><th>Price</th><th>Dir</th><th>RSI</th><th>MACD</th><th>EMA Ord</th><th>StochK</th><th>StochD</th><th>Entry</th><th>TP</th><th>SL</th>'+
    '<th>R:R</th><th>Lev</th><th>L%</th><th>S%</th><th>PnL</th><th>S/F</th><th>WR%</th><th>Fund</th><th>Model</th>'+
    '</tr></thead><tbody>';
  for(const r of rows){
    const hasSignal=r.direction==='LONG'||r.direction==='SHORT';
    const cls=hasSignal?(r.direction==='LONG'?'signal-long':'signal-short'):'';
    const dirCls='dir '+r.direction;
    const liveP=lp[r.coin];
    const price=liveP!=null?liveP:r.price;
    const prevP=prevPrices[r.coin];
    let pCls='price-same';
    if(prevP!=null&&liveP!=null){pCls=liveP>prevP?'price-up':liveP<prevP?'price-down':'price-same'}
    prevPrices[r.coin]=liveP!=null?liveP:r.price;
    const exitHtml=r.exit_reasons&&r.exit_reasons.length?' <span style="color:#d29922;font-size:9px">EXIT:'+r.exit_reasons.join(',')+'</span>':'';
    const entryText=r.entry?fmtPrice8(r.entry):'-';
    const tpText=r.target?fmtPrice8(r.target):'-';
    const slText=r.sl?fmtPrice8(r.sl):'-';
    const rrText=r.rr&&r.rr>0?r.rr.toFixed(2):'-';
    const pnlText=r.pnl!=null?(r.pnl>=0?'+':'')+r.pnl.toFixed(2)+'%':'-';
    const pnlCls=r.pnl!=null?(r.pnl>=0?'pnl-pos':'pnl-neg'):'';
    const sfText=r.success+r.failed>0?r.success+'/'+r.failed:'-';
    const wrText=r.win_rate>0?r.win_rate+'%':'-';
    const fundScore=r.fund_score!=null?r.fund_score+'%':'-';
    const modelScore=r.model_score!=null?r.model_score+'%':'-';
    const dirText=r.direction||'-';
    const lpText=r.long_pct!=null?r.long_pct+'%':'-';
    const spText=r.short_pct!=null?r.short_pct+'%':'-';
    const rsiText=r.rsi!=null?r.rsi.toFixed(1):'-';
    const macdText=r.macd||'-';
    const macdCls=r.macd==='POS'?'pnl-pos':r.macd==='NEG'?'pnl-neg':'';
    const emaOrdText=r.ema_order||'-';
    const skText=r.stoch_k!=null?r.stoch_k.toFixed(1):'-';
    const sdText=r.stoch_d!=null?r.stoch_d.toFixed(1):'-';
    html+='<tr class="'+cls+'">'+
      '<td class="coin">'+r.coin+exitHtml+'</td>'+
      '<td class="num '+pCls+'">'+fmtPrice(price)+'</td>'+
      '<td class="'+dirCls+'">'+dirText+'</td>'+
      '<td class="num">'+rsiText+'</td>'+
      '<td class="num '+macdCls+'">'+macdText+'</td>'+
      '<td style="text-align:center">'+emaOrdText+'</td>'+
      '<td class="num">'+skText+'</td>'+
      '<td class="num">'+sdText+'</td>'+
      '<td class="num">'+entryText+'</td>'+
      '<td class="num">'+tpText+'</td>'+
      '<td class="num">'+slText+'</td>'+
      '<td class="num">'+rrText+'</td>'+
      '<td style="text-align:center">'+(r.leverage||'-')+'</td>'+
      '<td class="num">'+lpText+'</td>'+
      '<td class="num">'+spText+'</td>'+
      '<td class="num '+pnlCls+'">'+pnlText+'</td>'+
      '<td style="text-align:center">'+sfText+'</td>'+
      '<td class="num">'+wrText+'</td>'+
      '<td class="num" style="font-weight:600">'+fundScore+'</td>'+
      '<td class="num" style="font-weight:600;color:#c678dd">'+modelScore+'</td>'+
    '</tr>';
  }
  html+='</tbody></table>';
  document.getElementById('content').innerHTML=html;
}

function fmtPrice(p){if(p>=100)return p.toFixed(2);if(p>=10)return p.toFixed(3);if(p>=1)return p.toFixed(4);if(p>=0.01)return p.toFixed(5);return p.toFixed(6)}
function fmtPrice8(p){if(p>=100)return p.toFixed(2);if(p>=10)return p.toFixed(3);if(p>=1)return p.toFixed(4);if(p>=0.01)return p.toFixed(5);return p.toFixed(6)}
load();setInterval(load,1000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/data":
            data = {**_data, "live_prices": dict(_live_prices)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(data, cls=_NumpyEncoder).encode())
        elif path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


def update_data(rows, btc_trend, candle_str):
    global _data
    stats = {
        "btc_trend": btc_trend.lower() if btc_trend else "neutral",
        "next_candle": candle_str or "-",
        "signals": sum(1 for r in rows if r.get("direction") in ("LONG", "SHORT")),
    }
    _data = {
        "rows": rows,
        "stats": stats,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }


def update_live_prices(prices):
    global _live_prices
    _live_prices.update(prices)


def start():
    server = HTTPServer((_host, _port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
