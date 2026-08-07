import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.data_manager import get_fact_data, get_dimension_data, add_supervisor, add_cuadrilla, delete_cuadrilla

# Metas por hora (kg/hora)
METAS_VELOCIDAD = {
    'A02': 2500, # Troquelado
    'A03': 7000, # Envasado
    'A04': 6300  # Empaque
}

RENDIMIENTOS_TEORICOS = {
    'Tubo': 50.0, 'Tentaculos': 12.5, 'Aleta': 20.0, 'Nucas': 8.0, 'Anillas': 19.0,
    'Recortes': 12.0, 'Boton': 2.0, 'Cono': 1.5, 'Reproductor': 2.5
}

def render_dashboard():
    st.markdown("<h1 style='text-align: center; color: #4fc3f7;'>Dashboard Gerencial - Rendimiento de Planta</h1>", unsafe_allow_html=True)
    
    # Filtros Globales
    st.markdown("### 🔍 Filtros Globales")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_date = st.date_input("Seleccionar Fecha de Producción", datetime.today())
        date_str = selected_date.strftime('%Y-%m-%d')
    with f_col2:
        turno_filter = st.selectbox("Filtrar por Turno", ["Todos", "Día", "Noche"])
        
    df_fact = get_fact_data(date_str)
    dims = get_dimension_data()
    cuadrillas_df = dims.get('cuadrillas', pd.DataFrame())
    areas_df = dims.get('areas', pd.DataFrame())
    
    if not df_fact.empty and turno_filter != "Todos":
        if 'Turno' in df_fact.columns:
            df_fact = df_fact[df_fact['Turno'] == turno_filter]
        else:
            st.warning("Los registros antiguos no tienen turno asignado.")
            
    # Convert numeric columns
    if not df_fact.empty:
        numeric_cols = ['Kilos_Ingreso', 'Kilos_Descuento_Calidad', 'Kilos_Aumento', 'Kilos_Conforme', 'Cantidad_Reportada', 'Horas_Proceso', 'Num_Operarios']
        for col in numeric_cols:
            if col in df_fact.columns:
                df_fact[col] = pd.to_numeric(df_fact[col], errors='coerce').fillna(0)
    
    tab_general, tab_cuadrillas, tab_gestion_cuadrillas, tab_gestion_supervisores = st.tabs([
        "📊 Rendimiento General", 
        "👥 Rendimiento de Cuadrillas", 
        "🦑 Gestión de Cuadrillas", 
        "👤 Gestión de Supervisores"
    ])
    
    with tab_general:
        if df_fact.empty:
            st.info("No hay datos de producción registrados para los filtros seleccionados.")
        else:
            # Separamos data por area
            df_recepcion = df_fact[df_fact['ID_Area'] == 'A01']
            df_troquelado = df_fact[df_fact['ID_Area'] == 'A02']
            df_envasado = df_fact[df_fact['ID_Area'] == 'A03']
            df_empaque = df_fact[df_fact['ID_Area'] == 'A04']
            
            # 1. KPIs Principales (Recepción)
            st.markdown("### 📊 Materia Prima (Recepción)")
            total_ingreso = df_recepcion['Kilos_Ingreso'].sum() if not df_recepcion.empty else 0
            total_aumento = df_recepcion['Kilos_Aumento'].sum() if not df_recepcion.empty and 'Kilos_Aumento' in df_recepcion.columns else 0
            kilos_netos = total_ingreso + total_aumento
            merma_teorica = kilos_netos * 0.095 # 9.5%
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ingreso Bruto", f"{total_ingreso:,.0f} kg")
            col2.metric("Aumento (Regalo)", f"{total_aumento:,.0f} kg", delta=f"+{(total_aumento/total_ingreso*100 if total_ingreso>0 else 0):.1f}%")
            col3.metric("Materia Prima Neta", f"{kilos_netos:,.0f} kg")
            col4.metric("Merma Teórica", f"{merma_teorica:,.0f} kg", delta="-9.5%", delta_color="normal")
            
            st.markdown("---")
            
            # 2. Análisis de Velocidad y Cuellos de Botella
            st.markdown("### ⚠️ Monitoreo de Velocidad y Cuellos de Botella")
            
            col_v1, col_v2, col_v3 = st.columns(3)
            
            def calc_velocidad(df, col_peso):
                horas = df['Horas_Proceso'].sum() if not df.empty and 'Horas_Proceso' in df.columns else 0
                peso = df[col_peso].sum() if not df.empty and col_peso in df.columns else 0
                return peso / horas if horas > 0 else 0
                
            vel_troquelado = calc_velocidad(df_troquelado, 'Kilos_Conforme')
            vel_envasado = calc_velocidad(df_envasado, 'Cantidad_Reportada')
            vel_empaque = calc_velocidad(df_empaque, 'Kilos_Conforme')
            
            def mostrar_velocidad(col, area, actual, meta):
                if actual > 0:
                    color = "normal" if actual <= meta else "inverse"
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
                    'Produccion': [
                        df_troquelado['Kilos_Conforme'].sum() if not df_troquelado.empty else 0, 
                        df_envasado['Cantidad_Reportada'].sum() if not df_envasado.empty else 0, 
                        df_empaque['Kilos_Conforme'].sum() if not df_empaque.empty else 0
                    ]
                })
                fig1 = px.bar(prod_area, x='Area', y='Produccion', color='Area', template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig1, use_container_width=True)
                
            with c_graph2:
                st.write("Distribución de Envasado por Producto")
                if not df_envasado.empty and 'Cantidad_Reportada' in df_envasado.columns and df_envasado['Cantidad_Reportada'].sum() > 0:
                    env_group = df_envasado.groupby('Producto_Envasado')['Cantidad_Reportada'].sum().reset_index()
                    fig2 = px.pie(env_group, values='Cantidad_Reportada', names='Producto_Envasado', template="plotly_dark", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
                    fig2.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Sin registros de Envasado.")

            st.markdown("---")
            st.subheader("Registros Detallados (Tabla)")
            st.dataframe(df_fact, use_container_width=True)
            
    with tab_cuadrillas:
        st.markdown("### 👥 Desempeño por Cuadrillas")
        if df_fact.empty:
            st.info("No hay datos de producción registrados para los filtros seleccionados.")
        else:
            # Filter areas that use cuadrillas (A02, A03, A04, A05, etc.)
            df_cuad_fact = df_fact.dropna(subset=['ID_Cuadrilla'])
            if df_cuad_fact.empty:
                st.info("No hay datos asociados a cuadrillas para este día.")
            else:
                # Merge with cuadrillas dict for names
                cuad_dict = dict(zip(cuadrillas_df['ID_Cuadrilla'], cuadrillas_df['Nombre_Lider'])) if not cuadrillas_df.empty else {}
                df_cuad_fact['Nombre_Cuadrilla'] = df_cuad_fact['ID_Cuadrilla'].map(cuad_dict).fillna(df_cuad_fact['ID_Cuadrilla'])
                
                # Combine kilos (Kilos_Conforme for troquelado/empaque, Cantidad_Reportada for envasado)
                def get_kilos(row):
                    if row['ID_Area'] == 'A03': return row.get('Cantidad_Reportada', 0)
                    return row.get('Kilos_Conforme', 0)
                df_cuad_fact['Produccion_Total_KG'] = df_cuad_fact.apply(get_kilos, axis=1)
                
                # Group by Cuadrilla
                cuad_metrics = df_cuad_fact.groupby(['ID_Cuadrilla', 'Nombre_Cuadrilla']).agg(
                    Total_Kilos=('Produccion_Total_KG', 'sum'),
                    Horas_Totales=('Horas_Proceso', 'sum'),
                    Operarios_Promedio=('Num_Operarios', 'mean')
                ).reset_index()
                
                cuad_metrics['Operarios_Promedio'] = cuad_metrics['Operarios_Promedio'].round(1)
                cuad_metrics['Velocidad (kg/h)'] = (cuad_metrics['Total_Kilos'] / cuad_metrics['Horas_Totales']).fillna(0).round(2)
                cuad_metrics['Eficiencia (kg/operario-hora)'] = (cuad_metrics['Total_Kilos'] / (cuad_metrics['Horas_Totales'] * cuad_metrics['Operarios_Promedio'])).fillna(0).round(2)
                
                st.dataframe(cuad_metrics, use_container_width=True)
                
                st.markdown("#### Comparativa de Eficiencia por Cuadrilla (kg/operario-hora)")
                if not cuad_metrics.empty:
                    fig_cuad = px.bar(cuad_metrics, x='Nombre_Cuadrilla', y='Eficiencia (kg/operario-hora)', color='Nombre_Cuadrilla', template="plotly_dark")
                    st.plotly_chart(fig_cuad, use_container_width=True)
                    
    with tab_gestion_cuadrillas:
        st.markdown("### 🦑 Gestión de Cuadrillas")
        st.dataframe(cuadrillas_df, use_container_width=True)
        
        st.markdown("#### Agregar Nueva Cuadrilla")
        with st.form("form_add_cuadrilla"):
            c_nombre = st.text_input("Nombre de la Cuadrilla o Líder")
            c_operarios = st.number_input("Número de Operarios Típico", min_value=1, step=1, value=10)
            c_area = st.selectbox("Área Asociada", ["Troquelado", "Envasado", "Empaque", "Saneamiento", "Varias"])
            submitted_add_c = st.form_submit_button("Agregar Cuadrilla", use_container_width=True)
            if submitted_add_c:
                if c_nombre.strip() == "":
                    st.error("El nombre no puede estar vacío.")
                else:
                    add_cuadrilla(c_nombre, c_operarios, c_area)
                    st.success("Cuadrilla agregada exitosamente.")
                    st.rerun()
                    
        st.markdown("#### Eliminar Cuadrilla")
        with st.form("form_del_cuadrilla"):
            if not cuadrillas_df.empty:
                opciones = {f"{r['ID_Cuadrilla']} - {r.get('Nombre_Lider','')}": r['ID_Cuadrilla'] for _, r in cuadrillas_df.iterrows()}
                c_del_label = st.selectbox("Seleccione la cuadrilla a eliminar", list(opciones.keys()))
                c_del_id = opciones.get(c_del_label)
                submitted_del_c = st.form_submit_button("Eliminar Cuadrilla", use_container_width=True)
                if submitted_del_c:
                    delete_cuadrilla(c_del_id)
                    st.success(f"Cuadrilla {c_del_id} eliminada exitosamente.")
                    st.rerun()
            else:
                st.info("No hay cuadrillas para eliminar.")
                
    with tab_gestion_supervisores:
        st.markdown("### 👤 Gestión de Supervisores y Usuarios")
        st.info("Los nuevos supervisores podrán acceder inmediatamente usando el usuario y contraseña asignados.")
        
        roles_df = pd.DataFrame()
        try:
            from utils.data_manager import MASTER_EXCEL_FILE
            roles_df = pd.read_excel(MASTER_EXCEL_FILE, sheet_name='Dim_Roles')
            st.dataframe(roles_df[['ID_Rol', 'Username', 'Nombre', 'ID_Area', 'Nivel_Acceso']], use_container_width=True)
        except Exception as e:
            st.error(f"Error cargando roles: {e}")
            
        st.markdown("#### Agregar Nuevo Supervisor")
        with st.form("form_add_supervisor"):
            s_usuario = st.text_input("Usuario de Acceso (Login)")
            s_password = st.text_input("Contraseña", type="password")
            s_nombre = st.text_input("Nombre Completo")
            
            # Map area IDs to names for selector
            area_options = {"A01": "Recepción", "A02": "Troquelado", "A03": "Envasado", "A04": "Empaque", "A05": "Saneamiento"}
            if not areas_df.empty:
                area_options = {row['ID_Area']: row['Nombre_Area'] for _, row in areas_df.iterrows() if row['ID_Area'] != 'A00'}
            
            s_area_name = st.selectbox("Área Asignada", list(area_options.values()))
            s_area_id = [k for k, v in area_options.items() if v == s_area_name][0]
            
            submitted_add_s = st.form_submit_button("Registrar Supervisor", use_container_width=True)
            if submitted_add_s:
                if s_usuario.strip() == "" or s_password.strip() == "" or s_nombre.strip() == "":
                    st.error("Todos los campos son obligatorios.")
                else:
                    # Check if username exists
                    if not roles_df.empty and s_usuario in roles_df['Username'].values:
                        st.error("El usuario ya existe. Por favor elija otro.")
                    else:
                        add_supervisor(s_usuario, s_password, s_nombre, s_area_id)
                        st.success(f"Supervisor '{s_nombre}' agregado exitosamente.")
                        st.rerun()
