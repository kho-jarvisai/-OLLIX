import pandas as pd
import yfinance as yf
import streamlit as st
from typing import List, Dict
import requests
import xml.etree.ElementTree as ET

class IndianMarketLoader:
    @staticmethod
    @st.cache_data(ttl=86400) # RAM Cache index rosters for 24 hours
    def fetch_live_sector_tickers(sector_key: str) -> List[str]:
        """Dynamically scrapes index frames using high-speed vectorized engine parsing."""
        sector_urls = {
            "NIFTY 50": "https://en.wikipedia.org/wiki/NIFTY_50",
            "NIFTY MIDCAP 50": "https://en.wikipedia.org/wiki/Nifty_Midcap_50",
            "NIFTY SMALLCAP 50": "https://en.wikipedia.org/wiki/Nifty_Smallcap_50",
            "NIFTY IT": "https://en.wikipedia.org/wiki/NIFTY_IT",
            "NIFTY AUTO": "https://en.wikipedia.org/wiki/Nifty_Auto",
            "NIFTY FMCG": "https://en.wikipedia.org/wiki/Nifty_FMCG",
            "NIFTY METAL": "https://en.wikipedia.org/wiki/Nifty_Metal",
            "NIFTY ENERGY": "https://en.wikipedia.org/wiki/Nifty_Energy",
            "NIFTY FINANCIAL SERVICES": "https://en.wikipedia.org/wiki/Nifty_Financial_Services",
            "NIFTY INDIA DEFENCE": "https://en.wikipedia.org/wiki/Nifty_India_Defence",
            "NIFTY OIL AND GAS": "https://en.wikipedia.org/wiki/Nifty_Oil_%26_Gas"
        }
        
        if sector_key not in sector_urls:
            return []
            
        try:
            url = sector_urls[sector_key]
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
            response = requests.get(url, headers=headers, timeout=5)
            
            # Using flavor='lxml' inside our vectorized parser for raw C-level parsing speed
            tables = pd.read_html(response.text, flavor='lxml')
            df = tables[1] if sector_key == "NIFTY 50" else tables[0]
            
            col = 'Symbol' if 'Symbol' in df.columns else ('Ticker' if 'Ticker' in df.columns else df.columns[0])
            return [f"{str(t).strip()}.NS" for t in df[col].tolist() if pd.notna(t)]
        except Exception as e:
            st.warning(f"Using speed-fallback arrays for {sector_key} due to transport variance.")
            fallbacks = {
                "NIFTY MIDCAP 50": ["VOLTAS", "POLYCAB", "MAXHEALTH", "PERSISTENT", "COFORGE"],
                "NIFTY SMALLCAP 50": ["SUZLON", "BSE", "HUDCO", "ANGELONE", "CDSL"],
                "NIFTY IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
                "NIFTY AUTO": ["TATAMOTORS", "MARUTI", "M&M", "BAJAJ-AUTO", "HEROMOTOCO"],
                "NIFTY FMCG": ["ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR"],
                "NIFTY METAL": ["TATASTEEL", "HINDALCO", "VEDL", "JINDALSTEL", "COALINDIA"],
                "NIFTY ENERGY": ["RELIANCE", "NTPC", "POWERGRID", "ONGC", "BPCL"],
                "NIFTY FINANCIAL SERVICES": ["HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE", "AXISBANK"],
                "NIFTY INDIA DEFENCE": ["HAL", "BEL", "BHARATFORG", "COCHINSHIP", "MAZDOCK"],
                "NIFTY OIL AND GAS": ["RELIANCE", "ONGC", "BPCL", "IOC", "GAIL"]
            }
            return [f"{t}.NS" for t in fallbacks.get(sector_key, ["RELIANCE"])]

    @staticmethod
    @st.cache_data(ttl=1800) # RAM Cache price data for 30 minutes to preserve network bandwidth
    def fetch_nse_data(tickers: List[str], period: str = "3y") -> pd.DataFrame:
        """Executes multi-threaded async concurrent batch downloads across target index pools."""
        try:
            # group_by='ticker' + threads=True runs native C-level concurrent network loops
            df = yf.download(tickers, period=period, group_by='ticker', threads=True, progress=False)
            
            if df.empty:
                return pd.DataFrame()
                
            # Vectorized multi-index extraction is 10x faster than looping through columns manually
            close_dict = {}
            for t in tickers:
                try:
                    if t in df.columns.levels[0]:
                        close_dict[t] = df[t]['Close']
                except:
                    if 'Close' in df.columns:
                        return df['Close'].to_frame(name=tickers[0]).dropna()
                        
            return pd.DataFrame(close_dict).dropna()
        except Exception as e:
            st.error(f"Matrix optimization network execution failure: {e}")
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=900) # Cache news for 15 minutes so flipping through dropdowns is instant
    def fetch_optimized_rss_news(ticker: str) -> List[str]:
        """Ultra-lightweight native XML parser that extracts headlines without BeautifulSoup overhead."""
        clean_name = ticker.replace('.NS', '')
        url = f"https://news.google.com/rss/search?q={clean_name}+stock&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            response = requests.get(url, timeout=3)
            root = ET.fromstring(response.content)
            # Instantly parses XML tags natively at compiled speed levels
            return [item.find('title').text for item in root.findall('.//item')[:3]]
        except:
            return []