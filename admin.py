
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Admin", page_icon="🔒")

PASSWORD = "wk2026"
DATA = Path("data.xlsx")

st.title("🔒 Admin Portal")

pwd = st.text_input("Wachtwoord", type="password")

if pwd != PASSWORD:
    st.stop()

uploaded = st.file_uploader("Upload data.xlsx", type=["xlsx"])

if uploaded:
    with open(DATA, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success("Excel opgeslagen")

if not DATA.exists():
    st.stop()

wedstrijden = pd.read_excel(DATA, sheet_name="Wedstrijden")

wedstrijd = st.selectbox(
    "Selecteer wedstrijd",
    wedstrijden.index,
    format_func=lambda x: f"{wedstrijden.loc[x,'Thuis']} - {wedstrijden.loc[x,'Uit']}"
)

uitslag = st.selectbox(
    "Resultaat",
    ["1","2","3"],
    help="1=Thuis wint, 2=Gelijkspel, 3=Uit wint"
)

if st.button("Opslaan"):
    wedstrijden.loc[wedstrijd, "Uitslag"] = uitslag

    with pd.ExcelWriter(DATA, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        wedstrijden.to_excel(writer, sheet_name="Wedstrijden", index=False)

    st.success("Uitslag opgeslagen")
