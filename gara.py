import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools 

# 1. Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# 2. CSS "FORZA BRUTA" + FIX ANTI-SBIADIMENTO
st.markdown("""
<style>
    /* ELIMINA L'EFFETTO SBIADITO (FANTASMA) DURANTE IL RERUN */
    [data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
    }
    div[data-testid="stAppViewBlockContainer"] > section:first-child {
        opacity: 1 !important;
    }
    .stApp {
        opacity: 1 !important;
    }

    /* Ripristino pulsante sidebar */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    [data-testid="stHeader"] button { color: #555 !important; visibility: visible !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    
    table { margin: auto; width: 100%; border-collapse: collapse; text-align: center; }
    th { font-size: 36px !important; background-color: #f0f2f6 !important; color: #000 !important; height: 80px; }
    td { font-size: 32px !important; font-weight: bold !important; height: 80px; vertical-align: middle !important; text-align: center !important; }
    .stTitle { text-align: center; font-size: 60px !important; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- STATO ---
PALETTE_COLORI = ["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb", "#d1f2eb", "#f3d8e6", "#ffeeba"]
if 'gara_avviata' not in st.session_state: st.session_state.gara_avviata = False
if 'log' not in st.session_state: st.session_state.log = []
if 'risolti' not in st.session_state: st.session_state.risolti = {}

# --- CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Gara")
    c1, c2 = st.columns(2)
    with c1:
        num_squadre = st.number_input("1) Numero squadre", min_value=2, value=5)
        nomi_input = st.text_area("2) Nomi", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    with c2:
        num_problemi = st.number_input("3) Problemi", min_value=1, value=10)
        punti_partenza = st.number_input("Punti iniziali", value=200)
        durata_minuti = st.number_input("4) Durata (min)", min_value=1, value=90)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        st.session_state.squadre = {n: {"PUNTI": punti_partenza} for n in lista_nomi}
        st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
        st.session_state.risolti = {n: [] for n in lista_nomi}
        st.session_state.fine_gara = datetime.now() + timedelta(minutes=durata_minuti)
        ciclo = itertools.cycle(PALETTE_COLORI)
        st.session_state.colori_squadre = {n: next(ciclo) for n in lista_nomi}
        st.session_state.gara_avviata = True
        st.rerun()

# --- GARA ---
else:
    if st.sidebar.button("⚠️ Reset Totale"):
        st.session_state.gara_avviata = False
        st.rerun()

    st.sidebar.header("Pannello Giudice")
    squadra_scelta = st.sidebar.selectbox("Squadra", list(st.session_state.squadre.keys()))
    prob_disp = [p for p in st.session_state.problemi.keys() if p not in st.session_state.risolti[squadra_scelta]]
    
    if prob_disp:
        prob_scelto = st.sidebar.selectbox("Problema", prob_disp)
        esito = st.sidebar.radio("Esito", ["Corretta ✅", "Sbagliata ❌"])
        if st.sidebar.button("Registra"):
            if esito == "Corretta ✅":
                st.session_state.squadre[squadra_scelta]["PUNTI"] += st.session_state.problemi[prob_scelto]
                st.session_state.risolti[squadra_scelta].append(prob_scelto)
                st.session_state.problemi[prob_scelto] = max(10, st.session_state.problemi[prob_scelto] - 2)
            else:
                st.session_state.squadre[squadra_scelta]["PUNTI"] -= 5
            st.rerun()

    # Calcolo tempo
    sec = (st.session_state.fine_gara - datetime.now()).total_seconds()
    
    if sec > 120:
        st.title("🏆 CLASSIFICA")
        m, s = divmod(int(sec), 60)
        st.info(f"⏱️ Fine gara tra: {m:02d}:{s:02d}")
        
        df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
        df.columns = ["SQUADRA", "PUNTI"]
        df = df.sort_values(by="PUNTI", ascending=False)
        tab_html = df.style.apply(lambda r: [f'background-color: {st.session_state.colori_squadre.get(r["SQUADRA"])};', ''], axis=1).hide(axis="index").to_html()
        st.write(tab_html, unsafe_allow_html=True)
            
    elif sec > 0:
        # FASE BUIO TOTALE
        m, s = divmod(int(sec), 60)
        st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 160px; font-weight: bold;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
        
    else:
        st.title("🏆 CLASSIFICA FINALE")
        st.error("⌛ GARA TERMINATA!")
        df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
        df.columns = ["SQUADRA", "PUNTI"]
        df = df.sort_values(by="PUNTI", ascending=False)
        tab_html = df.style.apply(lambda r: [f'background-color: {st.session_state.colori_squadre.get(r["SQUADRA"])};', ''], axis=1).hide(axis="index").to_html()
        st.write(tab_html, unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
