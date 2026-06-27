function fmtPrice(p){return p}
function fmtPrice8(p){return p}

let prevPrices={};
async function load(){try{
  const r=await fetch('/data');
  if(!r.ok) throw new Error('HTTP '+r.status);
  const d=await r.json();
  if(!d||!d.rows){document.getElementById('content').innerHTML='<div class="error">No data</div>';return}
  const rows=d.rows||[], st=d.stats||{}, ts=d.timestamp||'', lp=d.live_prices||{}, tr=d.trader||{};
  document.getElementById('stats').innerHTML=
    '<div class="stat"><span>BTC:</span> <span class="val '+st.btc_trend+'">'+st.btc_trend?.toUpperCase()+'</span></div>'+
    '<div class="stat"><span>Candle:</span> <span class="val">'+(st.next_candle||'-')+'</span></div>'+
    '<div class="stat"><span>Pairs:</span> <span class="val">'+rows.length+'</span></div>'+
    '<div class="stat"><span>Signals:</span> <span class="val">'+(st.signals||0)+'</span></div>'+
    '<div class="stat"><span>'+ts+'</span></div>';

  renderTradePanel(tr, rows);
  renderTable(rows, lp);
  renderFund(rows);
}catch(e){document.getElementById('content').innerHTML='<div class="error">Error: '+e.message+'</div>';document.getElementById('trade-content').innerHTML='<div class="error">Error</div>'}}

function renderTradePanel(tr, rows){
  const div=document.getElementById('trade-content');
  if(!tr||!tr.initial_balance){div.innerHTML='<div class="loading">Waiting for trader...</div>';return}
  const badge=document.getElementById('trade-badge');
  if(tr.paused){badge.innerHTML='<span class="alert-paused">&#9208; PAUSED</span>'}
  else if(tr.max_drawdown>=10){badge.innerHTML='<span class="alert-stop">&#9888; STOPPED (DD '+tr.max_drawdown+'%)</span>'}
  else{badge.innerHTML='<span style="color:#3fb950;font-size:11px">&#9679; Active</span>'}

  const totalPnl=tr.total_pnl_amount;
  const pnlCls=totalPnl>=0?'green':'red';

  let html='<div class="trade-grid">'+
    '<div class="trade-item"><div class="label">Balance</div><div class="value">$'+tr.balance.toFixed(2)+'</div></div>'+
    '<div class="trade-item"><div class="label">Equity</div><div class="value">$'+tr.equity.toFixed(2)+'</div></div>'+
    '<div class="trade-item"><div class="label">Total P&L</div><div class="value '+pnlCls+'">$'+totalPnl.toFixed(2)+' ('+tr.total_pnl_pct+'%)</div></div>'+
    '<div class="trade-item"><div class="label">Trades</div><div class="value">'+tr.total_trades+'</div></div>'+
    '<div class="trade-item"><div class="label">Win Rate</div><div class="value">'+tr.win_rate+'%</div></div>'+
    '<div class="trade-item"><div class="label">Profit Factor</div><div class="value">'+tr.profit_factor+'</div></div>'+
    '<div class="trade-item"><div class="label">Wins/Losses</div><div class="value">'+tr.wins+'/'+tr.losses+'</div></div>'+
    '<div class="trade-item"><div class="label">Avg Win / Loss</div><div class="value">$'+tr.avg_win+' / $'+tr.avg_loss+'</div></div>'+
    '<div class="trade-item"><div class="label">Drawdown</div><div class="value">'+tr.max_drawdown+'%</div></div>'+
    '<div class="trade-item"><div class="label">Today</div><div class="value '+(tr.daily_pnl>=0?'green':'red')+'">$'+tr.daily_pnl.toFixed(2)+'</div></div>'+
    '<div class="trade-item"><div class="label">This Week</div><div class="value '+(tr.weekly_pnl>=0?'green':'red')+'">$'+tr.weekly_pnl.toFixed(2)+'</div></div>'+
    '<div class="trade-item"><div class="label">Open</div><div class="value">'+tr.open_positions+'</div></div>'+
    '</div>';

  html+='<div class="trade-actions">'+
    '<button class="btn '+(tr.paused?'green':'yellow')+'" onclick="sendCmd(''+(tr.paused?'resume':'pause')+'')">'+(tr.paused?'&#9654; Resume':'&#9208; Pause')+'</button>'+
    '</div>';

  if(tr.recent_trades&&tr.recent_trades.length>0){
    html+='<div style="margin-top:8px"><table><thead><tr><th>Coin</th><th>Dir</th><th>Entry</th><th>Exit</th><th>P&L</th><th>P&L%</th><th>Reason</th></tr></thead><tbody>';
    for(const t of tr.recent_trades){
      const tc=t.pnl_pct>=0?'pnl-pos':'pnl-neg';
      html+='<tr><td class="coin">'+t.coin+'</td><td style="color:'+(t.direction==='LONG'?'#3fb950':'#f85149')+'">'+t.direction+'</td>'+
        '<td class="num">'+t.entry+'</td><td class="num">'+t.exit+'</td>'+
        '<td class="num '+tc+'">$'+t.pnl_amount.toFixed(2)+'</td><td class="num '+tc+'">'+t.pnl_pct+'%</td>'+
        '<td>'+t.reason+'</td></tr>';
    }
    html+='</tbody></table></div>';
  }
  div.innerHTML=html;
}

function renderTable(rows, lp){
  if(!rows.length){document.getElementById('content').innerHTML='<div class="loading">Waiting for data...</div>';return}
  let html='<table><thead><tr>'+
    '<th>Coin</th><th>Live Price</th><th>Chg</th><th>Dir</th><th>Entry</th><th>TP</th><th>SL</th>'+
    '<th>R:R</th><th>Lev</th><th>L%</th><th>S%</th><th>F%</th><th>ATR%</th><th>RSI</th><th>24h%</th><th>Scr</th><th>S/F</th><th>Win%</th>'+
    '</tr></thead><tbody>';
  for(const r of rows){
    const cls=r.direction==='LONG'?'signal-long':r.direction==='SHORT'?'signal-short':'';
    const dirCls='dir '+r.direction;
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
      '<td class="num" style="font-weight:600">'+scrHtml+'</td>'+
      '<td class="num">'+(r.success>0||r.failed>0?r.success+'/'+r.failed:'-')+'</td>'+
      '<td class="num">'+(r.win_rate>0?r.win_rate+'%':'-')+'</td>'+
    '</tr>';
  }
  html+='</tbody></table>';
  document.getElementById('content').innerHTML=html;
}

function renderFund(rows){
  const fundCoins=rows.filter(r=>r.fund_pct>0);
  if(fundCoins.length){const fg=document.getElementById('fund-grid');fg.innerHTML=fundCoins.map(r=>'<span class="fund-item"><b>'+r.coin+'</b> F:'+r.fund_pct+'% '+(r.checks?.Top50?'Top50':r.checks?.Top100?'Top100':'')+' '+(r.checks?.Liq?'Liq':'')+(r.checks?.Room?' Room':'')+(r.checks?.Dip?' Dip':'')+'</span>').join('');document.getElementById('fund-section').style.display=''}
  else{document.getElementById('fund-section').style.display='none'}
}

async function sendCmd(action, coin){
  try{
    const body={action};
    if(coin)body.coin=coin;
    const r=await fetch('/command',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const d=await r.json();
    if(!d.ok)alert('Error: '+d.error);
  }catch(e){alert('Command failed: '+e.message)}
}

function fmtPrice(p){if(p>=100)return p.toFixed(2);if(p>=10)return p.toFixed(3);if(p>=1)return p.toFixed(4);if(p>=0.01)return p.toFixed(5);return p.toFixed(6)}
function fmtPrice8(p){if(p>=100)return p.toFixed(2);if(p>=10)return p.toFixed(3);if(p>=1)return p.toFixed(4);if(p>=0.01)return p.toFixed(5);return p.toFixed(6)}
load();setInterval(load,1000);
