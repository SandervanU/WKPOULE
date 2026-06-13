import streamlit as st
import pandas as pd
from pathlib import Path

import shutil
from config import DATA

SOURCE = Path(__file__).resolve().parent / "data.xlsx"

if not DATA.exists():
    shutil.copy(SOURCE, DATA)

st.set_page_config(page_title="WK Poule", page_icon="⚽", layout="wide")

st.title("⚽ WK Poule")

if not DATA.exists():
    st.error("data.xlsx niet gevonden")
    st.stop()

# =========================
# FORCE RELOAD DATA (NO CACHE ISSUES)
# =========================
@st.cache_data(ttl=0)
def load_data():
    xls = pd.ExcelFile(DATA)
    return pd.read_excel(xls, xls.sheet_names[0], header=None)

df = load_data()

players = ["Jacq", "Joost", "Sander", "Tessa", "Sander 2", "Madelon"]

# =========================
# FIND MATCH START
# =========================
def find_match_start(df):
    for i in range(len(df)):
        row = df.iloc[i].astype(str).tolist()
        if "Datum" in row and "Thuis" in row and "Uit" in row:
            return i + 1
    return None

MATCH_START = find_match_start(df)

if MATCH_START is None:
    st.error("Kon match tabel niet vinden in Excel")
    st.stop()

matches = df.iloc[MATCH_START:].copy()

# filter echte rijen
matches = matches[matches.iloc[:, 3].notna() & matches.iloc[:, 4].notna()]

# =========================
# COLUMN MAPPING (JOUW FILE)
# =========================
HOME_COL = 3
AWAY_COL = 4
RESULT_COL = 5
PRED_START = 7

# =========================
# STAND BEREKENEN
# =========================
scores = {p: 0 for p in players}

for _, row in matches.iterrows():
    uitslag = row[RESULT_COL]

    for i, p in enumerate(players):
        pred = row[PRED_START + i]

        if pd.notna(uitslag) and pd.notna(pred):
            if str(pred).strip() == str(uitslag).strip():
                scores[p] += 1

stand = pd.DataFrame(scores.items(), columns=["Deelnemer", "Punten"])
stand = stand.sort_values("Punten", ascending=False)

st.subheader("🏆 Stand")
st.dataframe(stand, use_container_width=True, hide_index=True)

st.divider()

# =========================
# MATCH VIEW
# =========================
st.subheader("📅 Wedstrijden")

for _, row in matches.iterrows():
    home = row[HOME_COL]
    away = row[AWAY_COL]
    uitslag = row[RESULT_COL]

    if pd.isna(home) or pd.isna(away):
        continue

    with st.expander(f"{home} - {away}"):

        st.write(f"**Uitslag:** {uitslag}")

        table = []

        for i, p in enumerate(players):
            pred = row[PRED_START + i]

            correct = (
                pd.notna(pred)
                and pd.notna(uitslag)
                and str(pred).strip() == str(uitslag).strip()
            )

            table.append({
                "Deelnemer": p,
                "Voorspelling": pred,
                "Correct": "✅" if correct else "❌"
            })

        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
