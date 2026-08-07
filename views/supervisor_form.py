import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import get_dimension_data, add_production_record

def render_supervisor_form():
    user_info = st.session_state.get('user_info', {})
    
    st.markdown(f"<h1 style='text-align: center; color: #4fc3f7;'>🐟 Área: {user_info.get('ID_Area', 'General')} 🐙</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #b3e5fc;'>Supervisor: {user_info.get('Nombre', '')} 🌊</h3>", unsafe_allow_html=True)
    
    dims = get_dimension_data()
    lotes = dims.get('lotes', pd.DataFrame())
    productos_envasado = dims.get('productos_envasado', {})
    cuadrillas_df = dims.get('cuadrillas', pd.DataFrame())
    
    # Mapeo de cuadrillas
    lista_cuadrillas_labels = []
    cuadrilla_map = {}
    if not cuadrillas_df.empty:
        for _, row in cuadrillas_df.iterrows():
            id_c = row['ID_Cuadrilla']
            name_c = row.get('Nombre_Lider', f"Cuadrilla {id_c}")
            area_c = row.get('Area', '')
            if pd.notna(area_c) and area_c != '':
                label = f"{id_c} - {name_c} ({area_c})"
            else:
                label = f"{id_c} - {name_c}"
            lista_cuadrillas_labels.append(label)
            cuadrilla_map[label] = id_c
    else:
        lista_cuadrillas_labels = ["Sin Cuadrillas"]
        cuadrilla_map = {"Sin Cuadrillas": None}
    
    username = user_info.get('Username', '')
    
    with st.container():
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        with st.form("registro_produccion"):
            
            st.subheader("📝 Datos Generales")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                fecha = st.date_input("Fecha", datetime.today())
                turno = st.selectbox("Turno", ["Día", "Noche"])
            with col_g2:
                hora_inicio = st.time_input("Hora Inicio")
            with col_g3:
                hora_fin = st.time_input("Hora Fin")
                
            num_operarios = st.number_input("Número de Operarios / Personas", min_value=1, step=1)
            
            st.markdown("---")
            st.subheader("⚙️ Datos de Producción")
            
            # Inicializamos variables para que no den KeyError al guardar
            id_lote = None
            id_cuadrilla = None
            kilos_ingreso = None
            calidad_pota = None
            tamano_promedio = None
            kilos_aumento = None
            kilos_conforme = None
            cant_cajas = None
            cant_dinos = None
            cant_canastillas = None
            rend_saneamiento = None
            prod_envasado = None
            color_envasado = None
            cant_reportada = None
            
            if username == 'recepcion':
                id_lote = st.selectbox("Lote", lotes['ID_Lote'].tolist() if not lotes.empty else ["Sin Lotes"])
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    toneladas_ingreso = st.number_input("Materia Prima Bajada (Toneladas)", min_value=0.0, step=0.1)
                    kilos_ingreso = toneladas_ingreso * 1000
                    calidad_pota = st.selectbox("Calidad de Pota", ["Excelente", "Buena", "Regular", "Mala"])
                with col_r2:
                    kilos_aumento = st.number_input("Aumento / Regalo (Kilos)", min_value=0.0, step=1.0)
                    tamano_promedio = st.selectbox("Tamaño Promedio", ["Pequeño", "Mediano", "Grande", "Jumbo"])
                    
            elif username in ['envasado1', 'empaque1']:
                cuad_label = st.selectbox("🦑 Cuadrilla Responsable", lista_cuadrillas_labels)
                id_cuadrilla = cuadrilla_map.get(cuad_label)
                
                lista_prods = list(productos_envasado.keys())
                prod_envasado = st.selectbox("🦀 Producto", lista_prods)
                
                # Solo mostrar el color para envasado, o también empaque si lo requieren
                if username == 'envasado1':
                    color_envasado = productos_envasado.get(prod_envasado, "")
                    st.info(f"Color de Etiqueta/Envase correspondiente: **{color_envasado}**")
                
                cant_reportada = st.number_input("⚖️ Cantidad Producida (Kilos)", min_value=0.0, step=1.0)
                
            elif username == 'troquelado':
                cuad_label = st.selectbox("🦑 Cuadrilla Responsable", lista_cuadrillas_labels)
                id_cuadrilla = cuadrilla_map.get(cuad_label)
                
                # Filtramos los productos solo para troquelado
                prods_troquelado = [p for p in productos_envasado.keys() if "Anilla" in p or "Recorte" in p or "Boton" in p]
                prod_envasado = st.selectbox("🦀 Producto (Anillas/Botones/Recortes)", prods_troquelado)
                
                kilos_conforme = st.number_input("⚖️ Kilos Conformes Procesados", min_value=0.0, step=1.0)
                
            elif username == 'saneamiento':
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    cant_cajas = st.number_input("Cant. Cajas Limpiadas", min_value=0, step=1)
                with col_s2:
                    cant_dinos = st.number_input("Cant. Dinos Limpiados", min_value=0, step=1)
                with col_s3:
                    cant_canastillas = st.number_input("Cant. Canastillas", min_value=0, step=1)
                
                rend_saneamiento = st.text_input("Rendimiento del Área (Opcional)")
                
            else: # Otros posibles usuarios (ej. fileteo genérico)
                cuad_label = st.selectbox("🦑 Cuadrilla Responsable", lista_cuadrillas_labels)
                id_cuadrilla = cuadrilla_map.get(cuad_label)
                kilos_conforme = st.number_input("⚖️ Kilos Procesados (Conformes)", min_value=0.0, step=1.0)
                
            notas = st.text_area("🗒️ Notas u Observaciones")
            
            submitted = st.form_submit_button("Guardar Registro 🚢", use_container_width=True)
            
            if submitted:
                t_inicio = datetime.combine(datetime.today(), hora_inicio)
                t_fin = datetime.combine(datetime.today(), hora_fin)
                diff = (t_fin - t_inicio).total_seconds() / 3600.0
                if diff < 0: diff += 24 
                
                record = {
                    'ID_Registro': f"REG-{int(datetime.now().timestamp())}",
                    'Fecha': fecha.strftime('%Y-%m-%d'),
                    'Hora_Registro': datetime.now().strftime('%H:%M:%S'),
                    'ID_Rol': user_info.get('ID_Rol', ''),
                    'ID_Area': user_info.get('ID_Area', ''),
                    'ID_Cuadrilla': id_cuadrilla,
                    'Turno': turno,
                    'ID_Lote': id_lote,
                    
                    'Kilos_Ingreso': kilos_ingreso,
                    'Calidad_Pota': calidad_pota,
                    'Tamano_Promedio': tamano_promedio,
                    'Kilos_Aumento': kilos_aumento,
                    
                    'Kilos_Conforme': kilos_conforme,
                    
                    'Cantidad_Cajas': cant_cajas,
                    'Cantidad_Dinos': cant_dinos,
                    'Cantidad_Canastillas': cant_canastillas,
                    'Rendimiento_Saneamiento': rend_saneamiento,
                    
                    'Producto_Envasado': prod_envasado,
                    'Color_Envasado': color_envasado,
                    'Cantidad_Reportada': cant_reportada,
                    
                    'Horas_Proceso': round(diff, 2),
                    'Num_Operarios': num_operarios,
                    'Notas': notas
                }
                
                if add_production_record(record):
                    st.success("¡Registro de producción guardado con éxito! ⚓")
                    st.balloons()
                else:
                    st.error("Hubo un problema guardando el registro.")
        st.markdown("</div>", unsafe_allow_html=True)
