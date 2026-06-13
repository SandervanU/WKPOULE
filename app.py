
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

try:
    wedstrijden = pd.read_excel(DATA, sheet_name="Wedstrijden")
    stand = pd.read_excel(DATA, sheet_name="Stand")
except Exception as e:
    st.error(f"Kon Excel niet lezen: {e}")
    st.stop()

st.subheader("🏆 Stand")
stand = stand.sort_values("Punten", ascending=False)
st.dataframe(stand, use_container_width=True, hide_index=True)

st.divider()
st.subheader("📅 Wedstrijden")

for _, row in wedstrijden.iterrows():
    title = f"{row['Thuis']} vs {row['Uit']}"
    with st.expander(title):
        st.write(f"**Uitslag:** {row.get('Uitslag','Nog niet gespeeld')}")

        preds = []
        for c in wedstrijden.columns:
            if c not in ["Datum","Thuis","Uit","Uitslag"]:
                preds.append({"Deelnemer": c, "Voorspelling": row[c]})

        st.dataframe(pd.DataFrame(preds), use_container_width=True, hide_index=True)
