import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WK Poule", page_icon="⚽", layout="wide")

from config import DATA

st.title("⚽ WK Poule")

if not DATA.exists():
    st.error("data.xlsx niet gevonden")
    st.stop()

# -----------------------------
# LOAD EXCEL (eerste sheet)
# -----------------------------
xls = pd.ExcelFile(DATA)
df = pd.read_excel(xls, xls.sheet_names[0], header=None)

# -----------------------------
# CONFIG (jouw structuur)
# -----------------------------
BONUS_START = 5
MATCH_START = 12

COL_HOME = 2
COL_AWAY = 3
COL_RESULT = 4

PRED_START = 5   # Jacq start hier
NUM_PLAYERS = 6

players = ["Jacq", "Joost", "Sander", "Tessa", "Sander 2", "Madelon"]

# -----------------------------
# BONUS (optioneel tonen)
# -----------------------------
st.subheader("🎯 Bonusvragen")

bonus = df.iloc[BONUS_START:BONUS_START+5, :]

for i, row in bonus.iterrows():
    st.write(f"**{row[0]}**")
    answers = row[5:11].tolist()
    st.write(dict(zip(players, answers)))
    st.divider()

# -----------------------------
# WEDSTRIJDEN
# -----------------------------
st.subheader("📅 Wedstrijden")

matches = df.iloc[MATCH_START:].copy()
matches = matches.dropna(subset=[COL_HOME, COL_AWAY])

# -----------------------------
# STAND BEREKENEN
# -----------------------------
scores = {p: 0 for p in players}

for _, row in matches.iterrows():
    uitslag = row[COL_RESULT]

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

# -----------------------------
# MATCH VIEW
# -----------------------------
for _, row in matches.iterrows():
    home = row[COL_HOME]
    away = row[COL_AWAY]
    uitslag = row[COL_RESULT]

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
