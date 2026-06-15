import streamlit as st
import pandas as pd

from config import DATA, init_data

st.set_page_config(
    page_title="WK Poule",
    page_icon="⚽",
    layout="wide"
)

init_data()

st.title("⚽ WK Poule")

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=0)
def load_data():
    xls = pd.ExcelFile(DATA)
    return pd.read_excel(
        xls,
        xls.sheet_names[0],
        header=None
    )

df = load_data()

players = [
    "Jacq",
    "Joost",
    "Sander",
    "Tessa",
    "Sander 2",
    "Madelon"
]

# =========================
# FIND MATCH START
# =========================
def find_match_start(df):
    for i in range(len(df)):
        row = df.iloc[i].astype(str).tolist()

        if (
            "Datum" in row
            and "Thuis" in row
            and "Uit" in row
        ):
            return i + 1

    return None

MATCH_START = find_match_start(df)

if MATCH_START is None:
    st.error("Kon wedstrijdtabel niet vinden")
    st.stop()

# =========================
# BONUSVRAGEN
# =========================
BONUS_START = 5
BONUS_END = 11

bonus_df = df.iloc[BONUS_START:BONUS_END].copy()

# =========================
# WEDSTRIJDEN
# =========================
matches = df.iloc[MATCH_START:].copy()

matches = matches[
    matches.iloc[:, 3].notna()
    & matches.iloc[:, 4].notna()
]

HOME_COL = 3
AWAY_COL = 4
RESULT_COL = 5

PRED_START = 7

# =========================
# STAND BEREKENEN
# =========================
scores = {p: 0 for p in players}

# wedstrijden
for _, row in matches.iterrows():

    uitslag = row[RESULT_COL]

    home = str(row[HOME_COL]).strip()
    away = str(row[AWAY_COL]).strip()

    # Nederland wedstrijd = 2 punten
    match_points = 2 if (
        home == "Nederland"
        or away == "Nederland"
    ) else 1

    for i, p in enumerate(players):

        pred = row[PRED_START + i]

        if pd.notna(uitslag) and pd.notna(pred):

            if str(pred).strip() == str(uitslag).strip():
                scores[p] += match_points

# bonusvragen
for _, row in bonus_df.iterrows():

    correct_answer = row[5]

    for i, p in enumerate(players):

        answer = row[PRED_START + i]

        if pd.notna(correct_answer) and pd.notna(answer):

            if str(answer).strip() == str(correct_answer).strip():
                scores[p] += 5

stand = pd.DataFrame(
    scores.items(),
    columns=["Deelnemer", "Punten"]
)

stand = stand.sort_values(
    "Punten",
    ascending=False
)

# =========================
# STAND
# =========================
st.subheader("🏆 Stand")

st.dataframe(
    stand,
    use_container_width=True,
    hide_index=True
)

# =========================
# BONUSVRAGEN
# =========================
st.divider()

st.subheader("🎯 Bonusvragen")

for _, row in bonus_df.iterrows():

    vraag = row[1]
    correct = row[5]

    if pd.isna(vraag):
        continue

    with st.expander(str(vraag)):

        st.write(
            f"**Correct antwoord:** {correct}"
        )

        table = []

        for i, p in enumerate(players):

            antwoord = row[PRED_START + i]

            juist = (
                pd.notna(correct)
                and pd.notna(antwoord)
                and str(antwoord).strip()
                == str(correct).strip()
            )

            table.append({
                "Deelnemer": p,
                "Antwoord": antwoord,
                "Correct": "✅" if juist else "❌"
            })

        st.dataframe(
            pd.DataFrame(table),
            use_container_width=True,
            hide_index=True
        )

# =========================
# WEDSTRIJDEN
# =========================
st.divider()

st.subheader("📅 Wedstrijden")

for _, row in matches.iterrows():

    home = row[HOME_COL]
    away = row[AWAY_COL]
    uitslag = row[RESULT_COL]

    if pd.isna(home) or pd.isna(away):
        continue

    with st.expander(f"{home} - {away}"):

        st.write(
            f"**Uitslag:** {uitslag if pd.notna(uitslag) else 'Nog niet gespeeld'}"
        )

        table = []

        for i, p in enumerate(players):

            pred = row[PRED_START + i]

            correct = (
                pd.notna(pred)
                and pd.notna(uitslag)
                and str(pred).strip()
                == str(uitslag).strip()
            )

            table.append({
                "Deelnemer": p,
                "Voorspelling": pred,
                "Correct": "✅" if correct else "❌"
            })

        st.dataframe(
            pd.DataFrame(table),
            use_container_width=True,
            hide_index=True
        )
