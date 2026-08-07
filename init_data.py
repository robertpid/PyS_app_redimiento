import pandas as pd
import json
import os

DATA_DIR = 'data'
EXCEL_FILE = os.path.join(DATA_DIR, 'base_datos.xlsx')

def create_excel_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        # FACT_PRODUCCION - Estructura ampliada para todas las áreas
        df_fact = pd.DataFrame(columns=[
            'ID_Registro', 'Fecha', 'Hora_Registro', 'ID_Rol', 'ID_Area', 'ID_Cuadrilla',
            'ID_Lote', 'Kilos_Ingreso', 'Calidad_Pota', 'Tamano_Promedio', 'Kilos_Descuento_Calidad', # Recepcion
            'Kilos_Conforme', # Troquelado/Fileteo/Empaque
            'Cantidad_Cajas', 'Cantidad_Dinos', 'Cantidad_Canastillas', 'Rendimiento_Saneamiento', # Saneamiento
            'Producto_Envasado', 'Color_Envasado', 'Cantidad_Reportada', # Envasado
            'Horas_Proceso', 'Num_Operarios', 'Notas' # General
        ])
        df_fact.to_excel(writer, sheet_name='FACT_PRODUCCION', index=False)

        # Dim_Roles
        df_roles = pd.DataFrame({
            'ID_Rol': ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08'],
            'Username': ['recepcion', 'troquelado', 'envasado1', 'empaque1', 'saneamiento', 'jefa', 'contadora', 'jefeprod'],
            'Nombre': ['Juan Recepcion', 'Pedro Troquelado', 'Ana Envasado', 'Luis Empaque', 'Carlos Saneamiento', 'Jefa General', 'Contadora', 'Jefe Produccion'],
            'ID_Area': ['A01', 'A02', 'A03', 'A04', 'A05', 'A00', 'A00', 'A00'],
            'Nivel_Acceso': ['Supervisor', 'Supervisor', 'Supervisor', 'Supervisor', 'Supervisor', 'Gerencia', 'Gerencia', 'Gerencia']
        })
        df_roles.to_excel(writer, sheet_name='Dim_Roles', index=False)

        # Dim_Areas
        df_areas = pd.DataFrame({
            'ID_Area': ['A01', 'A02', 'A03', 'A04', 'A05', 'A00'],
            'Nombre_Area': ['Recepcion', 'Troquelado', 'Envasado', 'Empaque', 'Saneamiento', 'Gerencia']
        })
        df_areas.to_excel(writer, sheet_name='Dim_Areas', index=False)

        # Dim_Lotes (Mock data)
        df_lotes = pd.DataFrame({
            'ID_Lote': ['L001', 'L002', 'L003'],
            'Proveedor': ['Prov A', 'Prov B', 'Prov C'],
            'Fecha_Recepcion': ['2026-08-01', '2026-08-02', '2026-08-03']
        })
        df_lotes.to_excel(writer, sheet_name='Dim_Lotes', index=False)

        # Dim_Cuadrillas
        df_cuadrillas = pd.DataFrame({
            'ID_Cuadrilla': ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07'],
            'Nombre_Lider': ['Cuadrilla 1', 'Cuadrilla 2', 'Cuadrilla 3', 'Cuadrilla 4', 'Cuadrilla 5', 'Cuadrilla 6', 'Cuadrilla 7']
        })
        df_cuadrillas.to_excel(writer, sheet_name='Dim_Cuadrillas', index=False)

    print(f"Excel database initialized at {EXCEL_FILE}")

if __name__ == '__main__':
    create_excel_db()
