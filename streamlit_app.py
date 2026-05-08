import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Automatic Stock Analyzer", layout="centered")
st.title("📊 Automatic Stock Fundamental Analyzer")

st.markdown("""
Enter a **ticker symbol** and **exchange**, and the app will automatically
fetch financial data, compute fundamental metrics, and generate an investment score.
""")

# ---------------------------------------------------------
# Helper: Fetch and Calculate Financial Metrics
# ---------------------------------------------------------
def fetch_and_compute_metrics(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow

    # --- Revenue Growth (YoY) ---
    revenue = financials.loc["Total Revenue"]
    revenue_growth = ((revenue.iloc[0] - revenue.iloc[1]) / revenue.iloc[1]) * 100

    # --- Earnings Growth (YoY) ---
    earnings = financials.loc["Net Income"]
    earnings_growth = ((earnings.iloc[0] - earnings.iloc[1]) / earnings.iloc[1]) * 100

    # --- Profitability ---
    net_margin = (earnings.iloc[0] / revenue.iloc[0]) * 100
    roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0

    # --- Financial Health ---
    total_debt = balance_sheet.loc["Total Debt"].iloc[0]
    total_equity = balance_sheet.loc["Stockholders Equity"].iloc[0]
    debt_equity = total_debt / total_equity if total_equity else 0

    current_assets = balance_sheet.loc["Current Assets"].iloc[0]
    current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
    current_ratio = current_assets / current_liabilities if current_liabilities else 0

    # --- Free Cash Flow (TTM) ---
    operating_cf = cashflow.loc["Total Cash From Operating Activities"].iloc[0]
    capex = cashflow.loc["Capital Expenditures"].iloc[0]
    free_cash_flow = operating_cf + capex  # capex is negative

    # --- Valuation ---
    pe_ratio = info.get("trailingPE", 0)
    pb_ratio = info.get("priceToBook", 0)

    return {
        "Revenue Growth (%)": round(revenue_growth, 2),
        "Earnings Growth (%)": round(earnings_growth, 2),
        "ROE (%)": round(roe, 2),
        "Net Margin (%)": round(net_margin, 2),
        "Debt-to-Equity": round(debt_equity, 2),
        "Current Ratio": round(current_ratio, 2),
        "Free Cash Flow": round(free_cash_flow, 2),
        "P/E Ratio": round(pe_ratio, 2),
        "P/B Ratio": round(pb_ratio, 2)
    }

# ---------------------------------------------------------
# Scoring Engine (UNCHANGED)
# ---------------------------------------------------------
def score_stock(m):
    score = 0
    score += 10 if m["Revenue Growth (%)"] > 10 else 5
    score += 10 if m["Earnings Growth (%)"] > 10 else 5
    score += 15 if m["ROE (%)"] > 15 else 8
    score += 10 if m["Net Margin (%)"] > 10 else 5
    score += 10 if m["Debt-to-Equity"] < 1 else 5
    score += 10 if m["Current Ratio"] > 1.5 else 5
    score += 15 if m["Free Cash Flow"] > 0 else 0
    score += 10 if m["P/E Ratio"] < 20 else 5
    score += 10 if m["P/B Ratio"] < 3 else 5
    return score

# ---------------------------------------------------------
# UI Input
# ---------------------------------------------------------
ticker = st.text_input("Stock Ticker (e.g., AAPL, MSFT, INFY.NS)")
analyze = st.button("🔍 Fetch & Analyze Automatically")

if analyze and ticker:
    try:
        with st.spinner("Fetching financial data..."):
            metrics = fetch_and_compute_metrics(ticker)
            total_score = score_stock(metrics)

        st.subheader("📌 Auto-Fetched Metrics (TTM / Latest FY)")
        st.dataframe(pd.DataFrame(metrics.items(), columns=["Metric", "Value"]))

        if total_score >= 80:
            result = "✅ Strong Buy"
            color = "green"
        elif total_score >= 60:
            result = "✅ Buy"
            color = "blue"
        elif total_score >= 40:
            result = "⚠️ Hold"
            color = "orange"
        else:
            result = "❌ Avoid"
            color = "red"

        st.markdown("---")
        st.metric("Total Score", f"{total_score} / 100")
        st.markdown(f"<h3 style='color:{color}'>{result}</h3>", unsafe_allow_html=True)

    except Exception as e:
        st.error("Unable to fetch data. Try a different ticker or exchange.")
