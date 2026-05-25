import requests

class TelegramNotifier:
    # Default tracking keys set to universal placeholders
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_PERSONAL_CHAT_ID_HERE"

    @classmethod
    def send_execution_alert(cls, ticker: str, signal_type: str, entry: float, stop: float, target: float, b_type: str):
        """Validates credentials before transmitting outbound network data cards."""
        
        # --- DEFENSIVE FAILOVER GATEKEEPER ---
        # Checks if the user is using defaults or empty strings, or testing blindly
        is_placeholder = "YOUR_" in str(cls.BOT_TOKEN) or "YOUR_" in str(cls.CHAT_ID)
        is_empty = not cls.BOT_TOKEN or not cls.CHAT_ID or cls.BOT_TOKEN == "" or cls.CHAT_ID == ""
        
        if is_placeholder or is_empty:
            # Silently route to local stdout loop instead of making a web request
            print(f"📡 [TELEMETRY STANDBY]: {ticker} {signal_type} alert generated locally. Telegram link inactive (Placeholder or empty keys detected).")
            return True
        # ─────────────────────────────────────
            
        emoji = "🔥" if signal_type == "STRONGBUY" else "⚠️"
        
        message_payload = (
            f"🏛️ <b>HIGH-CONVICTION CORE EXECUTION ALERT</b>\n\n"
            f"• <b>Asset Node:</b> {ticker}\n"
            f"• <b>Action Call:</b> <code>{signal_type}</code> {emoji}\n"
            f"• <b>Target Entry Zone:</b> ₹{entry:.2f}\n"
            f"• <b>Risk Stop Loss:</b> ₹{stop:.2f}\n"
            f"• <b>{b_type}:</b> ₹{target:.2f}\n\n"
            f"<b>[RISK VERDICT]:</b> Extreme mathematical outlier validation confirmed. Signal profile state recorded to persistent local ledger."
        )
        
        url = f"https://api.telegram.org/bot{cls.BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": cls.CHAT_ID,
            "text": message_payload,
            "parse_mode": "HTML"
        }
        
        try:
            res = requests.post(url, data=data, timeout=5)
            return res.json().get("ok", False)
        except Exception as e:
            print(f"Telegram notification relay delay: {e}")
            return False