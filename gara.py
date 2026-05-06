# --- CSS AVANZATO PER IL CENTRAGGIO E RIPRISTINO PULSANTE SIDEBAR ---
st.markdown("""
    <style>
    /* Nasconde la barra colorata in alto ma LASCIANDO IL PULSANTE SIDEBAR */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: transparent !important;
    }
    
    /* Rende il pulsante della sidebar visibile e cliccabile */
    [data-testid="stHeader"] button {
        color: #555 !important;
        visibility: visible !important;
    }

    [data-testid="stStatusWidget"] { visibility: hidden !important; }
    
    /* Regola gli spazi e centra la tabella nel monitor */
    .main .block-container { max-width: 900px; padding-top: 1rem; }
    div[data-testid="stTable"] table { margin-left: auto; margin-right: auto; width: 100% !important; }
    
    /* REGOLE CELLE: Altezza fissa e rimozione spaziature */
    div[data-testid="stTable"] th, div[data-testid="stTable"] td {
        height: 80px !important;
        padding: 0 !important; 
        vertical-align: middle !important;
        text-align: center !important;
    }
    
    /* MAGIA FLEXBOX PER CENTRARE TUTTO */
    div[data-testid="stTable"] th div, div[data-testid="stTable"] td div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        width: 100% !important;
        margin: 0 auto !important;
        text-align: center !important;
    }
    
    thead th {
        font-size: 36px !important;
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    tbody td, tbody th {
        font-size: 32px !important;
        font-weight: bold !important;
    }
    
    .stTitle { text-align: center; font-size: 60px !important; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)
