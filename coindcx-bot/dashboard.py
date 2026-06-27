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
_host = "0.0.0.0"
_port = 8081

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>1H-15M Scanner</title>
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
.mode-off { color:#8b949e; }
.mode-paper { color:#d29922; }
.mode-live { color:#f85149; }
.trade-section { margin-top:14px; background:#161b22; border-radius:8px; padding:10px; border:1px solid #30363d; }
.trade-section h3 { color:#8b949e; font-size:12px; margin-bottom:6px; }
.trade-table { font-size:10px; }
.trade-table td { padding:3px 4px; }
.pnl-pos { color:#3fb950; }
.pnl-neg { color:#f85149; }
table { width:100%; border-collapse:collapse; background:#161b22; border-radius:8px; overflow:hidden; font-size:12px; margin-bottom:12px; }
th { background:#1c2128; color:#8b949e; padding:8px 6px; text-align:left; font-weight:600; white-space:nowrap; border-bottom:1px solid #30363d; position:sticky; top:0; }
td { padding:6px; border-bottom:1px solid #21262d; white-space:nowrap; }
tr:hover { background:#1c2128; }
tr.signal-long { background:rgba(63,185,80,0.15); border-left:3px solid #3fb950; }
tr.signal-short { background:rgba(248,81,69,0.15); border-left:3px solid #f85149; }
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
.loading { text-align:center; padding:40px; color:#484f58; }
.error { color:#f85149; }
.footer { margin-top:10px; text-align:center; color:#484f58; font-size:11px; }
.fund-section { margin-top:14px; background:#161b22; border-radius:8px; padding:10px; border:1px solid #30363d; }
.fund-section h3 { color:#8b949e; font-size:12px; margin-bottom:6px; }
.fund-grid { display:flex; gap:6px; flex-wrap:wrap; }
.fund-item { background:#1c2128; padding:3px 8px; border-radius:4px; font-size:10px; }
@media (max-width:768px) {
  .header { flex-direction:column; align-items:flex-start; }
  table { font-size:10px; }
  th, td { padding:4px 3px; }
}
</style>
</head>
<body>
<div class="header">
  <h1>1H-15M Scanner <span class="live-badge">LIVE</span></h1>
  <div class="stats" id="stats"></div>
</div>
<div id="content"><div class="loading">Loading data...</div></div>
<div class="fund-section" id="fund-section" style="display:none">
  <h3>Fundamental Highlights</h3>
  <div class="fund-grid" id="fund-grid"></div>
</div>
<div class="trade-section" id="trade-section">
  <h3>Open Positions</h3>
  <div id="open-positions"></div>
  <h3 style="margin-top:8px">Completed Orders</h3>
  <div id="completed-tabs" style="display:flex;gap:4px;margin-bottom:6px">
    <button class="tab-btn active" data-tab="all" style="background:#30363d;color:#c9d1d9;border:none;border-radius:4px;padding:3px 10px;cursor:pointer;font-size:10px">All</button>
    <button class="tab-btn" data-tab="profit" style="background:#30363d;color:#3fb950;border:none;border-radius:4px;padding:3px 10px;cursor:pointer;font-size:10px">Profit</button>
    <button class="tab-btn" data-tab="loss" style="background:#30363d;color:#f85149;border:none;border-radius:4px;padding:3px 10px;cursor:pointer;font-size:10px">Loss</button>
  </div>
  <div id="completed-orders"></div>
  <h3 style="margin-top:8px">Trade Log</h3>
  <div id="trade-log"></div>
</div>
<div class="footer">1H trend + 15M momentum filter &middot; 15M entry &middot; Updates every 15m on candle close</div>
<script>
let prevPrices={}, lastData=null, completedTab='all';
async function load(){try{
  const r=await fetch('/data');
  if(!r.ok) throw new Error('HTTP '+r.status);
  const d=await r.json();
  const rows=d.rows||[], st=d.stats||{}, ts=d.timestamp||'', lp=d.live_prices||{};
  const mode=st.mode||'OFF'; const modeCls=mode==='LIVE'?'mode-live':mode==='PAPER'?'mode-paper':'mode-off';
  document.getElementById('stats').innerHTML=
    '<div class="stat"><span>BTC:</span> <span class="val '+st.btc_trend+'">'+st.btc_trend?.toUpperCase()+'</span></div>'+
    '<div class="stat"><span>Candle:</span> <span class="val">'+(st.next_candle||'-')+'</span></div>'+
    '<div class="stat"><span>Pairs:</span> <span class="val">'+rows.length+'</span></div>'+
    '<div class="stat"><span>Signals:</span> <span class="val">'+(st.signals||0)+'</span></div>'+
    '<div class="stat"><span>Trade:</span> <span class="val '+modeCls+'">'+mode+'</span></div>'+
    '<div class="stat"><span>'+ts+'</span></div>';

  lastData=d;
  renderTable(rows, lp);
  renderFund(rows);
  renderTrades(d);
}catch(e){document.getElementById('content').innerHTML='<div class="error">Error: '+e.message+'</div>'}}

function renderTable(rows, lp){
  let html='<table><thead><tr>'+
    '<th>Coin</th><th>Live Price</th><th>Chg</th><th>Dir</th><th>Entry</th><th>TP</th><th>SL</th>'+
    '<th>R:R</th><th>Lev</th><th>L%</th><th>S%</th><th>F%</th><th>ATR%</th><th>RSI</th><th>24h%</th><th>DS%</th><th>Pump</th><th>Per</th><th>Scr</th>'+
    '</tr></thead><tbody>';
  for(const r of rows){
    const cls=r.direction==='LONG'?'signal-long':r.direction==='SHORT'?'signal-short':'';
    const dirCls=r.direction==='NONE'?'':'dir '+r.direction;
    const liveP=lp[r.coin];
    const price=liveP!=null?liveP:r.price;
    const prevP=prevPrices[r.coin];
    let pCls='price-same';
    if(prevP!=null&&liveP!=null){pCls=liveP>prevP?'price-up':liveP<prevP?'price-down':'price-same'}
    const chg=liveP!=null&&r.price?((liveP-r.price)/r.price*100):null;
    const chgCls=chg!=null?(chg>=0?'pnl-pos':'pnl-neg'):'';
    prevPrices[r.coin]=liveP!=null?liveP:r.price;
    const ed=r.entry_dir||'';
                    const entryLabel=r.entry?(ed==='LONG'?'L: ':'S: ')+fmtPrice8(r.entry):'-';
                    const tpLabel=r.target?fmtPrice8(r.target):'-';
                    const slLabel=r.sl?fmtPrice8(r.sl):'-';
    const overall=Math.max(r.long_pct||0, r.short_pct||0);
    const scrHtml=overall>0?overall+'%':'-';
    html+='<tr class="'+cls+'">'+
      '<td class="coin">'+r.coin+'</td>'+
      '<td class="num '+pCls+'">'+fmtPrice(price)+'</td>'+
      '<td class="num '+chgCls+'">'+(chg!=null?(chg>=0?'+':'')+chg.toFixed(2)+'%':'-')+'</td>'+
      '<td class="'+dirCls+'">'+(r.direction||'-')+'</td>'+
      '<td class="num">'+entryLabel+'</td>'+
      '<td class="num">'+tpLabel+'</td>'+
      '<td class="num">'+slLabel+'</td>'+
      '<td class="num">'+(r.rr>0?r.rr.toFixed(2):'-')+'</td>'+
      '<td style="text-align:center">'+(r.leverage||'-')+'</td>'+
      '<td class="num">'+(r.long_pct!=null?r.long_pct+'%':'-')+'</td>'+
      '<td class="num">'+(r.short_pct!=null?r.short_pct+'%':'-')+'</td>'+
      '<td class="num">'+(r.fund_pct?r.fund_pct+'%':'-')+'</td>'+
      '<td class="num">'+(r.atr_pct!=null?r.atr_pct.toFixed(2)+'%':'-')+'</td>'+
      '<td class="num">'+(r.rsi!=null?r.rsi.toFixed(1):'-')+'</td>'+
      '<td class="num '+(r.change_24h!=null?(r.change_24h>=0?'pnl-pos':'pnl-neg'):'')+'">'+(r.change_24h!=null?r.change_24h.toFixed(2)+'%':'-')+'</td>'+
      '<td class="num" style="font-weight:600">'+(r.ds_conf?r.ds_conf+'%':'-')+'</td>'+
      '<td class="num" style="'+(r.pump?'color:#d29922;font-weight:700':'')+'">'+(r.pump?r.pump_ratio+'x':'-')+'</td>'+
      '<td class="num">'+(r.persist?r.persist+'x':'-')+'</td>'+
      '<td class="num" style="font-weight:600">'+scrHtml+'</td>'+
    '</tr>';
  }
  html+='</tbody></table>';
  document.getElementById('content').innerHTML=html;
}

document.addEventListener('click',function(e){
  var t=e.target;
  if(t.classList.contains('close-btn')){var coin=t.getAttribute('data-coin'),p=prevPrices[coin];if(p) fetch('/close?coin='+coin+'&price='+p)}
  if(t.classList.contains('tab-btn')){completedTab=t.getAttribute('data-tab');document.querySelectorAll('.tab-btn').forEach(function(b){b.style.background='#30363d'});t.style.background='#58a6ff';renderCompleted(lastData?lastData.completed_orders||[]:[])}
});

function renderFund(rows){
  const fundCoins=rows?rows.filter(r=>r.fund_pct>0):[];
  if(fundCoins.length){const fg=document.getElementById('fund-grid');fg.innerHTML=fundCoins.map(r=>'<span class="fund-item"><b>'+r.coin+'</b> F:'+r.fund_pct+'% '+(r.checks?.Top50?'Top50':r.checks?.Top100?'Top100':'')+' '+(r.checks?.Liq?'Liq':'')+(r.checks?.Room?' Room':'')+(r.checks?.Dip?' Dip':'')+'</span>').join('');document.getElementById('fund-section').style.display=''}
  else{document.getElementById('fund-section').style.display='none'}
}

function renderCompleted(orders){
  var filtered=orders; var el=document.getElementById('completed-orders');
  if(completedTab==='profit'){filtered=orders.filter(function(o){return o.pnl>=0})}
  else if(completedTab==='loss'){filtered=orders.filter(function(o){return o.pnl<0})}
  if(!filtered.length){el.innerHTML='<span style="color:#484f58;font-size:11px">No completed orders '+(completedTab==='all'?'':completedTab)+'</span>';return}
  el.innerHTML='<table class="trade-table"><tr><th>Time</th><th>Coin</th><th>Dir</th><th>Entry</th><th>Exit</th><th>P&amp;L%</th><th>P&amp;L</th><th>Qty</th><th>Reason</th></tr>'+
    filtered.map(function(o){
      var pnlCls=o.pnl>=0?'pnl-pos':'pnl-neg';
      return '<tr><td>'+o.time+'</td><td class="coin">'+o.coin+'</td><td class="dir '+o.direction+'">'+(o.direction||'-')+'</td><td>'+(o.entry!=null?fmtPrice(o.entry):'-')+'</td><td>'+(o.exit!=null?fmtPrice(o.exit):'-')+'</td><td class="'+pnlCls+'">'+(o.pnl!=null?o.pnl+'%':'-')+'</td><td class="'+pnlCls+'">'+(o.pnl_value!=null?'$'+o.pnl_value.toFixed(2):'-')+'</td><td>'+(o.qty||'-')+'</td><td>'+(o.reason||'-')+'</td></tr>';
    }).join('')+
    '</table>';
}

function renderTrades(d){
  const open=d.open_positions||[], log=d.trade_log||[], completed=d.completed_orders||[];
  const opEl=document.getElementById('open-positions');
  if(open.length){
    opEl.innerHTML='<table class="trade-table"><tr><th>Coin</th><th>Dir</th><th>Entry</th><th>Price</th><th>P&L</th><th>TP</th><th>SL</th><th>Qty</th><th>Since</th><th></th></tr>'+
      open.map(p=>{
        const pnlCls=p.pnl!=null?(p.pnl>=0?'pnl-pos':'pnl-neg'):'';
        const liveP=p.live_price!=null?fmtPrice(p.live_price):'-';
        const pnlStr=p.pnl!=null?p.pnl+'%':'-';
        const btn='<button data-coin="'+p.coin+'" class="close-btn" style="background:#f85149;color:#fff;border:none;border-radius:4px;padding:2px 6px;cursor:pointer;font-size:10px">Close</button>';
        return '<tr><td class="coin">'+p.coin+'</td><td class="dir '+p.direction+'">'+p.direction+'</td><td>'+fmtPrice(p.entry)+'</td><td class="'+pnlCls+'">'+liveP+'</td><td class="'+pnlCls+'">'+pnlStr+'</td><td>'+fmtPrice(p.target)+'</td><td style="color:#f85149">'+fmtPrice(p.sl)+'</td><td>'+p.qty+'</td><td>'+p.entry_time+'</td><td>'+btn+'</td></tr>';
      }).join('')+
      '</table>';
  } else {opEl.innerHTML='<span style="color:#484f58;font-size:11px">No open positions</span>'}
  const lgEl=document.getElementById('trade-log');
  if(log.length){
    const rev=[...log].reverse();
    lgEl.innerHTML='<table class="trade-table"><tr><th>Time</th><th>Mode</th><th>Coin</th><th>Dir</th><th>Entry</th><th>Exit</th><th>P&L</th><th>Status</th></tr>'+
      rev.map(t=>{
        const pnlCls=t.pnl!=null?(t.pnl>=0?'pnl-pos':'pnl-neg'):'';
        return '<tr><td>'+t.time+'</td><td>'+t.mode+'</td><td class="coin">'+t.coin+'</td><td class="dir '+t.direction+'">'+(t.direction||'-')+'</td><td>'+(t.entry!=null?fmtPrice(t.entry):'-')+'</td><td>'+(t.exit!=null?fmtPrice(t.exit):'-')+'</td><td class="'+pnlCls+'">'+(t.pnl!=null?t.pnl+'%':'-')+'</td><td>'+(t.status||'-')+'</td></tr>';
      }).join('')+
      '</table>';
  } else {lgEl.innerHTML='<span style="color:#484f58;font-size:11px">No trades yet</span>'}
  renderCompleted(completed);
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
        elif path.startswith("/close"):
            import trader
            query = urlparse(self.path).query
            params = {kv.split("=")[0]: kv.split("=")[1] for kv in query.split("&") if "=" in kv}
            coin = params.get("coin", "")
            price_str = params.get("price", "0")
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                price = _live_prices.get(coin, 0)
            if coin and price > 0:
                log_entry = trader.close_position(coin, price)
                result = {"status": "ok", "log": log_entry} if log_entry else {"status": "not_found"}
            else:
                result = {"status": "error", "message": "missing coin or price"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
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
    _data["rows"] = rows
    _data["stats"] = stats
    _data["timestamp"] = datetime.now().strftime("%H:%M:%S")


def update_live_prices(prices):
    global _live_prices
    _live_prices.update(prices)


def start():
    server = HTTPServer((_host, _port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
