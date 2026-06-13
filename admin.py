import streamlit as st
import pandas as pd
from pathlib import Path

from config import DATA

st.set_page_config(page_title="Admin WK Poule", layout="wide")

st.title("🔧 Admin - WK Poule")

if not DATA.exists():
    st.error("data.xlsx niet gevonden")
    st.stop()

# =========================
# LOAD DATA
# =========================
xls = pd.ExcelFile(DATA)
df = pd.read_excel(xls, xls.sheet_names[0], header=None)

players = ["Jacq", "Joost", "Sander", "Tessa", "Sander 2", "Madelon"]

# =========================
# FIND MATCH START (same as app)
# =========================
def find_match_start(df):
    for i in range(len(df)):
        row = df.iloc[i].astype(str).tolist()
        if "Datum" in row and "Thuis" in row and "Uit" in row:
            return i + 1
    return None

MATCH_START = find_match_start(df)

if MATCH_START is None:
    st.error("Kon match tabel niet vinden")
    st.stop()

matches = df.iloc[MATCH_START:].copy()

# filter valid rows
matches = matches[matches.iloc[:, 3].notna() & matches.iloc[:, 4].notna()]

# =========================
# SAME COLUMN MAPPING AS APP
# =========================
HOME_COL = 3
AWAY_COL = 4
RESULT_COL = 5
PRED_START = 7

# =========================
# MATCH SELECT
# =========================
match_options = [
    f"{i} - {row[HOME_COL]} vs {row[AWAY_COL]}"
    for i, (_, row) in enumerate(matches.iterrows())
]

selected = st.selectbox("Select match", match_options)

match_idx = int(selected.split(" - ")[0])
excel_row = matches.index[match_idx]

current = df.loc[excel_row, RESULT_COL]

st.write("Huidige uitslag:", current)

new_result = st.selectbox("Nieuwe uitslag", ["1", "2", "3"], index=0)

# =========================
# SAVE (IMPORTANT FIX)
# =========================
if st.button("Opslaan"):

    df.loc[excel_row, RESULT_COL] = new_result

    # write safely back to Excel
    with open(DATA, "wb") as f:
        df.to_excel(f, index=False, header=False)

    st.success("Opgeslagen!")

    # force refresh admin page
    st.rerun()
