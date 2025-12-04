import sqlite3
import pandas as pd
from pathlib import Path
import os

# =======================================================
# CONFIGURACIÓN DE RUTAS
# =======================================================
APPDATA = os.getenv("APPDATA")  # Ej: C:\Users\usuario\AppData\Roaming
if not APPDATA:
    raise RuntimeError("No se pudo obtener la variable de entorno APPDATA")

DB_PATH = os.path.join(APPDATA, "SistemaJardin", "school.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

EXCEL_PATH = "DATOS ALUMNOS.xlsx"  # Ajusta si está en otra carpeta

# =======================================================
# UTILIDADES
# =======================================================

month_map = {
    "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
    "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
    "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": "11", "DICIEMBRE": "12"
}

def normalize_str(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s == "" or s.upper() == "NAN":
        return None
    return s

def numeric_to_str(x):
    if pd.isna(x):
        return None
    try:
        v = int(float(x))
        return str(v)
    except Exception:
        return normalize_str(x)

def build_birth_date(dia, mes, anio):
    if pd.isna(dia) or pd.isna(mes) or pd.isna(anio):
        return None
    mes_clean = str(mes).strip().upper()
    mm = month_map.get(mes_clean)
    if not mm:
        return None
    try:
        dd = int(dia)
        yy = int(anio)
        return f"{yy:04d}-{mm}-{dd:02d}"
    except Exception:
        return None

def map_gender(sexo):
    """
    Excel: H = Hombre, M = Mujer
    Tabla: gender IN ('M','F')
    Convención usada:
      H -> 'M' (Male)
      M -> 'F' (Female)
    Ajusta si en tu UI usas otra convención.
    """
    if pd.isna(sexo):
        return None
    s = str(sexo).strip().upper()
    if s == "H":
        return "M"
    if s == "M":
        return "F"
    return None

def make_address(row):
    parts = []
    for col in ["DOMICILIO", "E CALLE 1", "E CALLE 2"]:
        val = normalize_str(row.get(col))
        if val:
            parts.append(val)
    cp = numeric_to_str(row.get("CÓDIGO PTAL"))
    if cp:
        parts.append(f"CP {cp}")
    return ", ".join(parts) if parts else None

def upsert_catalog(conn, table, code, name):
    cur = conn.cursor()
    cur.execute(f"INSERT OR IGNORE INTO {table} (code, name) VALUES (?, ?)", (code, name))
    conn.commit()
    cur.execute(f"SELECT id FROM {table} WHERE code = ?", (code,))
    row = cur.fetchone()
    return row[0] if row else None

# =======================================================
# IMPORTACIÓN PRINCIPAL
# =======================================================

def import_data():
    xl_path = Path(EXCEL_PATH)
    if not xl_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de Excel: {xl_path}")

    print("Usando base de datos:", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Lee la primera hoja (ajusta sheet_name si usas otra)
    df = pd.read_excel(xl_path, sheet_name=0)

    for idx, row in df.iterrows():
        # ------------------------
        # Datos básicos del alumno
        # ------------------------
        enrollment = numeric_to_str(row.get("MATRICULA"))
        if not enrollment:
            print(f"Fila {idx}: sin matrícula, se omite")
            continue

        grado = normalize_str(row.get("GRADO"))
        grupo = normalize_str(row.get("GRUPO"))
        turno = normalize_str(row.get("HORARIO"))
        sexo = map_gender(row.get("SEXO"))

        apellido_p = normalize_str(row.get("APELLIDO PATERNO"))
        apellido_m = normalize_str(row.get("APELLIDO MATERNO"))
        nombres = normalize_str(row.get("NOMBRE"))

        # Guardamos el nombre propio en first_name y los apellidos en second_name
        first_name = nombres
        second_name = " ".join([p for p in [apellido_p, apellido_m] if p])

        address = make_address(row)
        birth_date = build_birth_date(row.get("DIA FNAC"), row.get("MES FNAC"), row.get("AÑO FNAC"))
        curp = normalize_str(row.get("CURP"))
        pay_ref = numeric_to_str(row.get("REFERENCIA"))

        # ------------------------
        # Catálogos: grados, grupos, turnos
        # ------------------------
        grade_id = group_id = shift_id = None
        if grado:
            grade_id = upsert_catalog(conn, "grades", code=str(grado), name=f"Grado {grado}")
        if grupo:
            group_id = upsert_catalog(conn, "groups", code=str(grupo), name=f"Grupo {grupo}")
        if turno:
            shift_id = upsert_catalog(conn, "shifts", code=turno.upper(), name=turno.strip().title())

        cur = conn.cursor()

        # ------------------------
        # customers (alumno)
        # ------------------------
        cur.execute("SELECT id FROM customers WHERE enrollment = ?", (enrollment,))
        existing = cur.fetchone()

        if existing:
            customer_id = existing[0]
            cur.execute("""
                UPDATE customers
                SET first_name = ?, second_name = ?, address = ?,
                    grade_id = ?, group_id = ?, shift_id = ?,
                    gender = ?, birth_date = ?, curp = ?, pay_reference = ?
                WHERE id = ?
            """, (
                first_name, second_name, address,
                grade_id, group_id, shift_id,
                sexo, birth_date, curp, pay_ref,
                customer_id
            ))
        else:
            cur.execute("""
                INSERT INTO customers
                (enrollment, first_name, second_name, address,
                 grade_id, group_id, shift_id,
                 gender, birth_date, curp, pay_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                enrollment, first_name, second_name, address,
                grade_id, group_id, shift_id,
                sexo, birth_date, curp, pay_ref
            ))
            customer_id = cur.lastrowid

        conn.commit()

        # ------------------------
        # tutors (mamá / papá del alumno)
        # ------------------------
        tel_casa = numeric_to_str(row.get("TELÉFONO"))
        cel1 = numeric_to_str(row.get("CELULAR 1"))
        cel2 = numeric_to_str(row.get("CELULAR 2"))

        mama_name = normalize_str(row.get("NOMBRE MAMÁ"))
        papa_name = normalize_str(row.get("NOMBRE PAPÁ"))

        # Para mantener consistencia con el Excel:
        # borramos tutores actuales del alumno y los recreamos
        cur.execute("DELETE FROM tutors WHERE student_id = ?", (customer_id,))

        primary_assigned = False

        if mama_name:
            phone_mom = cel1 or tel_casa or cel2
            cur.execute("""
                INSERT INTO tutors
                (student_id, first_name, second_name, relationship, phone, email, is_primary, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                customer_id,
                mama_name,  # Usamos el nombre completo en first_name
                None,       # second_name opcional, si quieres luego lo separamos
                "Madre",
                phone_mom,
                None,
                1  # is_primary
            ))
            primary_assigned = True

        if papa_name:
            phone_dad = cel2 or tel_casa or cel1
            cur.execute("""
                INSERT INTO tutors
                (student_id, first_name, second_name, relationship, phone, email, is_primary, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                customer_id,
                papa_name,
                None,
                "Padre",
                phone_dad,
                None,
                0 if primary_assigned else 1  # si no hubo mamá, papá será principal
            ))

        conn.commit()

        print(f"Procesado alumno matrícula {enrollment} (id={customer_id})")

    conn.close()
    print("Importación terminada.")

# =======================================================
# PUNTO DE ENTRADA
# =======================================================
if __name__ == "__main__":
    import_data()
