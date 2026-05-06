import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools 

# 1. Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# 2. CSS per centraggio e pulizia sidebar
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

# --- INIZIALIZZAZIONE STATO ---
if 'gara_avviata' not in st.session_state: 
    st.session_state.gara_avviata = False

PALETTE = ["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb", "#d1f2eb", "#f3d8e6", "#ffeeba"]

# --- SCHERMATA INIZIALE: CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Gara")
    c1, c2 = st.columns(2)
    with c1:
        num_s = st.number_input("Numero squadre", min_value=2, value=5)
        nomi = st.text_area("Nomi (uno per riga)", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    with c2:
        punti_p = st.number_input("Punti di partenza", value=200)
        durata = st.number_input("Durata (minuti)", min_value=1, value=90)
    
    if st.button("🚀 AVVIA GARA"):
        lista = [n.strip() for n in nomi.split("\n") if n.strip()]
        if len(lista) > 0:
            st.session_state.squadre = {n: {"PUNTI": punti_p} for n in lista}
            st.session_state.risolti = {n: [] for n in lista}
            st.session_state.fine = datetime.now() + timedelta(minutes=durata)
            ciclo = itertools.cycle(PALETTE)
            st.session_state.colori = {n: next(ciclo) for n in lista}
            st.session_state.gara_avviata = True
            st.rerun()
        else:
            st.error("Inserisci almeno un nome!")

# --- SCHERMATA GARA: CLASSIFICA E TIMER ---
else:
    # Pulsante di Reset nella Sidebar
    if st.sidebar.button("⚠️ Reset Totale"):
        st.session_state.gara_avviata = False
        st.rerun()
    
    # Pannello inserimento dati
    st.sidebar.header("Pannello Giudice")
    sq = st.sidebar.selectbox("Squadra", list(st.session_state.squadre.keys()))
    esito = st.sidebar.radio("Esito", ["✅ Corretta", "❌ Sbagliata"])
    if st.sidebar.button("Registra"):
        if esito == "✅ Corretta": 
            st.session_state.squadre[sq]["PUNTI"] += 20
        else: 
            st.session_state.squadre[sq]["PUNTI"] -= 5
        st.rerun()

    # --- CALCOLI (Solo se la gara è avviata!) ---
    adesso = datetime.now()
    sec_rimanenti = (st.session_state.fine - adesso).total_seconds()
    
    # Preparazione tabella HTML
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
    df.columns = ["SQUADRA", "PUNTI"]
    df = df.sort_values(by="PUNTI", ascending=False)
    
    html_classifica = (df.style
                       .apply(lambda r: [f'background-color: {st.session_state.colori.get(r["SQUADRA"])};', ''], axis=1)
                       .hide(axis="index")
                       .to_html())

    # --- VISUALIZZAZIONE ---
    placeholder = st.empty()

    with placeholder.container():
        if sec_rimanenti > 120:
            # FASE NORMALE
            st.title("🏆 CLASSIFICA LIVE")
            m, s = divmod(int(sec_rimanenti), 60)
            st.info(f"⏱️ Tempo rimanente: {m:02d}:{s:02d}")
            st.write(html_classifica, unsafe_allow_html=True)
            
        elif sec_rimanenti > 0:
            # FASE BUIO (Ultimi 2 minuti)
            m, s = divmod(int(sec_rimanenti), 60)
            st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 160px; font-weight: bold; text-align: center;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
            
        else:
            # FINE GARA
            st.title("🏆 CLASSIFICA FINALE")
            st.error("⌛ GARA TERMINATA!")
            st.write(html_classifica, unsafe_allow_html=True)

    # Refresh automatico ogni secondo
    time.sleep(1)
    st.rerun()
