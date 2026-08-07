import pandas as pd
import json
import bcrypt
import os
import streamlit as st
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXCEL_FILE = os.path.join(DATA_DIR, 'base_datos.xlsx')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

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
            # Fetch user role info from Excel
            try:
                df_roles = pd.read_excel(EXCEL_FILE, sheet_name='Dim_Roles')
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
    def append_data():
        df = pd.read_excel(EXCEL_FILE, sheet_name='FACT_PRODUCCION')
        new_record_df = pd.DataFrame([record_dict])
        df = pd.concat([df, new_record_df], ignore_index=True)
        # We rewrite the whole Excel file to append. Openpyxl can append but pandas is easier.
        # To not lose other sheets, we need to rewrite all or use openpyxl append.
        # Since the file might be small initially, we can read all and write all, OR use ExcelWriter in append mode.
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
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
        dimensions['areas'] = pd.read_excel(EXCEL_FILE, sheet_name='Dim_Areas')
        dimensions['lotes'] = pd.read_excel(EXCEL_FILE, sheet_name='Dim_Lotes')
        dimensions['productos_envasado'] = PRODUCTOS_ENVASADO
        dimensions['cuadrillas'] = pd.read_excel(EXCEL_FILE, sheet_name='Dim_Cuadrillas')
    except Exception as e:
        print(f"Error loading dimensions: {e}")
    return dimensions

def get_fact_data():
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name='FACT_PRODUCCION')
    except Exception as e:
        print(f"Error loading fact data: {e}")
        return pd.DataFrame()
