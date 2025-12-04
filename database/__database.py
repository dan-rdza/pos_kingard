# database.py
import sqlite3
import os
import sys
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="pos_system.db"):
        self.is_exe = getattr(sys, 'frozen', False)
        
        if self.is_exe:
            exe_dir = Path(sys.executable).parent
            self.db_path = str(exe_dir / db_path)
        else:
            self.db_path = db_path
        
        # Asegurar que el directorio existe
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.init_db()
        
    def get_base_path(self):
        """Obtiene la ruta base correcta"""
        if self.is_exe:
            return Path(sys._MEIPASS)
        else:
            return Path(__file__).parent.parent
        
    def init_db(self):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(self.db_path):
            self.create_database()
    
    def create_database(self):
        """Crea la base de datos desde schema.sql"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Buscar schema.sql en la carpeta database/
            schema_path = self.get_base_path() / "database" / "schema.sql"
            
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_content = f.read()
                conn.executescript(schema_content)
                conn.commit()
                print(f"Base de datos creada desde schema.sql")
            else:
                # Si no encuentra schema.sql, crear estructura básica
                self.create_basic_schema(conn)
                print("Base de datos creada con esquema básico")
            
        except Exception as e:
            print(f"Error creando BD: {e}")
            # Crear estructura mínima si falla
            self.create_basic_schema(conn)
        finally:
            conn.close()
    
    def create_basic_schema(self, conn):
        """Crea esquema básico si no encuentra schema.sql"""
        basic_schema = """
        PRAGMA foreign_keys = ON;
        
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            second_name TEXT,
            active INTEGER NOT NULL DEFAULT 1
        );
        
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );
        """
        conn.executescript(basic_schema)
        conn.commit()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn