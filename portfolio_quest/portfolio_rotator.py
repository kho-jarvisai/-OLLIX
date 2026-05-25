import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import importlib.util

# --- FORCE STREAMLIT DEACTIVATION SWITCH FOR BARE CLI MODE ---
# This intercepts and neutralizes Streamlit before it can inject thread constraints
sys.modules['streamlit'] = type('sys', (), {'cache_data': lambda *a, **k: lambda f: f, 'set_page_config': lambda *a, **k: None, 'tabs': lambda *a, **k: [None, None], 'write': print, 'error': print, 'warning': print, 'info': print, 'success': print})

# --- ABSOLUTE FILE INJECTOR GATE ---
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_local_module(module_name, file_name):
    path = os.path.join(parent_dir, file_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    data_loader_mod = load_local_module("data_loader", "data_loader.py")
    analyst_mod = load_local_module("analyst", "analyst.py")
    
    IndianMarketLoader = data_loader_mod.IndianMarketLoader
    QuantitativeAnalyst = analyst_mod.QuantitativeAnalyst
except Exception as e:
    print(f"❌ Critical System Error: Unable to bind core parent scripts: {e}")
    sys.exit()

def map_ticker_to_sector(ticker: str) -> str:
    """Helper method to auto-detect which index sector pool a stock belongs to."""
    sectors = [
        "NIFTY IT", "NIFTY AUTO", "NIFTY FMCG", "NIFTY METAL", 
        "NIFTY ENERGY", "NIFTY FINANCIAL SERVICES", "NIFTY INDIA DEFENCE", "NIFTY OIL AND GAS"
    ]
    for s in sectors:
        try:
            roster = IndianMarketLoader.fetch_live_sector_tickers(s)
            if f"{ticker}.NS" in roster or ticker in roster:
                return s
        except:
            continue
    return "NIFTY 50"

def run_smart_portfolio_questionnaire():
    """Captures user portfolio data via an interactive terminal interface loop."""
    portfolio_data = []
    print("\n" + "="*70)
    print("🏛️ HIGH-CONVICTION PERSONAL PORTFOLIO ROTATOR ENGINE")
    print("Input your positions below. When finished, type 'done' in the ticker prompt.")
    print("="*70 + "\n")
    
    while True:
        ticker = input("👉 Enter NSE Ticker Symbol (e.g., COFORGE, TATAMOTORS): ").strip().upper()
        if ticker == 'DONE':
            break
        if not ticker:
            continue
            
        try:
            buy_price = float(input(f"   Enter your average buying price for {ticker} (₹): "))
            shares = float(input(f"   Enter total shares held for {ticker}: "))
        except ValueError:
            print("   ❌ Invalid numerical input. Restarting asset entry node...")
            continue
            
        portfolio_data.append({"Ticker": ticker, "Buy_Price": buy_price, "Shares": shares})
        print(f"✅ Node Staged: {ticker} verified.\n")
        
    return portfolio_data

def evaluate_and_rotate_portfolio(holdings):
    if not holdings:
        print("❌ Ingestion aborted. Empty asset profile array.")
        return
        
    print("\n⚡ Processing Sector Alignment Matrix Math. Standby...")
    evaluation_rows = []
    
    for asset in holdings:
        ticker = asset["Ticker"]
        yf_ticker = f"{ticker}.NS"
        sector_context = map_ticker_to_sector(ticker)
        
        peer_basket = IndianMarketLoader.fetch_live_sector_tickers(sector_context)
        if yf_ticker not in peer_basket:
            peer_basket.append(yf_ticker)
            
        # Call yfinance safely down to raw frames
        try:
            prices = yf.download(peer_basket, period="3y", progress=False)['Close']
        except:
            continue
            
        if prices.empty or yf_ticker not in prices.columns:
            continue
                
        returns = prices.pct_change().dropna()
        
        try:
            weights = QuantitativeAnalyst.get_eigen_portfolio_weights(returns)
            sector_leader_yf = weights.idxmax()
            sector_leader_clean = sector_leader_yf.replace(".NS", "")
            asset_rank_weight = weights[yf_ticker]
            sector_median = weights.median()
        except:
            sector_leader_clean = "INDEX_BENCHMARK"
            asset_rank_weight = 1.0
            sector_median = 0.5
            
        series = prices[yf_ticker]
        cmp = float(series.iloc[-1])
        sma_50 = float(series.rolling(50).mean().iloc[-1])
        sma_200 = float(series.rolling(200).mean().iloc[-1])
        
        if cmp > sma_50 and sma_50 > sma_200:
            if asset_rank_weight >= sector_median:
                action = "🟢 KEEP ADDING"
                notes = "Asset is displaying superior momentum and ranks in the top half of its sector matrix."
            else:
                action = "⚪ HOLD"
                notes = f"Price action is healthy, but sector peer '{sector_leader_clean}' shows stronger backing. Pause loading."
        elif cmp < sma_200:
            if ticker == sector_leader_clean:
                action = "⚪ HOLD"
                notes = "Asset is under short-term pressure but maintains primary mathematical dominance in sector."
            else:
                action = "🚨 ROTATE POSITION"
                notes = f"SELL structure. Capital is dead weight here. Move funds directly into peer leader: {sector_leader_clean}"
        else:
            action = "⚪ HOLD"
            notes = f"Neutral consolidation boundaries active. Monitor for breakout or rotation toward {sector_leader_clean}."
            
        pnl_pct = ((cmp - asset["Buy_Price"]) / asset["Buy_Price"]) * 100
        
        evaluation_rows.append({
            "Asset": ticker, "Sector Domain": sector_context, "Buy Price": f"₹{asset['Buy_Price']:.2f}",
            "CMP": f"₹{cmp:.2f}", "Net Return": f"{pnl_pct:.1f}%", "SYSTEM MANDATE": action, "Execution Instructions": notes
        })
        
    df_result = pd.DataFrame(evaluation_rows)
    
    print("\n" + "="*110)
    print("🏛️ STRATEGIC EXECUTION PORTFOLIO VERDICT:")
    print("="*110 + "\n")
    for idx, row in df_result.iterrows():
        print(f"📌 ASSET NODE: {row['Asset']} | Sector: {row['Sector Domain']} | Current Return: {row['Net Return']}")
        print(f"   👉 MANDATE:  {row['SYSTEM MANDATE']}")
        print(f"   👉 ACTION:   {row['Execution Instructions']}\n")
    print("="*110)

if __name__ == "__main__":
    user_positions = run_smart_portfolio_questionnaire()
    evaluate_and_rotate_portfolio(user_positions)