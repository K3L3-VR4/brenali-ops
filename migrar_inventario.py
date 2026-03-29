import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    host="nozomi.proxy.rlwy.net",
    database="railway",
    user="postgres",
    password="FuuQagrMznDwVlnhKCyDiugkGPXLNACu",
    port=10465
)
cursor = conn.cursor()

file = r"C:\Users\Kandor\Documents\PORTFOLIO\Drive White Operations\Drive white - Operations.xlsx"
df_raw = pd.read_excel(file, sheet_name="Inventario Base")
df = df_raw.copy()
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)
df = df.dropna(how='all')

df.columns = [
    'id', 'categoria', 'material', 'color_tipo',
    'unidad', 'stock_inicial', 'stock_actual',
    'ubicacion', 'stock_minimo', 'estado', 'extra1', 'notas'
]

df = df.where(pd.notna(df), None)

columnas = [
    'categoria', 'material', 'color_tipo', 'unidad',
    'stock_inicial', 'stock_actual', 'ubicacion',
    'stock_minimo', 'estado', 'notas'
]

registros = [tuple(row) for row in df[columnas].values]

execute_values(cursor, """
    INSERT INTO inventario (
        categoria, material, color_tipo, unidad,
        stock_inicial, stock_actual, ubicacion,
        stock_minimo, estado, notas
    ) VALUES %s
""", registros)

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(registros)} items de inventario migrados exitosamente.")