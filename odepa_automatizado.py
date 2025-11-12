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
    """Descarga el boletín diario con una sesión persistente y headers reales"""
    try:
        session = requests.Session()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
                "application/vnd.ms-excel;q=0.9,*/*;q=0.8"
            ),
            "Referer": "https://www.odepa.gob.cl/",
            "Connection": "keep-alive",
        }

        # 1️⃣ Primero entrar a la página raíz para obtener cookies válidas
        session.get("https://www.odepa.gob.cl", headers=headers, timeout=20)

        # 2️⃣ Luego descargar el archivo Excel real
        r = session.get(url, headers=headers, timeout=40, allow_redirects=True)
        r.raise_for_status()

        # Validar si es realmente un Excel
        if "application/vnd.openxmlformats" not in r.headers.get("Content-Type", ""):
            print("⚠️ El servidor devolvió HTML en lugar del Excel, se guardará para inspección...")
            with open("respuesta_odepa.html", "wb") as f:
                f.write(r.content)
            return False

        with open(destino, "wb") as f:
            f.write(r.content)

        print(f"✅ Archivo descargado correctamente: {destino}")
        return True

    except Exception as e:
        print(f"⚠️ Error al descargar boletín: {e}")
        return False


def procesar_boletin():
    """Lee y filtra los datos de tomate"""
    try:
        df = pd.read_excel(ARCHIVO_EXCEL, sheet_name=HOJA, header=8, engine="openpyxl")
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        col_especie = [c for c in df.columns if "especie" in c or "producto" in c]
        if not col_especie:
            raise ValueError("No se encontró columna de especie o producto.")
        col_especie = col_especie[0]

        df_tomate = df[df[col_especie].str.contains("tomate", case=False, na=False)].copy()
        df_tomate["fecha"] = date.today().isoformat()

        print(f"✅ Registros de tomate encontrados: {len(df_tomate)}")
        return df_tomate

    except Exception as e:
        print(f"⚠️ Error al procesar boletín: {e}")
        return pd.DataFrame()


def guardar_en_sqlite(df):
    """Guarda los datos"""
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
