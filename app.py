import streamlit as st
# Force reload for styling and logic 2
from views.login import render_login
from views.supervisor_form import render_supervisor_form
from views.dashboard import render_dashboard

st.set_page_config(page_title="PyS Integrados - Rendimiento", page_icon="🐟", layout="wide")

# Global CSS Theme
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0b192c 0%, #1e3c72 100%);
    color: #e0f7fa;
}

/* Glassmorphism containers */
div[data-testid="stForm"], .form-container {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    margin-bottom: 20px;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #81d4fa !important;
}

/* Buttons */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #0288d1 0%, #03a9f4 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(3, 169, 244, 0.4);
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(3, 169, 244, 0.6);
}

/* Metrics */
div[data-testid="stMetricValue"] {
    color: #fff !important;
    font-size: 2rem !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 1rem !important;
}
</style>
""", unsafe_allow_html=True)
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    render_login()
else:
    user_info = st.session_state.get('user_info', {})
    nivel_acceso = user_info.get('Nivel_Acceso', '')
    
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"Bienvenido/a, **{user_info.get('Nombre', 'Usuario')}**")
    with col2:
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_info'] = {}
            st.rerun()
            
    st.markdown("---")
    
    if nivel_acceso == 'Gerencia':
        render_dashboard()
    else:
        render_supervisor_form()
