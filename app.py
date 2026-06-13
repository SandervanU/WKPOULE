import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WK Poule", page_icon="⚽", layout="wide")

DATA = Path("data.xlsx")

# =========================
# LOAD DATA ONCE
# =========================
if "df" not in st.session_state:
    xls = pd.ExcelFile(DATA)
    st.session_state.df = pd.read_excel(xls, xls.sheet_names[0], header=None)

df = st.session_state.df

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

matches = df.iloc[MATCH_START:].copy()
matches = matches[matches.iloc[:, 3].notna() & matches.iloc[:, 4].notna()]

HOME_COL = 3
AWAY_COL = 4
RESULT_COL = 5
PRED_START = 7

# =========================
# STAND CALC
# =========================
def calc_stand(df):
    scores = {p: 0 for p in players}

    for _, row in matches.iterrows():
        uitslag = row[RESULT_COL]

        for i, p in enumerate(players):
            pred = row[PRED_START + i]

            if pd.notna(uitslag) and pd.notna(pred):
                if str(pred).strip() == str(uitslag).strip():
                    scores[p] += 1

    return pd.DataFrame(scores.items(), columns=["Deelnemer", "Punten"]).sort_values("Punten", ascending=False)

# =========================
# AUTH
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# SIDEBAR NAV
# =========================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "🔧 Admin"])

# =========================
# DASHBOARD
# =========================
if menu == "📊 Dashboard":

    st.title("⚽ WK Poule")

    st.subheader("🏆 Stand")
    st.dataframe(calc_stand(df), use_container_width=True, hide_index=True)

    st.divider()
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

# =========================
# ADMIN
# =========================
if menu == "🔧 Admin":

    st.title("🔧 Admin Panel")

    password = st.text_input("Wachtwoord", type="password")

    if password != "sander":
        st.warning("Geen toegang")
        st.stop()

    st.success("Ingelogd als admin")

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

    if st.button("Opslaan"):

        # update session df
        st.session_state.df.loc[excel_row, RESULT_COL] = new_result

        st.success("Opgeslagen!")

        st.rerun()
