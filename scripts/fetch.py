import json, sys, time, math, statistics as st, requests, concurrent.futures as cf
# Main ranking: S&P 500 companies, grouped into the site's sector filters.
# Tickers that no longer trade are skipped automatically.
U = {
"Technology":"""AAPL MSFT NVDA AVGO ORCL CRM ADBE AMD CSCO ACN IBM INTU QCOM TXN AMAT MU NOW PANW LRCX ADI ANET KLAC
 PLTR CRWD INTC APH MSI CDNS SNPS ADSK ROP FTNT WDAY NXPI MCHP TEL IT GLW CTSH HPQ HPE DELL ON MPWR KEYS FICO
 CDW TYL TER ZBRA NTAP STX WDC PTC GDDY SMCI FSLR ENPH JBL TRMB AKAM FFIV EPAM GEN SWKS VRSN DDOG APP TTD""",
"Communication":"GOOGL META NFLX DIS TMUS VZ T CMCSA CHTR EA TTWO OMC LYV MTCH FOXA NWSA",
"Consumer":"""AMZN TSLA HD MCD NKE SBUX LOW BKNG TJX ABNB CMG ORLY AZO MAR HLT GM F ROST DHI LEN YUM RCL CCL NCLH
 EBAY DPZ DRI GPC ULTA LVS WYNN MGM BBY TSCO POOL KMX LKQ PHM NVR TPR RL DECK HAS EXPE APTV GRMN LULU CZR
 COST WMT PG KO PEP PM MDLZ CL MO KMB GIS KHC KDP STZ SYY ADM HSY KR MNST CHD CLX MKC CAG CPB SJM HRL TSN TAP
 BG EL DG DLTR TGT LW""",
"Financials":"""JPM BAC WFC GS MS BLK SCHW AXP V MA C SPGI BRK-B PGR CB MMC AON ICE CME MCO PNC USB TFC COF AIG MET
 PRU AFL TRV ALL AJG BK STT FITB HBAN RF KEY CFG MTB NTRS SYF PYPL FIS FI GPN AMP TROW BEN IVZ RJF CINF L WRB
 HIG ACGL BRO EG GL AIZ NDAQ CBOE MSCI FDS KKR BX APO COIN HOOD""",
"Health Care":"""LLY UNH JNJ ABBV MRK TMO ABT PFE DHR AMGN ISRG BSX VRTX GILD SYK MDT BMY ELV CI CVS HCA MCK COR CAH
 ZTS BDX EW REGN IDXX IQV A RMD DXCM GEHC HUM CNC MOH BIIB MRNA ALGN STE WAT MTD COO HOLX BAX ZBH PODD TECH
 CRL VTRS INCY DVA UHS HSIC LH DGX WST RVTY SOLV""",
"Industrials":"""GE CAT RTX HON UNP BA DE LMT UPS ETN ADP ITW GD NOC WM RSG CSX NSC FDX EMR PH CTAS TT CARR OTIS JCI
 PCAR CMI GWW FAST ODFL URI PWR AME ROK IR XYL DOV HWM VRSK PAYX CPRT LHX TDG HII TXT DAL UAL LUV J WAB EFX BR
 LDOS SNA PNR MAS ALLE AOS CHRW EXPD JBHT GNRC BLDR SWK NDSN IEX HUBB AXON UBER""",
"Energy & Utilities":"""XOM CVX COP EOG SLB OXY PSX MPC VLO WMB KMI OKE DVN FANG HAL BKR EQT TRGP APA
 NEE SO DUK D AEP SRE EXC XEL PCG ED PEG WEC EIX ETR DTE FE PPL AEE CMS CNP NI ATO LNT EVRG AES NRG PNW VST CEG""",
"Real Estate & Materials":"""PLD AMT EQIX CCI PSA O SPG WELL DLR VICI AVB EQR EXR IRM SBAC CBRE VTR ARE MAA ESS INVH KIM
 REG UDR HST CPT BXP FRT LIN SHW APD ECL FCX NEM DOW DD NUE PPG VMC MLM CTVA IFF LYB ALB CF MOS STLD PKG IP
 BALL AMCR AVY EMN""",
}
# Extra lower-priced, widely held stocks used by the Budget tab (core list above is the main ranking)
BUDGET = {
"Technology":"INTC HPE HPQ NOK GLW DELL SNAP PINS RBLX U",
"Communication":"WBD SIRI KHC CHTR LUMN",
"Consumer":"F GM RIVN LCID CCL NCLH AAL DAL UAL JBLU KDP KVUE MO CAG GIS HRL WBA M",
"Financials":"SOFI HOOD NU KEY HBAN RF CFG FITB USB TFC BEN IVZ AGNC NLY ALLY",
"Health Care":"VTRS TEVA BMY CVS HLN",
"Industrials":"GRAB UBER LYFT CSX JBLU",
"Energy & Utilities":"KMI ET EPD OXY DVN CTRA BTU AES PCG EXC",
"Real Estate & Materials":"VALE FCX NEM KGC CLF AA MPW O VICI",
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
CORE = {s for s,_ in syms}
for sec,v in BUDGET.items():
    for t in v.split():
        if t not in CORE and t not in {x for x,_ in syms}: syms.append((t,sec))
with cf.ThreadPoolExecutor(6) as ex: res = {s:(m,p) for s,m,p in ex.map(get,[s for s,_ in syms])}
def ret(p,n,skip=0):
    c=[x[1] for x in p]; return c[-1-skip]/c[-1-n]-1 if len(c)>n else None
spy = res["SPY"][1]
out=[]
for s,sec in syms:
    m,p = res[s]
    if not p or len(p) < 130: print("skip",s,file=sys.stderr); continue
    c=[x[1] for x in p]
    dr=[c[i]/c[i-1]-1 for i in range(1,len(c))]
    vol=st.pstdev(dr[-126:])*math.sqrt(252)
    sma50=sum(c[-50:])/50; sma200=sum(c[-200:])/min(200,len(c))
    hi=max(c); r12=ret(p,len(c)-1)
    d=dict(sym=s, name=m.get("longName") or m.get("shortName") or s, sector=sec, core=s in CORE, price=round(c[-1],2),
      chg1d=round(m.get("regularMarketChangePercent") or 0,2),
      r1m=ret(p,21), r3m=ret(p,63), r6m=ret(p,126), r12m=r12, mom=ret(p,len(c)-1,21),
      vol=vol, sma50=sma50, sma200=sma200, offHigh=c[-1]/hi-1,
      spark=[round(x,2) for x in c[::-5][::-1]][-52:])
    for k in ("r1m","r3m","r6m","r12m","mom","vol","offHigh"): d[k]=round(d[k],4) if d[k] is not None else None
    d["sma50"]=round(sma50,2); d["sma200"]=round(sma200,2)
    out.append(d)
if len(out) < 0.8*len(syms) or not res["SPY"][1]:
    sys.exit(f"Only got {len(out)} of {len(syms)} stocks; keeping the old data.json")
asof = max(x[0] for x in res["SPY"][1])
json.dump({"asof":asof,"stocks":out}, open(sys.argv[1] if len(sys.argv)>1 else "data.json","w"), separators=(",",":"))
print(len(out), "stocks", time.strftime("%Y-%m-%d", time.gmtime(asof)))
