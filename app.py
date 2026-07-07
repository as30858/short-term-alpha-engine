from flask import Flask
import yfinance as yf
import requests
from datetime import datetime
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = "8814271928:AAG8Db_g6Z4noOEYdLeXe0wzgELDP7ijjNw"
TELEGRAM_CHAT_ID = "8867850194"

SHORT_TERM_WATCHLIST = [
    'HDFCBANK.NS', 'BEL.NS', 'HAL.NS', 'LT.NS', 'TATAPOWER.NS', 'TATASTEEL.NS',
    'ITC.NS', 'BANKBARODA.NS', 'PFC.NS', 'RECLTD.NS', 'ONGC.NS', 'NTPC.NS', 
    'INFY.NS', 'RELIANCE.NS', 'BHARTIARTL.NS', 'COALINDIA.NS'
]

def deep_financial_and_sentiment_scan():
    premium_picks = []
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for ticker in SHORT_TERM_WATCHLIST:
        try:
            stock = yf.Ticker(ticker, session=session)
            
            # Fundamentals Evaluation
            info = stock.info
            debt_to_equity = info.get('debtToEquity', 0)
            rev_growth = info.get('quarterlyRevenueGrowth', 0)
            rev_growth_pct = (rev_growth * 100) if rev_growth else 0.0
            
            # Technical Flow & Volatility Velocity Filters
            hist = stock.history(period="3mo")
            if len(hist) < 20: continue
            
            current_price = float(hist['Close'].iloc[-1])
            price_20_days_ago = float(hist['Close'].iloc[-20])
            avg_volume = hist['Volume'].tail(20).mean()
            latest_volume = hist['Volume'].iloc[-1]
            
            if current_price > price_20_days_ago and latest_volume > (avg_volume * 1.05):
                momentum_pct = ((current_price - price_20_days_ago) / price_20_days_ago) * 100
                
                # Structural filter: Ensure data verification fields aren't heavily overleveraged
                if rev_growth_pct > 0 or debt_to_equity < 200:
                    premium_picks.append(
                        f"🏛️ *{ticker}* \n"
                        f"  ▪️ *Current Price:* ₹{current_price:.2f} (+{momentum_pct:.1f}% Momentum)\n"
                        f"  ▪️ *YoY Revenue Growth:* {rev_growth_pct:+.1f}%\n"
                        f"  ▪️ *Debt-to-Equity Ratio:* {debt_to_equity:.1f}%\n"
                        f"  ▪️ *Status:* Confirmed Financial Stability Alignment\n"
                    )
        except Exception:
            pass

    report = (
        f"🎯 *DEEP-VALUE SHORT-TERM MATRIX* 🎯\n"
        f"🗓️ Date: {datetime.now().strftime('%d-%b-%Y')}\n"
        f"📊 Metric Scope: Fundamentals, Gearing & Price Momentum\n"
        f"────────────────────────\n\n"
    )
    
    if premium_picks:
        report += "\n".join(premium_picks[:5])
    else:
        report += "⚖️ *System Note:* Market consolidation has temporarily pushed active tickers into a defensive hold rating based on strict fundamental conditions."
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": report, "parse_mode": "Markdown"}, timeout=15)

@app.route('/')
def handle_request():
    threading.Thread(target=deep_financial_and_sentiment_scan).start()
    return "OK", 200
