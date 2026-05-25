# analyst.py - Quantitative Orchestration Router & Core Engine
import numpy as np
import pandas as pd
# (Keep any other standard imports like sqlite3 or requests if you use them here)

# ======================================================================
# DYNAMIC BINARY SHIELD / FALLBACK ROUTER
# ======================================================================
try:
    # 1. Attempt to map the secure, compiled Windows binary platform first
    import secret_math as math_engine
    print("🚀 System Status: Running secure compiled binary module.")
except ImportError:
    # 2. Mismatch fallback: Clear the gate for Mac / alternative Python testers
    import secret_math_fallback as math_engine
    print("⚠️ System Status: Platform mismatch detected. Utilizing open cross-platform framework.")


# ======================================================================
# CORE ORCHESTRATION FUNCTIONS
# ======================================================================

def run_portfolio_analysis(matrix_data):
    """
    Cleans incoming data arrays using whichever math engine 
    was successfully mapped by the router above.
    """
    cleaned_matrix = math_engine.filter_matrix_noise(matrix_data)
    return cleaned_matrix

def check_market_signals(short_window, long_window, current_price):
    """
    Evaluates trend boundaries to generate execution signals.
    """
    signal_state = math_engine.generate_signals(short_window, long_window, current_price)
    return signal_state


# ======================================================================
# YOUR EXISTING ANALYSIS MODULES
# ======================================================================
# (If you have other functions below this for managing your SQLite database,
# threading pipelines, or calling data_loader.py, leave them exactly as they are!)