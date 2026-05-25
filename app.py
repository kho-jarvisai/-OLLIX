import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from data_loader import IndianMarketLoader
from analyst import QuantitativeAnalyst
from database import SignalDatabase
from notifier import TelegramNotifier

st.set_page_config(layout="wide", page_title="Institutional Quantamental Terminal")
SignalDatabase.initialize_db()

# Premium Institutional Broker UI Theme Upgrades
st.markdown("""
    <style>
    .reportview-container { background-color: #0b0e14; }
    .stButton>button { width: 100%; background-color: #00b4d8; color: black; font-weight: bold; border-radius: 6px; }
    .execution-card { background-color: #121824; padding: 24px; border-radius: 10px; border: 1px solid #1e293b; }
    .ticker-header { font-size: 32px; font-weight: bold; color: #ffffff; }
    .sector-label { font-size: 13px; color: #00b4d8; text-transform: uppercase; font-weight: 600; margin-bottom: 20px; }
    .metric-row { display: flex; justify-content: space-between; margin-bottom: 20px; gap: 10px; }
    .panel-metric { background-color: #1e293b; padding: 12px; border-radius: 6px; flex: 1; text-align: center; }
    .panel-lbl { font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }
    .panel-val { font-size: 18px; font-weight: bold; }
    
    /* Binary Execution Color Profiles */
    .badge-buy { background-color: #22c55e; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-short { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-noedge { background-color: #475569; color: #cbd5e1; padding: 4px 8px; border-radius: 4px; font-weight: normal; }
    
    .reasoning-text { background-color: #090d16; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6; font-size: 14px; color: #cbd5e1; }
    
    /* Telemetry Log Sub-Panel Styling */
    .telemetry-box { background-color: #070a12; border: 1px solid #1e293b; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; color: #10b981; margin-bottom: 6px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ High-Conviction Sectoral Core Terminal")

tab_live, tab_ledger = st.tabs(["📊 Active Market Terminal", "🗄️ Saved Signal Ledger"])

# Initialize session storage matrices to hold onto telemetry logs across button cycles
if "scan_data" not in st.session_state:
    st.session_state.scan_data = None
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None
if "telemetry_stream" not in st.session_state:
    st.session_state.telemetry_stream = []

with tab_live:
    target_domain = st.selectbox("Select Target Operational Domain Matrix:", [
        "NIFTY 50", "BANKNIFTY (Fixed Core)", "NIFTY MIDCAP 50", "NIFTY SMALLCAP 50",
        "NIFTY IT", "NIFTY AUTO", "NIFTY FINANCIAL SERVICES", "NIFTY FMCG",
        "NIFTY METAL", "NIFTY ENERGY", "NIFTY INDIA DEFENCE", "NIFTY OIL AND GAS"
    ])

    if st.button("RUN SPEED-OPTIMIZED QUANTAMENTAL SCAN"):
        with st.spinner(f"Executing Vectorized Calculations for {target_domain}..."):
            
            if "BANKNIFTY" in target_domain:
                basket = [f"{t}.NS" for t in ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BANKBARODA"]]
                lookback = "1y"
            else:
                basket = IndianMarketLoader.fetch_live_sector_tickers(target_domain)
                lookback = "3y"
                
            if basket:
                prices = IndianMarketLoader.fetch_nse_data(basket, period=lookback)
                
                if not prices.empty:
                    returns = prices.pct_change().dropna()
                    weights = QuantitativeAnalyst.get_eigen_portfolio_weights(returns)
                    sorted_weights = weights.sort_values(ascending=False)
                    top_filtered_weights = sorted_weights.head(8) 
                    
                    st.session_state.scan_data = {
                        "prices": prices,
                        "sorted_weights": top_filtered_weights
                    }
                    st.session_state.selected_row = top_filtered_weights.index[0].replace(".NS", "")
                    
                    # Reset dynamic logs stream on every fresh button press cycle
                    st.session_state.telemetry_stream = []
                    auto_alerts_sent = 0
                    
                    for t_code in top_filtered_weights.index:
                        t_series = prices[t_code]
                        c_px = float(t_series.iloc[-1])
                        s_50 = float(t_series.rolling(50).mean().iloc[-1])
                        s_200 = float(t_series.rolling(200).mean().iloc[-1])
                        t_atr = float(t_series.diff().abs().rolling(14).mean().iloc[-1])
                        t_clean = t_code.replace(".NS", "")
                        
                        if c_px > s_50 and s_50 > s_200:
                            TelegramNotifier.send_execution_alert(t_clean, "STRONGBUY", c_px, c_px - (2 * t_atr), c_px + (3 * t_atr), "Resistance Target")
                            auto_alerts_sent += 1
                            st.session_state.telemetry_stream.append(f"🟢 [BROADCAST SUCCESS]: Dynamic outlier match identified for {t_clean}. STRONGBUY parameters piped to mobile.")
                        elif c_px < s_200:
                            TelegramNotifier.send_execution_alert(t_clean, "STRONGSHORT", c_px, c_px + (2 * t_atr), c_px - (3 * t_atr), "Floor Support Zone")
                            auto_alerts_sent += 1
                            st.session_state.telemetry_stream.append(f"🔴 [BROADCAST SUCCESS]: Structural freefall breakdown verified for {t_clean}. STRONGSHORT mapped to phone.")
                            
                    # ST_FIX: Modern fading toast alert replacing old sticky sidebar notification box
                    if auto_alerts_sent > 0:
                        st.toast(f"📱 Secure Pipeline Link Active: Dispatched {auto_alerts_sent} High-Conviction setups straight to Telegram!", icon="⚡")

    if st.session_state.scan_data is not None:
        prices = st.session_state.scan_data["prices"]
        sorted_weights = st.session_state.scan_data["sorted_weights"]
        
        rows = []
        for ticker in sorted_weights.index:
            if ticker not in prices.columns:
                continue
            series = prices[ticker]
            current_price = float(series.iloc[-1])
            sma_50 = float(series.rolling(50).mean().iloc[-1])
            sma_200 = float(series.rolling(200).mean().iloc[-1])
            atr = float(series.diff().abs().rolling(14).mean().iloc[-1])
            
            if current_price > sma_50 and sma_50 > sma_200:
                pred, boundary_label, stop_loss, boundary_val = "STRONGBUY", "Resistance Target", current_price - (2 * atr), current_price + (3 * atr)
            elif current_price < sma_200:
                pred, boundary_label, stop_loss, boundary_val = "STRONGSHORT", "Floor Support Zone", current_price + (2 * atr), current_price - (3 * atr)
            else:
                pred, boundary_label, stop_loss, boundary_val = "NO_EDGE", "Neutral Boundary", 0.00, 0.00
                
            rows.append({
                "Ticker": ticker.replace(".NS", ""), "Signal": pred, "CMP (₹)": f"{current_price:.2f}",
                "Buy/Sell Zone": f"{current_price:.2f}" if pred != "NO_EDGE" else "0.00", 
                "Stop Loss (₹)": f"{stop_loss:.2f}" if pred != "NO_EDGE" else "0.00",
                "Boundary Target (₹)": f"{boundary_val:.2f}" if pred != "NO_EDGE" else "0.00", 
                "Boundary Type": boundary_label
            })
            
        matrix_df = pd.DataFrame(rows)
        
        st.write("### 📊 Active Sector Matrix")
        render_df = matrix_df.copy()
        
        def assign_badge(val):
            if val == "STRONGBUY": return f'<span class="badge-buy">{val}</span>'
            if val == "STRONGSHORT": return f'<span class="badge-short">{val}</span>'
            return f'<span class="badge-noedge">{val}</span>'
            
        render_df['Signal'] = render_df['Signal'].apply(assign_badge)
        columns_to_show = ["Ticker", "Signal", "CMP (₹)", "Buy/Sell Zone", "Stop Loss (₹)", "Boundary Target (₹)", "Boundary Type"]
        
        st.write(render_df[columns_to_show].to_html(escape=False, index=False, classes='table table-dark table-hover'), unsafe_allow_html=True)
        st.write("")
        
        st.session_state.selected_row = st.selectbox("Inspect Asset Workspace:", matrix_df["Ticker"].tolist())
        st.write("---")

        active_ticker = st.session_state.selected_row + ".NS"
        row_data = matrix_df[matrix_df["Ticker"] == st.session_state.selected_row].iloc[0]
        
        border_color = "#22c55e" if row_data["Signal"] == "STRONGBUY" else ("#ef4444" if row_data["Signal"] == "STRONGSHORT" else "#475569")
        badge_style = "badge-buy" if row_data["Signal"] == "STRONGBUY" else ("badge-short" if row_data["Signal"] == "STRONGSHORT" else "badge-noedge")
        
        st.markdown('<div class="execution-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="ticker-header">{row_data["Ticker"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sector-label">{target_domain} Balanced Workspace Node</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="metric-row">
                <div class="panel-metric" style="border-bottom: 3px solid {border_color};">
                    <div class="panel-lbl">Execution Signal</div>
                    <div class="panel-val"><span class="{badge_style}">{row_data["Signal"]}</span></div>
                </div>
                <div class="panel-metric">
                    <div class="panel-lbl">Current Market Price</div>
                    <div class="panel-val">₹{row_data["CMP (₹)"]}</div>
                </div>
            </div>
            <div class="metric-row">
                <div class="panel-metric">
                    <div class="panel-lbl">Trigger Entry</div>
                    <div class="panel-val" style="color: #22c55e;">₹{row_data["Buy/Sell Zone"]}</div>
                </div>
                <div class="panel-metric">
                    <div class="panel-lbl">Stop Loss</div>
                    <div class="panel-val" style="color: #ef4444;">₹{row_data["Stop Loss (₹)"]}</div>
                </div>
                <div class="panel-metric">
                    <div class="panel-lbl">{row_data["Boundary Type"]}</div>
                    <div class="panel-val" style="color: #00b4d8;">₹{row_data["Boundary Target (₹)"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if row_data["Signal"] != "NO_EDGE":
            if st.button("⚡ LOG SELECTION TO LOCAL DATABASE"):
                SignalDatabase.log_signal(
                    ticker=str(row_data["Ticker"]), signal_type=str(row_data["Signal"]),
                    entry=float(row_data["Buy/Sell Zone"]), stop=float(row_data["Stop Loss (₹)"]),
                    target=float(row_data["Boundary Target (₹)"]), b_type=str(row_data["Boundary Type"])
                )
                TelegramNotifier.send_execution_alert(
                    str(row_data["Ticker"]), str(row_data["Signal"]), 
                    float(row_data["Buy/Sell Zone"]), float(row_data["Stop Loss (₹)"]), 
                    float(row_data["Boundary Target (₹)"]), str(row_data["Boundary Type"])
                )
                st.toast(f"Logged parameter states and mirrored data link to phone line!", icon="✅")
        else:
            st.info("Execution Locked: System identifies no quantitative edge for this node today. Capital preservation active.")
        
        st.write("**🤖 Catalyst Reasoning Evaluation:**")
        raw_news_titles = IndianMarketLoader.fetch_optimized_rss_news(active_ticker)
        
        if not raw_news_titles:
            st.markdown(f'<div class="reasoning-text" style="border-left-color: #00b4d8;"><b>[SYSTEM UPDATE]:</b> Structural matrix metrics remain intact. No headline anomalies reported for <b>{row_data["Ticker"]}</b>.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Querying local model backend..."):
                news_payload = "".join([f"- {title}\n" for title in raw_news_titles])
                prompt = f"You are a hedge fund risk officer. Synthesize these news items for {row_data['Ticker']} running a {row_data['Signal']} outlook:\n{news_payload}\nProvide a fast 2-sentence verdict. Speak naturally."
                try:
                    res = requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False}, timeout=15)
                    st.markdown(f'<div class="reasoning-text">{res.json().get("response")}</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="reasoning-text" style="border-left-color: red;">AI pipeline timeout.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- ST_FIX: PERSISTENT END-OF-SCREEN TELEMETRY FEED STREAM ---
        st.write("")
        st.write("---")
        st.write("### 🛰️ Live Outbound Telemetry Stream History")
        if st.session_state.telemetry_stream:
            for log_entry in st.session_state.telemetry_stream:
                st.markdown(f'<div class="telemetry-box">{log_entry}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="telemetry-box" style="color: #64748b;">[STANDBY]: No high-conviction communication packets dispatched within the active interface cycle. Waiting for scan...</div>', unsafe_allow_html=True)

with tab_ledger:
    st.write("### 🏛 Implemented High-Conviction Records")
    stats = SignalDatabase.calculate_live_performance()
    
    st.markdown(f"""
        <div class="metric-row">
            <div class="panel-metric" style="border-top: 3px solid #00b4d8;"><div class="panel-lbl">Total Logged Records</div><div class="panel-val" style="font-size: 24px;">{stats["total"]}</div></div>
            <div class="panel-metric" style="border-top: 3px solid #eab308;"><div class="panel-lbl">Active Pending / Holds</div><div class="panel-val" style="font-size: 24px; color: #eab308;">{stats["pending"]}</div></div>
            <div class="panel-metric" style="border-top: 3px solid #22c55e;"><div class="panel-lbl">Audited Wins</div><div class="panel-val" style="font-size: 24px; color: #22c55e;">{stats["wins"]}</div></div>
            <div class="panel-metric" style="border-top: 3px solid #ef4444;"><div class="panel-lbl">Audited Losses</div><div class="panel-val" style="font-size: 24px; color: #ef4444;">{stats["losses"]}</div></div>
            <div class="panel-metric" style="border-top: 3px solid #ffffff;"><div class="panel-lbl">Realized Win-Rate</div><div class="panel-val" style="font-size: 24px; color: #ffffff;">{stats["win_rate"]}</div></div>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    try:
        import sqlite3
        conn = sqlite3.connect("signals.db")
        ledger_df = pd.read_sql_query("SELECT timestamp, ticker, signal_type, entry_price, stop_loss, boundary_target, boundary_type FROM trade_signals ORDER BY id DESC", conn)
        conn.close()
        if not ledger_df.empty: st.dataframe(ledger_df, use_container_width=True)
        else: st.info("No recorded trades found inside local memory arrays yet.")
    except Exception as e: st.error(f"Failed to fetch local database array context: {e}")