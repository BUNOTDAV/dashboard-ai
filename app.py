import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Portfolio", layout="wide")

st.title("📊 Mon Portefeuille")

# =========================
# TABLEAU MODIFIABLE
# =========================

st.sidebar.header("💼 Ton portefeuille")

df = pd.DataFrame({
    "Nom": ["NVIDIA", "ASML", "MSCI WORLD"],
    "Montant (€)": [1000, 800, 2000],
    "Performance (%)": [25, -10, 5]
})

df = st.sidebar.data_editor(df, num_rows="dynamic")

# =========================
# MAPPING
# =========================

mapping = {
    "NVIDIA": "NVDA",
    "ASML": "ASML",
    "TSMC": "TSM",
    "MSCI WORLD": "IWDA.AS",
}

def get_ticker(name):
    for k in mapping:
        if k in name.upper():
            return mapping[k]
    return name

# =========================
# CONVERSION
# =========================

positions = []

for _, row in df.iterrows():
    try:
        nom = row["Nom"]
        montant = float(row["Montant (€)"])
        perf = float(row["Performance (%)"])
        ticker = get_ticker(nom)

        positions.append((nom, ticker, montant, perf))
    except:
        pass

# =========================
# GRAPHIQUE PORTEFEUILLE
# =========================

st.subheader("📈 Évolution portefeuille")

data = pd.DataFrame()

for nom, ticker, montant, perf in positions:
    try:
        hist = yf.Ticker(ticker).history(period="1mo")
        hist["value"] = hist["Close"] / hist["Close"].iloc[0] * montant

        if data.empty:
            data = hist[["value"]]
        else:
            data = data.join(hist["value"], how="outer", rsuffix="_"+ticker)
    except:
        pass

if not data.empty:
    data = data.fillna(method="ffill")
    data["total"] = data.sum(axis=1)
    st.line_chart(data["total"])

# =========================
# GRAPHIQUE PAR ACTION
# =========================

st.subheader("📊 Performance par action")

perf_dict = {}

for nom, ticker, montant, perf in positions:
    try:
        hist = yf.Ticker(ticker).history(period="1mo")
        variation = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
        perf_dict[nom] = variation
    except:
        perf_dict[nom] = 0

df_perf = pd.DataFrame.from_dict(perf_dict, orient="index", columns=["Perf %"])

st.bar_chart(df_perf)

# =========================
# SCORE
# =========================

st.subheader("🧠 Score portefeuille")

total = sum([p[2] for p in positions])

score = 0
for nom, ticker, montant, perf in positions:
    poids = montant / total if total else 0
    score += poids * perf

st.metric("Performance globale (%)", round(score,2))
