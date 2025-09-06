🔧 Prompt para Desarrollo Continuo del Sistema de Gestión para Jardín de Niños

🎯 CONTEXTO DEL SISTEMA:
Desarrollo de una aplicación desktop para gestión administrativa de jardines de niños independientes. Sistema POS especializado en servicios educativos (comedor, útiles, actividades) con control de pagos, alumnos y familiares.

📋 REGLAS DE NEGOCIO FUNCIONALES:

1. Gestión de Alumnos y Familias:

Un alumno puede tener múltiples tutores/padres registrados

Cada tutor puede tener múltiples alumnos (hermanos)

Registrar relación familiar (padre/madre/tutor), permisos de recoger al niño, contacto de emergencia

Campos obligatorios: CURP, matrícula única, datos de contacto

2. Sistema de Ventas y Servicios:

Venta de servicios (comedor, cuidados, actividades) y productos (útiles, uniformes)

Un ticket de venta puede contener múltiples servicios/productos

Precios predefinidos pero editables durante la venta (con validación)

Soporte para abonos y pagos parciales múltiples

Cálculo automático de impuestos (IVA 16%)

3. Control de Pagos:

Múltiples métodos de pago por ticket (efectivo, tarjeta, transferencia)

Cambio automático cuando el pago en efectivo excede el total

Estados de pago: pagado, parcial, pendiente

Historial completo de transacciones por alumno/familia

4. Seguridad y Accesos:

Roles: administrador, vendedor, solo reportes

Autenticación por usuario y contraseña

Auditoría de operaciones (quién, cuándo, qué)

5. Reportes y Análisis:

Ventas por periodo, por alumno, por servicio

Estado de cuentas por familia

Productos/servicios más vendidos

Cortes de caja diarios

⚙️ REGLAS NO FUNCIONALES:

1. Rendimiento:

Respuesta en interfaz < 200ms

Soporte para 1000+ alumnos y 10k+ transacciones

Inicio de aplicación en < 3 segundos

2. Confiabilidad:

Funcionamiento offline permanente

Backup automático diario

Recuperación ante fallos de energía

3. Usabilidad:

Interfaz intuitiva para personal administrativo

Flujos optimizados para ventas rápidas

Navegación por teclado (atajos)

Formularios con validación en tiempo real

4. Mantenibilidad:

Arquitectura por capas (UI, servicios, datos)

Código documentado y modular

Facilidad para agregar nuevos reportes

5. Seguridad:

Datos locales cifrados

Validación de integridad de base de datos

Control de acceso por roles

🎨 REQUERIMIENTOS DE INTERFAZ:

1. Estilo Visual:

Tema oscuro/light mode intercambiable

Paleta de colores profesional (verdes, azules, grises)

Esquinas redondeadas en tarjetas y botones

Tipografía: Inter o Roboto, jerarquía clara

2. Experiencia de Usuario:

Pantalla de login elegante con logo institucional

Dashboard con métricas clave

Formularios agrupados por secciones

Feedback visual inmediato (éxito/error/loading)

Confirmaciones para acciones destructivas

3. Componentes Específicos:

Selector de alumno con búsqueda en tiempo real

Tabla de productos con filtros rápidos

Modal de pagos con desglose claro

Visor de tickets estilo recibo fiscal

Navegación por pestañas o sidebar

4. Responsividad:

Adaptable a resoluciones desde 1280x720

Scroll suave en listas largas

Ventanas modales responsivas

📦 ENTORNOS SOPORTADOS:

Windows 10/11 (principal)

Linux (compatibilidad secundaria)

Instalación silenciosa/un archivo ejecutable

Actualizaciones automáticas

🚀 INSTRUCCIONES PARA CONTINUAR DESARROLLO:

"Continúa el desarrollo del sistema de gestión para jardín de niños basado en los requerimientos funcionales y no funcionales establecidos. Mantén la arquitectura por capas actual (UI, servicios, datos) y asegura el cumplimiento de todas las reglas de negocio.

Próximo módulo a desarrollar: [Especificar módulo aquí]

Requerimientos específicos del módulo: [Describir funcionalidades esperadas]

Consideraciones técnicas: [Restricciones o integraciones necesarias]

Criterios de aceptación: [Métricas de éxito para el módulo]"

📝 NOTAS ADICIONALES:

Usar CustomTkinter para interfaz moderna

SQLite como base de datos embebida

Priorizar experiencia de usuario administrativa

Mantener consistencia en patrones de código existentes

Documentar cambios y decisiones técnicas

Este prompt asegura continuidad en el desarrollo manteniendo consistencia en requerimientos, arquitectura y estándares de calidad. 🚀