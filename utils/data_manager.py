import pandas as pd
import json
import bcrypt
import os
import streamlit as st
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MASTER_EXCEL_FILE = os.path.join(DATA_DIR, 'base_datos.xlsx')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def initialize_daily_file(daily_file):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(MASTER_EXCEL_FILE):
        return # If master doesn't exist, we can't do much here.
        
    try:
        xl = pd.ExcelFile(MASTER_EXCEL_FILE)
        sheets = xl.sheet_names
        
        with pd.ExcelWriter(daily_file, engine='openpyxl') as writer:
            # First, write FACT_PRODUCCION (empty)
            df_fact = pd.DataFrame(columns=[
                'ID_Registro', 'Fecha', 'Hora_Registro', 'ID_Rol', 'ID_Area', 'ID_Cuadrilla', 'Turno',
                'ID_Lote', 'Kilos_Ingreso', 'Calidad_Pota', 'Tamano_Promedio', 'Kilos_Descuento_Calidad',
                'Kilos_Conforme', 'Cantidad_Cajas', 'Cantidad_Dinos', 'Cantidad_Canastillas', 'Rendimiento_Saneamiento',
                'Producto_Envasado', 'Color_Envasado', 'Cantidad_Reportada', 'Horas_Proceso', 'Num_Operarios', 'Notas'
            ])
            df_fact.to_excel(writer, sheet_name='FACT_PRODUCCION', index=False)
            
            # Write all other sheets from master
            for sheet in sheets:
                if sheet != 'FACT_PRODUCCION':
                    df_sheet = pd.read_excel(xl, sheet_name=sheet)
                    df_sheet.to_excel(writer, sheet_name=sheet, index=False)
    except Exception as e:
        print(f"Error initializing daily file {daily_file}: {e}")

def get_excel_file_for_date(date_str):
    daily_file = os.path.join(DATA_DIR, f'base_datos_{date_str}.xlsx')
    if not os.path.exists(daily_file):
        initialize_daily_file(daily_file)
    return daily_file

def authenticate(username, password):
    if not os.path.exists(USERS_FILE):
        return False, None
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username in users:
        stored_password = users[username]['password']
        
        # Verificar si está encriptada con bcrypt o es texto plano
        if stored_password.startswith("$2b$"):
            try:
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            except ValueError:
                is_valid = False
        else:
            is_valid = (password == stored_password)
            
        if is_valid:
            try:
                df_roles = pd.read_excel(MASTER_EXCEL_FILE, sheet_name='Dim_Roles')
                user_info = df_roles[df_roles['Username'] == username]
                if not user_info.empty:
                    return True, user_info.iloc[0].to_dict()
            except Exception as e:
                print(f"Error reading roles: {e}")
                return True, {"Username": username, "Nivel_Acceso": "Desconocido"}
    return False, None

def _safe_write_excel(func, retries=5, delay=0.5):
    """ Helper to handle concurrent writes in Excel """
    for attempt in range(retries):
        try:
            func()
            return True
        except PermissionError:
            time.sleep(delay)
    return False

def add_production_record(record_dict):
    """ Adds a new record to FACT_PRODUCCION """
    date_str = record_dict.get('Fecha', datetime.now().strftime('%Y-%m-%d'))
    daily_file = get_excel_file_for_date(date_str)
    
    def append_data():
        df = pd.read_excel(daily_file, sheet_name='FACT_PRODUCCION')
        new_record_df = pd.DataFrame([record_dict])
        df = pd.concat([df, new_record_df], ignore_index=True)
        with pd.ExcelWriter(daily_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='FACT_PRODUCCION', index=False)
    
    return _safe_write_excel(append_data)

PRODUCTOS_ENVASADO = {
    'Anillas 1.2-1.6': 'AZUL',
    'Anillas 0.8-1.2': 'BLANCO',
    'Recorte blanco': 'CRISTAL',
    'Recorte amarillo': 'ROJO',
    'Boton blanco': 'VERDE',
    'Boton amarillo': 'ROSADO',
    'Nuca 100-300': 'LILA',
    'Nuca 300-500': 'VERDE',
    'Nuca 500-1000': 'ROSADO',
    'Nuca 1-up': 'NARANJA',
    'Tentaculo limpio 100-300': 'CREMA',
    'Tentaculo limpio 300-500': 'LILA',
    'Tentaculo limpio 500-1000': 'S/C',
    'Tentaculo limpio 1-2': 'S/C',
    'Tentaculo sucio 100-500': 'VERDE',
    'Tentaculo sucio 500-1000': 'ROSADO',
    'Aleta 100-300': 'CRISTAL',
    'Aleta 500-1000': 'NARANJA',
    'Aleta 1-2': 'AMARILLO',
    'Aleta 2-UP': 'VERDE',
    'Reproductor GRANDE': 'AZUL',
    'Reproductor PEQUEÑO': 'BLANCO',
    'Manto C/M C/T L.P. 1-2': 'BLANCO',
    'Manto C/M C/T L.P. 2-4': 'AMARILLO',
    'Filete C/M C/T L.P. 1-2': 'VERDE',
    'Filete C/M C/T L.P. 2-4': 'AZUL',
}

@st.cache_data(ttl=60)
def get_dimension_data():
    """ Loads dimension tables for dropdowns """
    dimensions = {}
    try:
        dimensions['areas'] = pd.read_excel(MASTER_EXCEL_FILE, sheet_name='Dim_Areas')
        dimensions['lotes'] = pd.read_excel(MASTER_EXCEL_FILE, sheet_name='Dim_Lotes')
        dimensions['productos_envasado'] = PRODUCTOS_ENVASADO
        dimensions['cuadrillas'] = pd.read_excel(MASTER_EXCEL_FILE, sheet_name='Dim_Cuadrillas')
    except Exception as e:
        print(f"Error loading dimensions: {e}")
    return dimensions

def get_fact_data(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    daily_file = get_excel_file_for_date(date_str)
    try:
        return pd.read_excel(daily_file, sheet_name='FACT_PRODUCCION')
    except Exception as e:
        print(f"Error loading fact data for {date_str}: {e}")
        return pd.DataFrame()

def add_supervisor(username, password, nombre, id_area, nivel_acceso='Supervisor'):
    if not os.path.exists(USERS_FILE):
        users = {}
    else:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[username] = {'password': hashed_password}
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
        
    def append_role(file_path):
        if not os.path.exists(file_path): return
        try:
            df_roles = pd.read_excel(file_path, sheet_name='Dim_Roles')
            if username in df_roles['Username'].values:
                df_roles.loc[df_roles['Username'] == username, ['Nombre', 'ID_Area', 'Nivel_Acceso']] = [nombre, id_area, nivel_acceso]
            else:
                last_id = df_roles['ID_Rol'].max()
                if pd.isna(last_id) or not str(last_id).startswith('R'):
                    new_id = 'R01'
                else:
                    new_id = f"R{int(str(last_id)[1:]) + 1:02d}"
                new_row = pd.DataFrame([{'ID_Rol': new_id, 'Username': username, 'Nombre': nombre, 'ID_Area': id_area, 'Nivel_Acceso': nivel_acceso}])
                df_roles = pd.concat([df_roles, new_row], ignore_index=True)
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_roles.to_excel(writer, sheet_name='Dim_Roles', index=False)
        except Exception as e:
            print(f"Error appending role: {e}")

    append_role(MASTER_EXCEL_FILE)
    current_date = datetime.now().strftime('%Y-%m-%d')
    daily_file = os.path.join(DATA_DIR, f'base_datos_{current_date}.xlsx')
    if os.path.exists(daily_file):
        append_role(daily_file)

def add_cuadrilla(nombre_lider, num_operarios, area):
    def append_cuadrilla_file(file_path):
        if not os.path.exists(file_path): return
        try:
            df = pd.read_excel(file_path, sheet_name='Dim_Cuadrillas')
            if 'Num_Operarios' not in df.columns: df['Num_Operarios'] = None
            if 'Area' not in df.columns: df['Area'] = None
            
            last_id = df['ID_Cuadrilla'].max()
            if pd.isna(last_id) or not str(last_id).startswith('C'):
                new_id = 'C01'
            else:
                new_id = f"C{int(str(last_id)[1:]) + 1:02d}"
                
            new_row = pd.DataFrame([{'ID_Cuadrilla': new_id, 'Nombre_Lider': nombre_lider, 'Num_Operarios': num_operarios, 'Area': area}])
            df = pd.concat([df, new_row], ignore_index=True)
            
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='Dim_Cuadrillas', index=False)
        except Exception as e:
            print(f"Error appending cuadrilla: {e}")

    append_cuadrilla_file(MASTER_EXCEL_FILE)
    current_date = datetime.now().strftime('%Y-%m-%d')
    daily_file = os.path.join(DATA_DIR, f'base_datos_{current_date}.xlsx')
    if os.path.exists(daily_file):
        append_cuadrilla_file(daily_file)

def delete_cuadrilla(id_cuadrilla):
    def delete_cuadrilla_file(file_path):
        if not os.path.exists(file_path): return
        try:
            df = pd.read_excel(file_path, sheet_name='Dim_Cuadrillas')
            df = df[df['ID_Cuadrilla'] != id_cuadrilla]
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='Dim_Cuadrillas', index=False)
        except Exception as e:
            print(f"Error deleting cuadrilla: {e}")

    delete_cuadrilla_file(MASTER_EXCEL_FILE)
    current_date = datetime.now().strftime('%Y-%m-%d')
    daily_file = os.path.join(DATA_DIR, f'base_datos_{current_date}.xlsx')
    if os.path.exists(daily_file):
        delete_cuadrilla_file(daily_file)
