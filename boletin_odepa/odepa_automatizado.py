import os
import pandas as pd
import sqlite3
import requests
from datetime import date

# === Parámetros ===
URL_EXCEL = "https://www.odepa.gob.cl/wp-content/uploads/boletines/diario/boletin-diario-precios-volumenes-frutas-hortalizas.xlsx"
ARCHIVO_EXCEL = "boletin_diario.xlsx"
ARCHIVO_DB = "boletin_odepa.db"
HOJA = "Hortalizas_Lo Valledor"

def descargar_boletin(url=URL_EXCEL, destino=ARCHIVO_EXCEL):
    """Descarga el boletín diario de ODEPA"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(destino, "wb") as f:
            f.write(r.content)
        print(f"✅ Archivo descargado: {destino}")
        return True
    except Exception as e:
        print(f"⚠️ Error al descargar boletín: {e}")
        return False

def procesar_boletin():
    """Lee y filtra los datos de tomate del boletín"""
    try:
        df = pd.read_excel(ARCHIVO_EXCEL, sheet_name=HOJA, header=8)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        col_especie = [c for c in df.columns if "especie" in c or "producto" in c][0]
        df_tomate = df[df[col_especie].str.contains("tomate", case=False, na=False)].copy()
        df_tomate["fecha"] = date.today().isoformat()
        print(f"✅ Registros de tomate encontrados: {len(df_tomate)}")
        return df_tomate
    except Exception as e:
        print(f"⚠️ Error al procesar boletín: {e}")
        return pd.DataFrame()

def guardar_en_sqlite(df):
    """Guarda los datos en la base SQLite"""
    if df.empty:
        print("⚠️ No hay datos para guardar.")
        return
    conn = sqlite3.connect(ARCHIVO_DB)
    df.to_sql("tomate", conn, if_exists="append", index=False)
    conn.close()
    print(f"💾 Datos guardados en {ARCHIVO_DB}")

def main():
    print("=== Ejecución automática boletín ODEPA ===")
    if descargar_boletin():
        df_tomate = procesar_boletin()
        guardar_en_sqlite(df_tomate)
    print("✅ Proceso completado.")

if __name__ == "__main__":
    main()
