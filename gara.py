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

# --- INIZIALIZZAZIONE ---
if 'gara_avviata' not in st.session_state: 
    st.session_state.gara_avviata = False

PALETTE = ["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb", "#d1f2eb", "#f3d8e6", "#ffeeba"]

# Contenitore principale
schermata_principale = st.empty()

# --- LOGICA DI NAVIGAZIONE ---
with schermata_principale.container():
    if not st.session_state.gara_avviata:
        st.title("⚙️ Configurazione Gara")
        c1, c2 = st.columns(2)
        with c1:
            num_s = st.number_input("1) Numero squadre", min_value=2, value=5)
            nomi = st.text_area("2) Nomi squadre (uno per riga)", value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
            num_p = st.number_input("3) Numero problemi", min_value=1, value=10)
        with c2:
            punti_p = st.number_input("4) Punti di partenza", value=200)
            durata = st.number_input("5) Durata (minuti)", min_value=1, value=90)
        
        if st.button("🚀 AVVIA GARA"):
            lista = [n.strip() for n in nomi.split("\n") if n.strip()]
            if len(lista) == num_s:
                st.session_state.squadre = {n: {"PUNTI": punti_p} for n in lista}
                st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, int(num_p) + 1)}
                st.session_state.risolti = {n: [] for n in lista}
                st.session_state.fine = datetime.now() + timedelta(minutes=durata)
                ciclo = itertools.cycle(PALETTE)
                st.session_state.colori = {n: next(ciclo) for n in lista}
                st.session_state.backup = None # Inizializziamo il backup
                st.session_state.gara_avviata = True
                st.rerun()
            else:
                st.error(f"Errore: hai inserito {len(lista)} nomi per {num_s} squadre!")

    elif st.session_state.gara_avviata:
        # --- CALCOLO DATI ---
        sec_rimanenti = (st.session_state.fine - datetime.now()).total_seconds()
        df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index').reset_index()
        df.columns = ["SQUADRA", "PUNTI"]
        df = df.sort_values(by="PUNTI", ascending=False)
        
        # Stile tabella
        html_classifica = (df.style
                        .apply(lambda r: [f'background-color: {st.session_state.colori.get(r["SQUADRA"])};', ''], axis=1)
                        .hide(axis="index")
                        .to_html())

        # --- VISUALIZZAZIONE GARA ---
        if sec_rimanenti > 120:
            st.title("🏆 CLASSIFICA LIVE")
            m, s = divmod(int(sec_rimanenti), 60)
            st.info(f"⏱️ Tempo rimanente: {m:02d}:{s:02d}")
            st.write(html_classifica, unsafe_allow_html=True)
        elif sec_rimanenti > 0:
            m, s = divmod(int(sec_rimanenti), 60)
            st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #ff4b4b;'>🙈 Classifica nascosta 🙈</h1>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 160px; font-weight: bold; text-align: center;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
        else:
            st.title("🏆 CLASSIFICA FINALE")
            st.error("⌛ GARA TERMINATA!")
            st.write(html_classifica, unsafe_allow_html=True)

# --- SIDEBAR (Pannello Giudice) ---
if st.session_state.gara_avviata:
    st.sidebar.header("🕹️ Pannello Giudice")
    
    # Reset Totale con conferma
    if st.sidebar.button("⚠️ Reset Totale"):
        if st.sidebar.checkbox("Confermo il reset"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.sidebar.markdown("---")
    
    sq = st.sidebar.selectbox("Squadra", list(st.session_state.squadre.keys()))
    disp = [p for p in st.session_state.problemi.keys() if p not in st.session_state.risolti.get(sq, [])]
    
    if disp:
        pb = st.sidebar.selectbox("Problema", disp)
        val_attuale = st.session_state.problemi[pb]
        st.sidebar.write(f"Valore attuale {pb}: **{val_attuale} pt**")
        
        esito = st.sidebar.radio("Esito", ["✅ Corretta", "❌ Sbagliata"])
        
        if st.sidebar.button("Registra"):
            # Salvataggio Backup prima della modifica
            st.session_state.backup = {
                "squadre": {k: v.copy() for k, v in st.session_state.squadre.items()},
                "problemi": st.session_state.problemi.copy(),
                "risolti": {k: list(v) for k, v in st.session_state.risolti.items()}
            }
            
            if esito == "✅ Corretta": 
                st.session_state.squadre[sq]["PUNTI"] += val_attuale
                st.session_state.risolti[sq].append(pb)
                st.session_state.problemi[pb] = max(10, val_attuale - 2)
            else: 
                st.session_state.squadre[sq]["PUNTI"] -= 5
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # TASTO ANNULLA ULTIMA AZIONE
    if st.session_state.get('backup') is not None:
        if st.sidebar.button("⏪ Annulla Ultima Azione"):
            st.session_state.squadre = st.session_state.backup["squadre"]
            st.session_state.problemi = st.session_state.backup["problemi"]
            st.session_state.risolti = st.session_state.backup["risolti"]
            st.session_state.backup = None # Consumiamo il backup
            st.rerun()

    time.sleep(1)
    st.rerun()
