import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WK Poule", page_icon="⚽", layout="wide")

DATA = Path("data.xlsx")

st.markdown("""
<style>
.main {background-color:#f8fafc;}
[data-testid="stExpander"]{
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ WK Poule")

if not DATA.exists():
    st.info("Upload eerst data.xlsx via de Admin pagina.")
    st.stop()

# --- Excel inlezen zonder headers (belangrijk voor rij/kolom control) ---
try:
    df_raw = pd.read_excel(DATA, sheet_name="Wedstrijden", header=None)
except Exception as e:
    st.error(f"Kon Excel niet lezen: {e}")
    st.stop()

# =========================
# CONFIG (jouw structuur)
# =========================
START_ROW = 12   # rij 13 in Excel (0-indexed)
COL_HOME = 0
COL_AWAY = 1
COL_RESULT = 5   # kolom F
COL_PRED_START = 7  # kolom H
COL_PRED_END = 12   # kolom M

# deelnemersnamen (rij 11 of ergens boven wedstrijden)
# → we halen ze dynamisch uit rij 12 (header-rij voorspellingen)
deelnemers = list(df_raw.iloc[START_ROW - 1, COL_PRED_START:COL_PRED_END + 1])

# =========================
# WEDSTRIJDEN PARSEN
# =========================
wedstrijden = df_raw.iloc[START_ROW:].copy()
wedstrijden = wedstrijden.dropna(subset=[COL_HOME, COL_AWAY])

def bepaal_winnaar(uitkomst):
    if pd.isna(uitkomst):
        return None
    return str(uitkomst).strip()

# =========================
# STAND BEREKENEN
# =========================
scores = {d: 0 for d in deelnemers if pd.notna(d)}

for _, row in wedstrijden.iterrows():
    uitslag = bepaal_winnaar(row[COL_RESULT])

    for i, d in enumerate(deelnemers):
        if pd.isna(d):
            continue

        voorspelling = row[COL_PRED_START + i]

        if pd.isna(voorspelling) or pd.isna(uitslag):
            continue

        if str(voorspelling).strip() == str(uitslag):
            scores[d] += 1

stand = (
    pd.DataFrame(scores.items(), columns=["Deelnemer", "Punten"])
    .sort_values("Punten", ascending=False)
)

# =========================
# UI
# =========================
st.subheader("🏆 Stand")
st.dataframe(stand, use_container_width=True, hide_index=True)

st.divider()
st.subheader("📅 Wedstrijden")

for _, row in wedstrijden.iterrows():
    thuis = row[COL_HOME]
    uit = row[COL_AWAY]
    uitslag = row[COL_RESULT]

    title = f"{thuis} vs {uit}"

    with st.expander(title):
        st.write(f"**Uitslag:** {uitslag if pd.notna(uitslag) else 'Nog niet gespeeld'}")

        preds = []
        for i, d in enumerate(deelnemers):
            if pd.isna(d):
                continue

            voorspelling = row[COL_PRED_START + i]

            correct = (
                pd.notna(uitslag)
                and pd.notna(voorspelling)
                and str(voorspelling).strip() == str(uitslag).strip()
            )

            preds.append({
                "Deelnemer": d,
                "Voorspelling": voorspelling,
                "Correct": "✅" if correct else "❌"
            })

        st.dataframe(pd.DataFrame(preds), use_container_width=True, hide_index=True)
