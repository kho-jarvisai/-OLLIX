import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import yfinance as yf

class SignalDatabase:
    @staticmethod
    def initialize_db():
        """Creates a local database file and setups our automated trading journal."""
        conn = sqlite3.connect("signals.db")
        cursor = conn.cursor()
        # Create table to permanently store our elite quantamental signals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ticker TEXT,
                signal_type TEXT,
                entry_price REAL,
                stop_loss REAL,
                boundary_target REAL,
                boundary_type TEXT
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def log_signal(ticker: str, signal_type: str, entry: float, stop: float, target: float, b_type: str):
        """Silently saves a high-conviction call to our local uneditable history file."""
        conn = sqlite3.connect("signals.db")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cursor.execute("""
            INSERT INTO trade_signals (timestamp, ticker, signal_type, entry_price, stop_loss, boundary_target, boundary_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, ticker, signal_type, entry, stop, target, b_type))
        
        conn.commit()
        conn.close()

    @staticmethod
    def calculate_live_performance() -> dict:
        """Compares saved signal metrics against live market prices to audit system accuracy."""
        conn = sqlite3.connect("signals.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT ticker, signal_type, entry_price, stop_loss, boundary_target FROM trade_signals")
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            return {"total": 0, "wins": 0, "losses": 0, "pending": 0, "win_rate": "0.0%"}
            
        tickers = list(set([r[0] + ".NS" for r in records]))
        try:
            live_data = yf.download(tickers, period="1d")['Close'].iloc[-1]
        except:
            return {"total": len(records), "wins": 0, "losses": 0, "pending": len(records), "win_rate": "Data Link Error"}
            
        wins = 0
        losses = 0
        pending = 0
        
        if isinstance(live_data, (int, float, np.float64, np.float32)):
            single_ticker = tickers[0]
            val = live_data
            live_data = pd.Series([val], index=[single_ticker])
            
        for ticker, sig_type, entry, stop, target in records:
            t_key = ticker + ".NS"
            if t_key not in live_data or pd.isna(live_data[t_key]):
                pending += 1
                continue
                
            current_price = float(live_data[t_key])
            
            if sig_type == "STRONGBUY":
                if current_price >= target: wins += 1
                elif current_price <= stop: losses += 1
                else: pending += 1
            elif sig_type == "AVOID/SELL":
                if current_price <= target: wins += 1
                elif current_price >= stop: losses += 1
                else: pending += 1
            else:
                # Explicitly tracks HOLD signals or neutral allocations as active pending assets
                pending += 1
                
        total_resolved = wins + losses
        win_rate_pct = (wins / total_resolved * 100) if total_resolved > 0 else 0.0
        
        return {
            "total": len(records),
            "wins": wins,
            "losses": losses,
            "pending": pending,
            "win_rate": f"{win_rate_pct:.1f}%" if total_resolved > 0 else "0.0% (No Exits)"
        }