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
│   ├── tutor.py            # Modelo de tutores
│   └── user.py             # Modelo de usuarios
│
├── repositories/           # Capa de acceso a datos (SQL)
│   ├── __init__.py
│   ├── customer_repo.py    # Consultas de alumnos
│   ├── tutor_repo.py       # Consultas de tutores
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
│   ├── menu.py         # Pantalla de menu
│   ├── students.py     # Gestión de estudiantes
│   ├── tutors.py       # Gestión de tutores
│   ├── sales.py        # Gestión de ventas
│   ├── reports.py      # Reportes
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