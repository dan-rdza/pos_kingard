# 🎯 POS KinGard - Sistema de Gestión para Preescolar

Sistema Point of Sale (POS) y gestión administrativa diseñado específicamente para instituciones preescolares.

## ✨ Características Principales

### 👥 Gestión de Alumnos
- Registro completo de estudiantes con datos personales
- Matrículas únicas y sistema de seguimiento
- Gestión de información de contacto y CURP
- Control de referencias de pago

### 💰 Sistema de Pagos
- Control de colegiaturas y pagos
- Referencias de pago personalizadas
- Historial de transacciones
- Reportes financieros

### 📊 Dashboard y Reportes
- Panel de control administrativo
- Reportes de asistencia y pagos
- Estadísticas de matrícula
- Exportación de datos

### 🔐 Seguridad y Roles
- Sistema de autenticación seguro
- Roles de usuario (Admin, Docente, Secretaría)
- Control de acceso por permisos
- Registro de actividades

## 🚀 Tecnologías Utilizadas

- **Frontend**: CustomTkinter (Interfaz moderna)
- **Backend**: Python 3.10+
- **Base de Datos**: SQLite3 (Próximamente MySQL)
- **Reportes**: PDF y Excel integration

## 📦 Instalación

### Prerrequisitos
```bash
Python 3.10 o superior
pip install -r requirements.txt
```

### Instalación de Dependencias
```bash
pip install customtkinter
pip install pillow
pip install tkcalendar
```

### Ejecución
```bash
python main.py
```

## 🏗️ Estructura del Proyecto

```
pos_kingard/
├── main.py                 # Aplicación principal
├── database.py            # Configuración de base de datos
├── requirements.txt       # Dependencias del proyecto
├── models/               # Modelos de datos
│   └── student.py        # Modelo de estudiante
├── repositories/         # Acceso a datos
│   └── student_repo.py   # Repository de estudiantes
├── ui/                  # Interfaces de usuario
│   ├── menu.py          # Menú principal
│   ├── students.py      # Gestión de alumnos
│   └── __init__.py
└── assets/              # Recursos multimedia
    └── images/
        └── logo.png     # Logo de la aplicación
```

## 👤 Roles de Usuario

### Administrador
- Acceso completo al sistema
- Gestión de usuarios y permisos
- Configuración del sistema
- Reportes completos

### Docente
- Visualización de sus grupos
- Registro de asistencias
- Comunicación con padres

### Secretaría
- Registro de alumnos
- Control de pagos
- Reportes básicos

## 🎨 Interfaz de Usuario

La aplicación utiliza **CustomTkinter** para una experiencia moderna y dark-mode:

- **Tema Oscuro** por defecto
- **Botones y controles modernos**
- **Formularios responsivos**
- **Scrollable frames** para grandes listas
- **Validación de datos en tiempo real**

## 📋 Funcionalidades por Módulo

### Módulo de Estudiantes
- [x] Crear, editar y eliminar estudiantes
- [x] Búsqueda avanzada por nombre/matrícula
- [x] Validación de datos (CURP, fechas)
- [ ] Gestión de tutores (próximamente)
- [ ] Historial académico

### Módulo de Pagos
- [ ] Registro de pagos y colegiaturas
- [ ] Generación de referencias
- [ ] Recordatorios automáticos
- [ ] Reportes financieros

### Módulo de Reportes
- [ ] Reportes de matrícula
- [ ] Estado de cuentas
- [ ] Asistencias por periodo
- [ ] Exportación PDF/Excel

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
DB_PATH=database/kingard.db
APP_THEME=dark
DEFAULT_LANGUAGE=es
```

### Base de Datos
La aplicación crea automáticamente la base de datos SQLite en:
`database/kingard.db`

## 🚀 Roadmap

### Versión 1.0 (Actual)
- ✅ Gestión básica de estudiantes
- ✅ Sistema de autenticación
- ✅ Interfaz moderna con CustomTkinter

### Versión 1.1 (Próxima)
- [ ] Módulo completo de pagos
- [ ] Sistema de tutores
- [ ] Reportes básicos
- [ ] Backup automático

### Versión 2.0
- [ ] App móvil para padres
- [ ] Notificaciones push
- [ ] API REST
- [ ] Multi-tenant

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

## 📞 Contacto

**Daniel Rodriguez** - [GitHub](https://github.com/dan-rdza)

---

**¡Gracias por usar POS KinGard!** 🎓✨