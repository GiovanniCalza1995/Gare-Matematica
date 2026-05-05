import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Configurazione Pagina
st.set_page_config(page_title="Gestione Gara", layout="wide")

# --- INIZIALIZZAZIONE STATO ---
if 'gara_avviata' not in st.session_state:
    st.session_state.gara_avviata = False
if 'log' not in st.session_state:
    st.session_state.log = []
if 'risolti' not in st.session_state:
    st.session_state.risolti = {} # Dizionario per tracciare chi ha risolto cosa

# --- SCHERMATA DI CONFIGURAZIONE ---
if not st.session_state.gara_avviata:
    st.title("⚙️ Configurazione Nuova Gara")
    
    col_conf1, col_conf2 = st.columns(2)
    
    with col_conf1:
        num_squadre = st.number_input("1) Quante squadre partecipano?", min_value=2, max_value=50, value=5)
        nomi_input = st.text_area("2) Inserisci i nomi delle squadre (uno per riga)", 
                                  value="Squadra A\nSquadra B\nSquadra C\nSquadra D\nSquadra E")
    
    with col_conf2:
        num_problemi = st.number_input("3) Quanti problemi ci sono in totale?", min_value=1, max_value=50, value=10)
        punti_partenza = st.number_input("Punti iniziali per squadra", value=200)
        durata_minuti = st.number_input("4) Durata della gara (minuti)", min_value=1, max_value=300, value=90)

    if st.button("🚀 AVVIA GARA"):
        lista_nomi = [n.strip() for n in nomi_input.split("\n") if n.strip()]
        
        if len(lista_nomi) != num_squadre:
            st.error(f"Attenzione: hai indicato {num_squadre} squadre ma hai inserito {len(lista_nomi)} nomi.")
        else:
            st.session_state.squadre = {n: {"Punti": punti_partenza, "Errori": 0} for n in lista_nomi}
            st.session_state.problemi = {f"Prob {i}": 20 for i in range(1, num_problemi + 1)}
            st.session_state.risolti = {n: [] for n in lista_nomi} # Traccia problemi risolti per ogni squadra
            st.session_state.fine_gara = datetime.now() + timedelta(minutes=durata_minuti)
            st.session_state.gara_avviata = True
            st.rerun()

# --- INTERFACCIA GARA ---
else:
    st.title("🏆 CLASSIFICA")
    
    # --- LOGICA TIMER ---
    tempo_rimanente = st.session_state.fine_gara - datetime.now()
    if tempo_rimanente.total_seconds() > 0:
        mins, secs = divmod(int(tempo_rimanente.total_seconds()), 60)
        timer_text = f"⏱️ Tempo Rimanente: {mins:02d}:{secs:02d}"
        if mins < 5:
            st.error(timer_text) # Rosso se mancano meno di 5 min
        else:
            st.warning(timer_text)
    else:
        st.error("⌛ GARA TERMINATA!")

    # Tasto Reset
    if st.sidebar.button("⚠️ Reset Totale"):
        st.session_state.gara_avviata = False
        st.rerun()

    # --- LATERALE: INSERIMENTO DATI ---
    st.sidebar.header("Pannello Giudice")
    squadra_scelta = st.sidebar.selectbox("Seleziona Squadra", list(st.session_state.squadre.keys()))
    
    # FILTRO: Mostra solo i problemi NON ancora risolti da questa squadra
    problemi_totali = list(st.session_state.problemi.keys())
    problemi_risolti = st.session_state.risolti[squadra_scelta]
    problemi_disponibili = [p for p in problemi_totali if p not in problemi_risolti]
    
    if problemi_disponibili:
        prob_scelto = st.sidebar.selectbox("Seleziona Problema", problemi_disponibili)
        esito = st.sidebar.radio("Esito Risposta", ["Corretta ✅", "Sbagliata ❌"])

        if st.sidebar.button("Registra Risposta"):
            punti_attuali = st.session_state.problemi[prob_scelto]
            
            if esito == "Corretta ✅":
                st.session_state.squadre[squadra_scelta]["Punti"] += punti_attuali
                st.session_state.risolti[squadra_scelta].append(prob_scelto) # BLOCCO: Aggiungi ai risolti
                # Il valore del problema cala per gli altri
                st.session_state.problemi[prob_scelto] = max(10, punti_attuali - 2)
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} risolve {prob_scelto} (+{punti_attuali})")
            else:
                st.session_state.squadre[squadra_scelta]["Punti"] -= 5
                st.session_state.squadre[squadra_scelta]["Errori"] += 1
                st.session_state.log.append(f"{datetime.now().strftime('%H:%M')} - {squadra_scelta} ERRORE su {prob_scelto} (-5)")
            st.rerun()
    else:
        st.sidebar.success(f"La squadra {squadra_scelta} ha risolto tutti i problemi! 🌟")

    # --- CENTRALE: CLASSIFICA E LOG ---
    col1, col2 = st.columns([2, 1])

    with col1:
        df = pd.DataFrame.from_dict(st.session_state.squadre, orient='index')
        df = df.sort_values(by="Punti", ascending=False)
        st.table(df)

    with col2:
        st.subheader("Cronologia")
        for msg in reversed(st.session_state.log[-8:]):
            st.write(msg)

    # Sezione Valore Problemi
    st.divider()
    st.subheader("Valore Attuale Problemi")
    cols_prob = st.columns(min(len(st.session_state.problemi), 10)) 
    for i, (p, val) in enumerate(st.session_state.problemi.items()):
        cols_prob[i % 10].metric(p, f"{val} pt")
    
    # Auto-aggiornamento ogni 30 secondi per il timer
    time.sleep(1)
    st.rerun()
