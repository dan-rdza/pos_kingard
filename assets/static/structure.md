sistema_jardin/
│
├── main.py                 # Punto de entrada de la aplicación
├── database.py             # Configuración y conexión de base de datos
│
├── models/                 # Modelos de datos (clases)
│   ├── __init__.py
│   ├── customer.py         # Modelo de alumnos
│   ├── product.py          # Modelo de productos
│   ├── sale.py             # Modelo de ventas
│   └── user.py             # Modelo de usuarios
│
├── repositories/           # Capa de acceso a datos (SQL)
│   ├── __init__.py
│   ├── customer_repo.py    # Consultas de alumnos
│   ├── product_repo.py     # Consultas de productos
│   ├── sale_repo.py        # Consultas de ventas
│   └── user_repo.py        # Consultas de usuarios
│
├── services/               # Lógica de negocio
│   ├── __init__.py
│   ├── auth_service.py     # Autenticación y permisos
│   ├── sale_service.py     # Procesamiento de ventas
│   └── report_service.py   # Generación de reportes
│
├── ui/                     # Interfaces gráficas
│   ├── __init__.py
│   ├── components/         # Componentes reutilizables
│   │   ├── header.py       # Encabezado común
│   │   ├── sidebar.py      # Menú lateral
│   │   └── dialogs.py      # Diálogos modales
│   │
│   ├── frames/             # Pantallas principales
│   │   ├── login_frame.py  # Pantalla de login
│   │   ├── sales_frame.py  # Pantalla de ventas
│   │   ├── customers_frame.py # Gestión de alumnos
│   │   └── reports_frame.py # Reportes
│   │
│   └── themes/             # Configuración de estilos
│       ├ __init__.py
│       └── styles.py       # Colores, fuentes, temas
│
├── utils/                  # Utilidades
│   ├── __init__.py
│   ├── validators.py       # Validaciones de formularios
│   ├── printers.py         # Utilidades de impresión ESC/POS
│   └── helpers.py          # Funciones auxiliares
│
└── assets/                 # Recursos
    ├── images/             # Iconos e imágenes
    ├── fonts/              # Fuentes personalizadas
    └── templates/          # Plantillas de tickets/reportes