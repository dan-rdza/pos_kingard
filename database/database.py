import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or self.get_default_db_path()
        self.init_db()
    
    def get_default_db_path(self):
        """Obtener ruta por defecto para la BD (AppData)"""
        if os.name == 'nt':  # Windows
            app_data = Path(os.environ['APPDATA']) / 'SistemaJardin'
        else:  # Linux/Mac
            app_data = Path.home() / '.pos_kingard'
        
        app_data.mkdir(exist_ok=True)
        return app_data / 'school.db'
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializar la base de datos si no existe"""
        if not os.path.exists(self.db_path):
            print("Creando base de datos por primera vez...")
            self.create_database()
    
    def create_database(self):
        """Crear la base de datos desde schema.sql"""
        schema_path = Path(__file__).parent / 'schema.sql'
        print(f"Schema Path: {schema_path}")

        with self.get_connection() as conn:
            # Ejecutar schema completo
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            
            # Insertar datos iniciales
            self.insert_initial_data(conn)
            
            conn.commit()
    
    def insert_initial_data(self, conn):
        """Insertar datos mínimos para que funcione la app"""
        try:
            # Configuración del negocio
            conn.execute('''
                INSERT INTO business_config (id, name, rfc, address, phone, thank_you)
                VALUES (1, 'Prescolar Libertad y Creatividad A.C.', 'LCR030414IB8', 'Av. de los Frutales #201, Frutales de la Hacienda, León, Gto. Mx.', 
                        '477-198-31-64', '¡Gracias por su preferencia!')
            ''')
            
            # Usuario admin por defecto (password: admin123)
            conn.execute('''
                INSERT INTO sellers (employee_code, first_name, second_name, job_title, 
                                   username, password_hash, role)
                VALUES ('ADMIN001', 'Administrador', 'Sistema', 'Director', 
                       'admin', 'admin123', 'admin')
            ''')
            
        except sqlite3.IntegrityError:
            # Los datos ya existen, no hay problema
            pass

    def authenticate_user(self, username, password):
        """Autenticar usuario contra la base de datos"""
        username = username.upper()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, employee_code, first_name, second_name, role, job_title 
                FROM sellers 
                WHERE username = ? AND password_hash = ? AND active = 1
            ''', (username, password))
            
            user = cursor.fetchone()
            return dict(user) if user else None

    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, employee_code, first_name, second_name, role, username
                FROM sellers 
                WHERE id = ? AND active = 1
            ''', (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None

# Para probar directamente
if __name__ == "__main__":
    db = Database()
    print(f"Base de datos creada en: {db.db_path}")