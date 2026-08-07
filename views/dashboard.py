import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_manager import get_fact_data, get_dimension_data

# Metas por hora (kg/hora)
METAS_VELOCIDAD = {
    'A02': 2500, # Troquelado
    'A03': 7000, # Envasado
    'A04': 6300  # Empaque
}

# Rendimientos teóricos (%) respecto al volumen de materia prima entera
RENDIMIENTOS_TEORICOS = {
    'Tubo': 50.0,
    'Tentaculos': 12.5,
    'Aleta': 20.0,
    'Nucas': 8.0,
    'Anillas': 19.0,
    'Recortes': 12.0,
    'Boton': 2.0,
    'Cono': 1.5,
    'Reproductor': 2.5
}

def render_dashboard():
    st.markdown("<h1 style='text-align: center; color: #4fc3f7;'>Dashboard Gerencial - Rendimiento de Planta</h1>", unsafe_allow_html=True)
    
    df_fact = get_fact_data()
    
    if df_fact.empty:
        st.info("No hay datos de producción registrados aún.")
        return
        
    # Convert numeric columns
    numeric_cols = ['Kilos_Ingreso', 'Kilos_Descuento_Calidad', 'Kilos_Conforme', 'Cantidad_Reportada', 'Horas_Proceso']
    for col in numeric_cols:
        df_fact[col] = pd.to_numeric(df_fact[col], errors='coerce').fillna(0)
        
    # Separamos data por area
    df_recepcion = df_fact[df_fact['ID_Area'] == 'A01']
    df_troquelado = df_fact[df_fact['ID_Area'] == 'A02']
    df_envasado = df_fact[df_fact['ID_Area'] == 'A03']
    df_empaque = df_fact[df_fact['ID_Area'] == 'A04']
    
    # 1. KPIs Principales (Recepción)
    st.markdown("### 📊 Materia Prima (Recepción)")
    total_ingreso = df_recepcion['Kilos_Ingreso'].sum()
    total_descuento = df_recepcion['Kilos_Descuento_Calidad'].sum()
    kilos_netos = total_ingreso - total_descuento
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingreso Bruto", f"{total_ingreso:,.0f} kg")
    col2.metric("Descuentos por Calidad", f"{total_descuento:,.0f} kg", delta=f"-{(total_descuento/total_ingreso*100 if total_ingreso>0 else 0):.1f}%", delta_color="inverse")
    col3.metric("Materia Prima Neta", f"{kilos_netos:,.0f} kg")
    
    st.markdown("---")
    
    # 2. Análisis de Velocidad y Cuellos de Botella
    st.markdown("### ⚠️ Monitoreo de Velocidad y Cuellos de Botella")
    
    col_v1, col_v2, col_v3 = st.columns(3)
    
    def calc_velocidad(df, col_peso):
        horas = df['Horas_Proceso'].sum()
        peso = df[col_peso].sum()
        return peso / horas if horas > 0 else 0
        
    vel_troquelado = calc_velocidad(df_troquelado, 'Kilos_Conforme')
    vel_envasado = calc_velocidad(df_envasado, 'Cantidad_Reportada') # Assuming Cantidad is kg equivalent for now
    vel_empaque = calc_velocidad(df_empaque, 'Kilos_Conforme')
    
    def mostrar_velocidad(col, area, actual, meta):
        if actual > 0:
            porcentaje = (actual / meta) * 100
            color = "normal" if actual <= meta else "inverse" # Rojo si excede
            col.metric(f"Avance {area}", f"{actual:,.0f} kg/h", delta=f"Meta: {meta:,.0f}", delta_color=color)
            if actual > meta:
                col.error(f"¡Saturación! (Cuello de Botella en {area})")
        else:
            col.metric(f"Avance {area}", "Sin datos")
            
    mostrar_velocidad(col_v1, "Troquelado", vel_troquelado, METAS_VELOCIDAD['A02'])
    mostrar_velocidad(col_v2, "Envasado", vel_envasado, METAS_VELOCIDAD['A03'])
    mostrar_velocidad(col_v3, "Empaque", vel_empaque, METAS_VELOCIDAD['A04'])
    
    st.markdown("---")
    
    # 3. Rendimientos y Gráficos
    st.markdown("### 📈 Rendimientos y Productos")
    
    c_graph1, c_graph2 = st.columns(2)
    
    with c_graph1:
        st.write("Producción por Área (kg)")
        prod_area = pd.DataFrame({
            'Area': ['Troquelado', 'Envasado', 'Empaque'],
            'Produccion': [df_troquelado['Kilos_Conforme'].sum(), df_envasado['Cantidad_Reportada'].sum(), df_empaque['Kilos_Conforme'].sum()]
        })
        fig1 = px.bar(prod_area, x='Area', y='Produccion', color='Area', template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
        
    with c_graph2:
        st.write("Distribución de Envasado por Producto")
        if not df_envasado.empty and df_envasado['Cantidad_Reportada'].sum() > 0:
            env_group = df_envasado.groupby('Producto_Envasado')['Cantidad_Reportada'].sum().reset_index()
            fig2 = px.pie(env_group, values='Cantidad_Reportada', names='Producto_Envasado', template="plotly_dark", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sin registros de Envasado.")

    st.markdown("---")
    st.subheader("Registros Detallados (Tabla)")
    st.dataframe(df_fact, use_container_width=True)
