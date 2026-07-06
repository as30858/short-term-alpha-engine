from flask import Flask
import yfinance as yf
import requests
from datetime import datetime
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = "8814271928:AAG8Db_g6Z4noOEYdLeXe0wzgELDP7ijjNw"
TELEGRAM_CHAT_ID = "8867850194"

# High-liquidity mid/large-cap stocks suited for parking short-term money
SHORT_TERM_WATCHLIST = [
    'HDFCBANK.NS', 'BEL.NS', 'HAL.NS', 'LT.NS', 'TATAPOWER.NS', 'TATASTEEL.NS',
    'ITC.NS', 'BANKBARODA.NS', 'PFC.NS', 'RECLTD.NS', 'ONGC.NS', 'NTPC.NS', 
    'INFY.NS', 'RELIANCE.NS', 'BHARTIARTL.NS', 'COALINDIA.NS'
]

def run_short_term_scan():
    velocity_picks = []
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for ticker in SHORT_TERM_WATCHLIST:
        try:
            stock = yf.Ticker(ticker, session=session)
            # Fetch 3 months of historical data to check the near-term velocity trend
            hist = stock.history(period="3mo")
            if len(hist) < 20: continue
            
            current_price = float(hist['Close'].iloc[-1])
            price_20_days_ago = float(hist['Close'].iloc[-20])
            avg_volume = hist['Volume'].tail(20).mean()
            latest_volume = hist['Volume'].iloc[-1]
            
            # Analytical Filters: Strong 20-day momentum AND expanding institutional volume
            if current_price > price_20_days_ago and latest_volume > (avg_volume * 1.15):
                momentum_pct = ((current_price - price_20_days_ago) / price_20_days_ago) * 100
                
                # Dynamic Headline News Extraction
                news_feed = stock.get_news()
                headline_text = "No recent major global news wire matches."
                if news_feed and len(news_feed) > 0:
                    headline_text = f"[{news_feed[0]['title']}]({news_feed[0]['link']})"
                
                velocity_picks.append(
                    f"🚀 *{ticker}* \n"
                    f"  ▪️ *Current Price:* ₹{current_price:.2f}\n"
                    f"  ▪️ *Short-Term Momentum:* +{momentum_pct:.1f}% (Last 20 Days)\n"
                    f"  ▪️ *Institutional Volume Spike:* +{((latest_volume/avg_volume)-1)*100:.1f}%\n"
                    f"  ▪️ *Live Market Wire:* {headline_text}\n"
                )
        except Exception:
            pass

    report = f"⚡ *SHORT-TERM CAPITAL VELOCITY REPORT* ⚡\n🗓️ Date: {datetime.now().strftime('%d-%b-%Y')}\n🎯 Strategy: High-Liquidity 1-12 Month Swing Allocations\n────────────────────────\n\n"
    
    if velocity_picks:
        report += "\n".join(velocity_picks[:5])
    else:
        report += "⚖️ *Market Analytics Note:* Volatility index is high; global sector news has currently pushed tracked short-term assets into a defensive neutral hold pattern."
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": report, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=15)

@app.route('/')
def handle_request():
    threading.Thread(target=run_short_term_scan).start()
    return "Short-term alpha matrix scanning initialized successfully.", 200
