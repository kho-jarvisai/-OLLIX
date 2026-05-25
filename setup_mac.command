#!/bin/bash
# Move local directory path execution space to the script home folder context
cd "$(dirname "$0")"

echo "🏛️ OLLIX QUANTAMENTAL TERMINAL INITIALIZATION GATEWAY FOR MAC"
echo "------------------------------------------------------------"

# Check if Python 3 is active on host machine
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 was not detected on this system core architecture."
    echo "Please download and install Python from official servers before running."
    exit
fi

echo "⚡ Auditing local environment dependency arrays..."
python3 -m pip install streamlit pandas numpy yfinance scipy requests beautifulsoup4 lxml openpyxl

echo "🚀 Booting Ollix Core presentation layers via Streamlit..."
python3 -m streamlit run app.py --global.developmentMode=false