import json, sys, time, math, statistics as st, requests, concurrent.futures as cf
U = {
"Technology":"AAPL MSFT NVDA AVGO ORCL CRM ADBE AMD CSCO ACN IBM INTU QCOM TXN AMAT MU NOW PANW LRCX ADI ANET KLAC PLTR CRWD",
"Communication":"GOOGL META NFLX DIS TMUS VZ T CMCSA",
"Consumer":"AMZN TSLA HD MCD NKE SBUX LOW BKNG TJX COST WMT PG KO PEP PM MDLZ CL",
"Financials":"JPM BAC WFC GS MS BLK SCHW AXP V MA C SPGI BRK-B PGR CB",
"Health Care":"LLY UNH JNJ ABBV MRK TMO ABT PFE DHR AMGN ISRG BSX VRTX GILD SYK",
"Industrials":"GE CAT RTX HON UNP BA DE LMT UPS ETN",
"Energy & Utilities":"XOM CVX COP NEE SO DUK",
"Real Estate & Materials":"PLD AMT LIN SHW",
}
S = requests.Session(); S.headers["User-Agent"]="Mozilla/5.0"
def get(sym):
    for i in range(3):
        try:
            r = S.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d", timeout=20).json()["chart"]["result"][0]
            c = [x for x in r["indicators"]["quote"][0]["close"]]
            t = r["timestamp"]; pts=[(a,b) for a,b in zip(t,c) if b is not None]
            return sym, r["meta"], pts
        except Exception as e: time.sleep(1+i)
    return sym, None, None
syms = [(s,sec) for sec,v in U.items() for s in v.split()] + [("SPY","Benchmark")]
with cf.ThreadPoolExecutor(8) as ex: res = {s:(m,p) for s,m,p in ex.map(get,[s for s,_ in syms])}
def ret(p,n,skip=0):
    c=[x[1] for x in p]; return c[-1-skip]/c[-1-n]-1 if len(c)>n else None
spy = res["SPY"][1]
out=[]
for s,sec in syms:
    m,p = res[s]
    if not p: print("miss",s,file=sys.stderr); continue
    c=[x[1] for x in p]
    dr=[c[i]/c[i-1]-1 for i in range(1,len(c))]
    vol=st.pstdev(dr[-126:])*math.sqrt(252)
    sma50=sum(c[-50:])/50; sma200=sum(c[-200:])/min(200,len(c))
    hi=max(c); r12=ret(p,len(c)-1)
    d=dict(sym=s, name=m.get("longName") or m.get("shortName") or s, sector=sec, price=round(c[-1],2),
      chg1d=round(m.get("regularMarketChangePercent") or 0,2),
      r1m=ret(p,21), r3m=ret(p,63), r6m=ret(p,126), r12m=r12, mom=ret(p,len(c)-1,21),
      vol=vol, sma50=sma50, sma200=sma200, offHigh=c[-1]/hi-1,
      spark=[round(x,2) for x in c[::5]][-52:])
    for k in ("r1m","r3m","r6m","r12m","mom","vol","offHigh"): d[k]=round(d[k],4) if d[k] is not None else None
    d["sma50"]=round(sma50,2); d["sma200"]=round(sma200,2)
    out.append(d)
asof = max(x[0] for x in res["SPY"][1])
json.dump({"asof":asof,"stocks":out}, open(sys.argv[1] if len(sys.argv)>1 else "data.json","w"), separators=(",",":"))
print(len(out), "stocks", time.strftime("%Y-%m-%d", time.gmtime(asof)))
