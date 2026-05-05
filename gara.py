import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools # Serve per ciclare i colori infinitamente

# Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# --- CSS PER IL DESIGN E IL CENTRAGGIO ---
st.markdown("""
    <style>
    /* Nasconde l'header di Streamlit */
    header { visibility: hidden !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    /* Regola gli spazi e centra la tabella */
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    div[data-testid="stTable"] table { margin-left: auto; margin-right: auto; width: 100% !important; }
    
    /* INTESTAZIONI COLONNE */
    thead th {
        text-align: center !important;
        font-size: 36px !important;
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    /* CELLE DATI (Testo grande e centrato) */
    tbody td {
        text-align: center !important;
        font-size: 32px !important;
        font-weight: bold !important;
        vertical-align: middle !important;
    }
    
    .stTitle { text-align: center; font-size: 60px !important; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Tavolozza di colori pastello per le squadre
PALETTE_COLORI = [
    "#d4edda", # Verde chiaro
    "#fff3cd", # Giallo/Arancione chiaro
    "#d1ecf1", # Azzurro
    "#f8d7da", # Rosa/Rosso chiaro
    "#e2e3e5", # Grigio
    "#cce5ff", # Blu
    "#e8d5cb", # Pesca
    "#d1f2eb", # Menta
    "#f3d8e6", # Lilla
    "#ffeeba", # Albicocca
]

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
        nomi_input = st.text_area("2) Nomi squadre (uno per riga)", value="Squadra A\nSquadra
