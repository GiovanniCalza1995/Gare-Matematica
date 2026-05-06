import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools 

# 1. Configurazione Pagina (Deve essere il primo comando Streamlit)
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# 2. CSS "FORZA BRUTA" PER CENTRAGGIO E SIDEBAR
st.markdown("""
<style>
    /* Ripristino pulsante sidebar */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    [data-testid="stHeader"] button { color: #555 !important; visibility: visible !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    div[data-testid="stTable"] table { margin-left: auto; margin-right: auto; width: 100% !important; }
    
    /* Centraggio Totale Verticale e Orizzontale */
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        height: 80px !important;
        padding: 0 !important; 
        vertical-align: middle !important;
        text-align: center !important;
    }
    
    /* Forza il centro su ogni elemento interno alla cella */
    div[data-testid="stTable"] td *, div[data-testid="stTable"] th * {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        margin: 0 auto !important;
        width: 100% !important;
        height: 100% !important;
    }

    thead th { font-size: 36px !important; background-color: #f0f2f6 !important; color: #000; }
    tbody td { font-size: 32px !important; font-weight: bold !important; }
    .stTitle { text-align: center; font-size: 60px !important; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- LOGICA GARA ---
PALETTE_COLORI = ["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb", "#d1f2eb", "#f3d8e6", "#ffeeba"]

if 'gara_avviata' not in st.session_state:
    st.session_state.gara_avviata = False
if 'log' not in st.session_state:
    st.session_state.log = []
if 'risolti' not in st.session_state:
    st.session_state.risolti = {}

if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Gara")
    c1, c2 = st.columns(2)
    with c1:
        num_squadre = st.number_input("1) Numero squadre", min_value=2, max_value=50, value=5)
        nomi_input = st.text_area("2) Nomi squadre", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    with c2:
        num_problemi = st.number_input("3) Numero problemi", min_value=1, max_value=50, value=10)
        punti_partenza = st.number_input("Punti iniziali", value=200)
        durata_minuti = st.number_input("4) Durata (minuti)", min_value=1, max_value=300, value=90)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        if len(lista_nomi) != num_squadre:
            st.error(f"Errore nomi!")
        else:
            st.session_state.squadre = {n: {"PUNTI": punti_partenza} for n in lista_nomi}
            st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
            st.session_state.risolti = {n: [] for n in lista_nomi}
            st.session_state.fine_gara = datetime.now() + timedelta(minutes=durata_minuti)
            ciclo = itertools.cycle(PALETTE_COLORI)
            st.session_state.colori_squadre = {n: next(ciclo) for n in lista_nomi}
            st.session_state.gara_avviata = True
            st.rerun()
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
            punti_att = st.session_state.problemi[prob_scelto]
            if esito == "Corretta ✅":
                st.session_state.squadre[squadra_scelta]["PUNTI"] += punti_att
                st.session_state.risolti[squadra_scelta].append(prob_scelto)
                st.session_state.problemi[prob_scelto] = max(10, punti_att - 2)
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} OK")
            else:
                st.session_state.squadre[squadra_scelta]["PUNTI"] -= 5
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERR")
            st.rerun()

    # Preparazione Tabella
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
    df.columns = ["SQUADRA", "PUNTI"]
    df = df.sort_values(by="PUNTI", ascending=False)
    
    def style_c(col):
        return [f'background-color: {st.session_state.colori_squadre.get(n, "#fff")}; color: #000; text-align: center;' for n in col]
    
    tabella = df.style.apply(style_c, subset=['SQUADRA']).set_properties(**{'text-align': 'center'}).hide(axis="index")

    # Visualizzazione Temporizzata
    rimanente = st.session_state.fine_gara - datetime.now()
    sec = rimanente.total_seconds()
    
    if sec > 120:
        st.title("🏆 CLASSIFICA")
        m, s = divmod(int(sec), 60)
        st.info(f"⏱️ Fine gara tra: {m:02d}:{s:02d}")
        st.table(tabella)
    elif sec > 0:
        m, s = divmod(int(sec), 60)
        st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 120px; font-weight: bold;'>⏱️ {m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
    else:
        st.title("🏆 CLASSIFICA FINALE")
        st.error("⌛ GARA TERMINATA!")
        st.table(tabella)

    time.sleep(1)
    st.rerun()
