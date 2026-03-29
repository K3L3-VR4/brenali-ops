import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

# --- CONEXION ---
conn = psycopg2.connect(
    host="localhost",
    database="brenali_ops",
    user="postgres",
    password="12345678"
)
cursor = conn.cursor()

# --- LEER EXCEL ---
file = "Drive white - Operations.xlsx"
df_raw = pd.read_excel(file, sheet_name="RAW DATA PROYECTS")
df = df_raw.copy()
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)
df = df.dropna(how='all')

# --- LIMPIAR ---
df.columns = [
    'proyecto', 'id', 'area', 'seccion_trabajada', 'materiales',
    'tipo_pintura', 'colores', 'codigos', 'stain_glaze',
    'nombre_stain', 'codigo_stain', 'fecha_inicio',
    'fecha_delivery', 'estado', 'notas'
]

# Reemplazar NaN con None para que entre como NULL
df = df.where(pd.notna(df), None)

# Convertir fechas
df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], errors='coerce')
df['fecha_delivery'] = pd.to_datetime(df['fecha_delivery'], errors='coerce')
df['fecha_inicio'] = df['fecha_inicio'].astype(object).where(df['fecha_inicio'].notna(), None)
df['fecha_delivery'] = df['fecha_delivery'].astype(object).where(df['fecha_delivery'].notna(), None)

# --- INSERTAR ---
columnas = [
    'proyecto', 'area', 'seccion_trabajada', 'materiales',
    'tipo_pintura', 'colores', 'codigos', 'stain_glaze',
    'nombre_stain', 'codigo_stain', 'fecha_inicio',
    'fecha_delivery', 'estado', 'notas'
]

registros = [tuple(row) for row in df[columnas].values]

execute_values(cursor, """
    INSERT INTO proyectos (
        proyecto, area, seccion_trabajada, materiales,
        tipo_pintura, colores, codigos, stain_glaze,
        nombre_stain, codigo_stain, fecha_inicio,
        fecha_delivery, estado, notas
    ) VALUES %s
""", registros)

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(registros)} registros migrados exitosamente.")