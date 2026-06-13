
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Admin WK Poule", layout="wide")

from config import DATA

st.title("🔧 Admin - WK Poule")

if not DATA.exists():
    st.error("data.xlsx niet gevonden")
    st.stop()

xls = pd.ExcelFile(DATA)
df = pd.read_excel(xls, xls.sheet_names[0], header=None)

MATCH_START = 12
COL_HOME = 2
COL_AWAY = 3
COL_RESULT = 4

matches = df.iloc[MATCH_START:].copy()
matches = matches.dropna(subset=[COL_HOME, COL_AWAY])

match_options = [
    f"{i} - {row[COL_HOME]} vs {row[COL_AWAY]}"
    for i, (_, row) in enumerate(matches.iterrows())
]

selected = st.selectbox("Select match", match_options)

match_idx = int(selected.split(" - ")[0])
excel_row = matches.index[match_idx]

current = df.loc[excel_row, COL_RESULT]

st.write("Huidige uitslag:", current)

new_result = st.selectbox("Nieuwe uitslag", ["1", "2", "3"], index=0)

if st.button("Opslaan"):
    df.loc[excel_row, COL_RESULT] = new_result
    df.to_excel(DATA, index=False, header=False)
    st.success("Opgeslagen!")
