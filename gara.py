import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# --- CSS PER IL DESIGN DELLA TABELLA ---
st.markdown("""
    <style>
    /* Nasconde l'header di Streamlit (cerchietto di caricamento e menu a tendina) */
    header {
        visibility: hidden !important;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
    
    /* Regola gli spazi e centra la tabella */
    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
    }
    div[data-testid="stTable"] table {
        margin-left: auto;
        margin-right: auto;
        width: 100% !important;
    }
    
    /* INTESTAZIONE (Scritta PUNTI in maiuscolo) */
    thead th {
        text-align: center !important;
        font-size: 36px !important; /* Testo ingrandito */
        background-color: #f0f2f6 !important;
    }
    
    /* NOMI DELLE SQUADRE (Celle evidenziate a sinistra) */
    tbody th {
        text-align: center !important;
        font-size: 28px !important;
        background-color: #d1ecf1 !important; /* Colore azzurrino per evidenziarle */
        color: #0c5460 !important; /* Testo scuro abbinato per alta leggibilità */
        font-weight: bold !important;
    }
    
    /* NUMERI (I punteggi effettivi) */
    tbody td {
        text-align: center !important;
        font-size: 32px !important; /* Numeri belli grandi */
        font-weight: bold !important;
    }
    
    .stTitle {
        text-align: center;
        font-size: 60px !important;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE STATO ---
if 'gara_avviata' not in st.session_state:
    st.session_state.gara_avviata = False
if 'log' not in st.session_state:
    st.session_state.log = []
if 'risolti' not in st.session_state:
    st.session_state.risolti = {}

# --- SCHERMATA DI CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Gara")
    col_conf1, col_conf2 = st.columns(2)
    with col_conf1:
        num_squadre = st.number_input("1) Numero squadre", min_value=2, max_value=50, value=5)
        nomi_input = st.text_area("2) Nomi squadre (uno per riga)", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    with col_conf2:
        num_problemi = st.number_input("3) Numero problemi", min_value=1, max_value=50, value=10)
        punti_partenza = st.number_input("Punti iniziali", value=200)
        durata_minuti = st.number_input("4) Durata (minuti)", min_value=1, max_value=300, value=90)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        if len(lista_nomi) != num_squadre:
            st.error(f"Inseriti {len(lista_nomi)} nomi per {num_squadre} squadre.")
        else:
            st.session_state.squadre = {n: {"Punti": punti_partenza} for n in lista_nomi}
            st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
            st.session_state.risolti = {n: [] for n in lista_nomi}
            st.session_state.fine_gara = datetime.now() + timedelta(minutes=durata_minuti)
            st.session_state.gara_avviata = True
            st.rerun()

# --- INTERFACCIA GARA ---
else:
    st.title("🏆 CLASSIFICA")
    
    # --- TIMER ---
    tempo_rimanente = st.session_state.fine_gara - datetime.now()
    if tempo_rimanente.total_seconds() > 0:
        mins, secs = divmod(int(tempo_rimanente.total_seconds()), 60)
        timer_text = f"⏱️ Fine gara tra: {mins:02d}:{secs:02d}"
        if mins < 5:
            st.error(timer_text)
        else:
            st.info(timer_text)
    else:
        st.error("⌛ GARA TERMINATA!")

    # Tasto Reset in Sidebar
    if st.sidebar.button("⚠️ Reset Totale"):
        st.session_state.gara_avviata = False
        st.rerun()

    # --- PANNELLO GIUDICE ---
    st.sidebar.header("Pannello Giudice")
    squadra_scelta = st.sidebar.selectbox("Squadra", list(st.session_state.squadre.keys()))
    
    problemi_disponibili = [p for p in st.session_state.problemi.keys() if p not in st.session_state.risolti[squadra_scelta]]
    
    if problemi_disponibili:
        prob_scelto = st.sidebar.selectbox("Problema", problemi_disponibili)
        esito = st.sidebar.radio("Esito", ["Corretta ✅", "Sbagliata ❌"])

        if st.sidebar.button("Registra"):
            punti_attuali = st.session_state.problemi[prob_scelto]
            if esito == "Corretta ✅":
                st.session_state.squadre[squadra_scelta]["Punti"] += punti_attuali
                st.session_state.risolti[squadra_scelta].append(prob_scelto)
                st.session_state.problemi[prob_scelto] = max(10, punti_attuali - 2)
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} CORRETTO {prob_scelto}")
            else:
                st.session_state.squadre[squadra_scelta]["Punti"] -= 5
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERRORE {prob_scelto}")
            st.rerun()
    else:
        st.sidebar.success("Tutti i problemi risolti!")

    # --- CLASSIFICA CENTRATA E FORMATTATA ---
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index')
    df = df.sort_values(by="Punti", ascending=False)
    
    # Rinominiamo la colonna in maiuscolo
    df = df.rename(columns={"Punti": "PUNTI"})
    
    st.table(df[['PUNTI']])

    # --- CRONOLOGIA ---
    st.write("---")
    st.subheader("Ultimi aggiornamenti")
    for msg in reversed(st.session_state.log[-5:]):
        st.write(f"• {msg}")
    
    # Refresh automatico per il timer
    time.sleep(1)
    st.rerun()
