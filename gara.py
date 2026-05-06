import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import time
import itertools

# 1. Configurazione Pagina
st.set_page_config(page_title="Gara Matematica Live", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CSS per centraggio e stile
st.markdown("""
<style>
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; color: transparent !important; }
    .main .block-container { max-width: 1000px; padding-top: 1rem; }
    table { margin: auto; width: 100%; border-collapse: collapse; text-align: center; }
    th { font-size: 30px !important; background-color: #f0f2f6 !important; height: 60px; }
    td { font-size: 35px !important; font-weight: bold !important; height: 80px; border-bottom: 1px solid #ddd; }
    .stTitle { text-align: center; font-size: 60px !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI DI SINCRONIZZAZIONE ---
def carica_tutto():
    try:
        # Carichiamo sia la classifica che lo stato dei problemi
        df = conn.read(worksheet="Classifica", ttl=0)
        dp = conn.read(worksheet="Problemi", ttl=0)
        return df, dp
    except:
        return pd.DataFrame(), pd.DataFrame()

def salva_tutto(df_classifica, df_problemi):
    conn.update(worksheet="Classifica", data=df_classifica)
    conn.update(worksheet="Problemi", data=df_problemi)

# --- LOGICA DI STATO ---
df_classifica, df_problemi = carica_tutto()
gara_attiva = not df_classifica.empty

# --- SETUP INIZIALE ---
if not gara_attiva:
    st.title("⚙️ Setup Gara")
    c1, c2 = st.columns(2)
    with c1:
        nomi_raw = st.text_area("Squadre", "Squadra 1\nSquadra 2")
        num_p = st.number_input("Numero Problemi", min_value=1, value=15)
    with c2:
        punti_p = st.number_input("Punti iniziali", value=200)
    
    if st.button("🚀 AVVIA"):
        lista = [n.strip() for n in nomi_raw.split("\n") if n.strip()]
        ciclo = itertools.cycle(["#d4edda", "#fff3cd", "#d1ecf1", "#f8d7da", "#e2e3e5", "#cce5ff", "#e8d5cb"])
        
        df_c = pd.DataFrame({"SQUADRA": lista, "PUNTI": [punti_p]*len(lista), "COLORE": [next(ciclo) for _ in lista]})
        df_p = pd.DataFrame({"ID": [f"P{i+1}" for i in range(num_p)], "VALORE": [20]*num_p})
        
        salva_tutto(df_c, df_p)
        st.rerun()

# --- GARA ---
else:
    st.sidebar.header("🕹️ Pannello Giudice")
    
    # 1. Selezione Squadra e Problema
    sq_sel = st.sidebar.selectbox("Squadra", df_classifica["SQUADRA"].tolist())
    prob_sel = st.sidebar.selectbox("Problema", df_problemi["ID"].tolist())
    valore_attuale = int(df_problemi.loc[df_problemi["ID"] == prob_sel, "VALORE"].values[0])
    
    st.sidebar.write(f"Valore attuale {prob_sel}: **{valore_attuale} pt**")

    # TASTI AZIONE
    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("✅ CORRETTA"):
        # SALVIAMO IL BACKUP PRIMA DI MODIFICARE (per l'Annulla)
        st.session_state.backup_c = df_classifica.copy()
        st.session_state.backup_p = df_problemi.copy()
        
        df_classifica.loc[df_classifica["SQUADRA"] == sq_sel, "PUNTI"] += valore_attuale
        df_problemi.loc[df_problemi["ID"] == prob_sel, "VALORE"] = max(10, valore_attuale - 2)
        salva_tutto(df_classifica, df_problemi)
        st.rerun()

    if col2.button("❌ ERRATA"):
        st.session_state.backup_c = df_classifica.copy()
        st.session_state.backup_p = df_problemi.copy()
        
        df_classifica.loc[df_classifica["SQUADRA"] == sq_sel, "PUNTI"] -= 5
        salva_tutto(df_classifica, df_problemi)
        st.rerun()

    st.sidebar.markdown("---")
    
    # 2. TASTO ANNULLA (Il cuore della tua richiesta)
    if "backup_c" in st.session_state:
        if st.sidebar.button("⏪ ANNULLA ULTIMA AZIONE"):
            salva_tutto(st.session_state.backup_c, st.session_state.backup_p)
            del st.session_state.backup_c # Rimuoviamo per non annullare due volte la stessa cosa
            st.sidebar.warning("Azione annullata!")
            time.sleep(1)
            st.rerun()

    if st.sidebar.button("⚠️ RESET"):
        if st.sidebar.checkbox("Confermo"):
            conn.update(worksheet="Classifica", data=pd.DataFrame())
            conn.update(worksheet="Problemi", data=pd.DataFrame())
            st.rerun()

    # --- VISUALIZZAZIONE PC ---
    st.title("🏆 CLASSIFICA LIVE")
    df_proiettata = df_classifica.sort_values(by="PUNTI", ascending=False)
    html = (df_proiettata.style
            .apply(lambda r: [f'background-color: {r["COLORE"]}; color: black;', ''], axis=1, subset=["SQUADRA", "PUNTI"])
            .hide(axis="index").to_html())
    st.write(html, unsafe_allow_html=True)

    time.sleep(4)
    st.rerun()
