
import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Dashboard Portfolio", layout="wide")

st.title("📊 Dashboard Portfolio (Simple & Propre)")

# Mapping noms -> tickers
mapping = {
    "NVIDIA": "NVDA",
    "ASML": "ASML",
    "TSMC": "TSM",
    "MICROSOFT": "MSFT",
    "APPLE": "AAPL",
    "META": "META",
    "MSCI WORLD": "IWDA.AS",
    "CW8": "CW8.PA",
    "GOLD": "GLD",
    "BIGBEAR.AI": "BBAI",
    "IONQ": "IONQ",
    "QUANTUM EMOTION": "QNC.V",
    "WESTERN DIGITAL": "WDC",
    "EURO STOXX BANKS": "BNK.PA"
}

def convert(name):
    name = str(name).upper()
    for k in mapping:
        if k in name:
            return mapping[k]
    return name

# Tableau éditable
st.sidebar.header("💼 Ton Portefeuille")

data_init = pd.DataFrame({
    "Nom": ["NVIDIA", "ASML", "MSCI WORLD"],
    "Montant (€)": [1000, 800, 2000],
    "Performance (%)": [25, -10, 5]
})

df = st.sidebar.data_editor(
    data_init,
    num_rows="dynamic",
    use_container_width=True
)

# Conversion positions
positions = []

for _, row in df.iterrows():
    try:
        nom = row["Nom"]
        montant = float(row["Montant (€)"])
        perf = float(row["Performance (%)"])
        ticker = convert(nom)

        positions.append((nom, ticker, montant, perf))
    except:
        pass

# Analyse simple
st.subheader("📊 Analyse")

results = []

for nom, ticker, montant, perf in positions:
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        perf_court = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100

        if perf_court > 3:
            signal = "🔥 Fort"
        elif perf_court > 0:
            signal = "📈 Positif"
        else:
            signal = "⚠️ Faible"

        results.append((nom, montant, perf, round(perf_court,2), signal))
        time.sleep(0.3)

    except:
        results.append((nom, montant, perf, 0, "Erreur"))

for r in results:
    st.write(f"{r[0]} | {r[1]}€ | Perf: {r[2]}% | Momentum: {r[3]}% → {r[4]}")

# Graphique portefeuille
st.subheader("📈 Évolution du portefeuille")

@st.cache_data(ttl=300)
def portfolio_history(positions):
    df_all = pd.DataFrame()

    for nom, ticker, montant, perf in positions:
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            hist["value"] = hist["Close"] / hist["Close"].iloc[0] * montant

            if df_all.empty:
                df_all = hist[["value"]]
            else:
                df_all = df_all.join(hist["value"], how="outer", rsuffix="_"+ticker)

        except:
            pass

    df_all = df_all.fillna(method="ffill")
    df_all["total"] = df_all.sum(axis=1)

    return df_all

if positions:
    df_port = portfolio_history(positions)
    st.line_chart(df_port["total"])

# Graphique par action
st.subheader("📊 Performance par action")

data_perf = {}

for nom, ticker, montant, perf in positions:
    try:
        hist = yf.Ticker(ticker).history(period="1mo")
        variation = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
        data_perf[nom] = round(variation, 2)
    except:
        data_perf[nom] = 0

df_perf = pd.DataFrame.from_dict(data_perf, orient="index", columns=["Perf %"])
st.bar_chart(df_perf)

# Score portefeuille
st.subheader("🧠 Score global")

total = sum([p[2] for p in positions])
score = 0

for nom, ticker, montant, perf in positions:
    poids = montant / total if total else 0
    score += poids * perf

st.metric("Performance pondérée (%)", round(score,2))
