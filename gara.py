import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools 

# 1. Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# 2. CSS per centraggio e pulizia
st.markdown("""
<style>
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    [data-testid="stHeader"] button { color: #555 !important; visibility: visible !important; }
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    table { margin: auto; width: 100%; border-collapse: collapse; text-align: center; }
    th { font-size: 36px !important; background-color: #f0f2f6 !important; height: 80px; }
    td { font-size: 32px !important; font-weight: bold !important; height: 80px; vertical-align: middle !important; }
    .stTitle { text-align: center; font-size: 60px !important; }
</style>
""", unsafe_allow_html=True)

# --- STATO SESSIONE ---
if 'gara_avviata' not in st.session_state: st.session_state.gara_avviata = False
PALETTE = ["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb", "#d1f2eb", "#f3d8e6", "#ffeeba"]

# --- CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione")
    c1, c2 = st.columns(2)
    with c1:
        num_s = st.number_input("Squadre", min_value=2, value=5)
        nomi = st.text_area("Nomi (uno per riga)", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    with c2:
        punti_p = st.number_input("Punti partenza", value=200)
        durata = st.number_input("Minuti", min_value=1, value=90)
    
    if st.button("🚀 AVVIA"):
        lista = [n.strip() for n in nomi.split("\n") if n.strip()]
        st.session_state.squadre = {n: {"PUNTI": punti_p} for n in lista}
        st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, 21)}
        st.session_state.risolti = {n: [] for n in lista}
        st.session_state.fine = datetime.now() + timedelta(minutes=durata)
        ciclo = itertools.cycle(PALETTE)
        st.session_state.colori = {n: next(ciclo) for n in lista}
        st.session_state.gara_avviata = True
        st.rerun()

# --- GARA ---
else:
    # Sidebar
    if st.sidebar.button("Reset"):
        st.session_state.gara_avviata = False
        st.rerun()
    
    sq = st.sidebar.selectbox("Squadra", list(st.session_state.squadre.keys()))
    esito = st.sidebar.radio("Esito", ["✅", "❌"])
    if st.sidebar.button("Registra"):
        if esito == "✅": st.session_state.squadre[sq]["PUNTI"] += 20
        else: st.session_state.squadre[sq]["PUNTI"] -= 5
        st.rerun()

    # Prepariamo i dati
    sec = (st.session_state.fine - datetime.now()).total_seconds()
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
    df.columns = ["SQUADRA", "PUNTI"]
    df = df.sort_values(by="PUNTI", ascending=False)
    html = df.style.apply(lambda r: [f'background-color: {st.session_state.colori.get(r["SQUADRA"])};', ''], axis=1).hide(axis="index").to_html()

    # AREA VISUALIZZAZIONE DINAMICA
    placeholder = st.empty()

    with placeholder.container():
        if sec > 120:
            st.title("🏆 CLASSIFICA")
            m, s = divmod(int(sec), 60)
            st.info(f"⏱️ Tempo: {m:02d}:{s:02d}")
            st.write(html, unsafe_allow_html=True)
        elif sec > 0:
            # BUIO TOTALE: La classifica NON viene scritta nel container
            m, s = divmod(int(sec), 60)
            st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 160px; font-weight: bold; text-align: center;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
        else:
            st.title("🏆 FINALE")
            st.error("GARA TERMINATA")
            st.write(html, unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
