import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools 

# Configurazione Pagina
st.set_page_config(page_title="Classifica Gara Matematica", layout="wide")

# --- CSS AVANZATO PER IL CENTRAGGIO ASSOLUTO ---
st.markdown("""
    <style>
    /* Nasconde l'header di Streamlit */
    header { visibility: hidden !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    /* Regola gli spazi e centra la tabella nel monitor */
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    div[data-testid="stTable"] table { margin-left: auto; margin-right: auto; width: 100% !important; }
    
    /* REGOLE CELLE: Altezza fissa e rimozione spaziature che sbilanciano */
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        height: 80px !important;
        padding: 0 !important; 
        vertical-align: middle !important;
        text-align: center !important; /* Forza il centro orizzontale nella cella */
    }
    
    /* LA MAGIA FLEXBOX CORRETTA: Centra ovunque i contenitori interni */
    div[data-testid="stTable"] th div, div[data-testid="stTable"] td div {
        display: flex !important;
        align-items: center !important; /* Centro verticale */
        justify-content: center !important; /* Centro orizzontale */
        height: 100% !important;
        width: 100% !important; /* Obbliga il div a occupare tutta la cella */
        margin: 0 auto !important;
        text-align: center !important;
    }
    
    /* Stili specifici per l'INTESTAZIONE */
    thead th {
        font-size: 36px !important;
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    /* Stili specifici per le SQUADRE e i PUNTI */
    tbody td, tbody th {
        font-size: 32px !important;
        font-weight: bold !important;
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
        testo_squadre_base = "Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E"
        nomi_input = st.text_area("2) Nomi squadre (uno per riga)", value=testo_squadre_base)
    with col_conf2:
        num_problemi = st.number_input("3) Numero problemi", min_value=1, max_value=50, value=10)
        punti_partenza = st.number_input("Punti iniziali", value=200)
        durata_minuti = st.number_input("4) Durata (minuti)", min_value=1, max_value=300, value=90)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        if len(lista_nomi) != num_squadre:
            st.error(f"Inseriti {len(lista_nomi)} nomi per {num_squadre} squadre.")
        else:
            st.session_state.squadre = {n: {"PUNTI": punti_partenza} for n in lista_nomi}
            st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
            st.session_state.risolti = {n: [] for n in lista_nomi}
            st.session_state.fine_gara = datetime.now() + timedelta(minutes=durata_minuti)
            
            # ASSEGNAZIONE COLORI
            ciclo_colori = itertools.cycle(PALETTE_COLORI)
            st.session_state.colori_squadre = {n: next(ciclo_colori) for n in lista_nomi}
            
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
                st.session_state.squadre[squadra_scelta]["PUNTI"] += punti_attuali
                st.session_state.risolti[squadra_scelta].append(prob_scelto)
                st.session_state.problemi[prob_scelto] = max(10, punti_attuali - 2)
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} CORRETTO {prob_scelto}")
            else:
                st.session_state.squadre[squadra_scelta]["PUNTI"] -= 5
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERRORE {prob_scelto}")
            st.rerun()
    else:
        st.sidebar.success("Tutti i problemi risolti!")

    # --- CREAZIONE TABELLA CON COLORI DINAMICI E CENTRAGGIO FORZATO ---
    df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index')
    df = df.sort_values(by="PUNTI", ascending=False)
    
    df = df.reset_index()
    df.columns = ["SQUADRA", "PUNTI"]
    
    def colora_squadre(colonna):
        # Aggiunto text-align: center direttamente nello stile in linea di Pandas
        return [f'background-color: {st.session_state.colori_squadre.get(nome, "#ffffff")}; color: #000000; text-align: center;' for nome in colonna]

    # Applichiamo i colori, forziamo l'allineamento su tutta la tabella e nascondiamo l'indice
    tabella_stilizzata = (df.style
                          .apply(colora_squadre, subset=['SQUADRA'])
                          .set_properties(**{'text-align': 'center'})
                          .hide(axis="index"))

    st.table(tabella_stilizzata)

    # --- CRONOLOGIA ---
    st.write("---")
    st.subheader("Ultimi aggiornamenti")
    for msg in reversed(st.session_state.log[-5:]):
        st.write(f"• {msg}")
    
    # Refresh automatico invisibile per il timer
    time.sleep(1)
    st.rerun()
