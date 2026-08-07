import streamlit as st
from utils.data_manager import authenticate

def render_login():
    st.markdown("""
        <style>
        .login-box {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            text-align: center;
            margin-top: 50px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("PyS INTEGRADOS")
        st.subheader("Sistema de Rendimiento")
        
        username = st.text_input("Usuario").strip()
        password = st.text_input("Contraseña", type="password").strip()
        
        if st.button("Iniciar Sesión", use_container_width=True):
            is_auth, user_info = authenticate(username, password)
            if is_auth:
                st.session_state['authenticated'] = True
                st.session_state['user_info'] = user_info
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.markdown('</div>', unsafe_allow_html=True)
