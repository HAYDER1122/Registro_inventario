# Sistema de Inventario de Artículos de Oficina

## 📋 Descripción

Sistema de gestión de inventario desarrollado en Python con interfaz gráfica (PyQt6). Permite registrar, controlar y monitorear artículos de oficina con funcionalidades avanzadas como devoluciones, reportes y notificaciones por correo.

**Versión:** 1.0  
**Estado:** Compilado como ejecutable (.exe)

---

## ✨ Características Principales

### 🎯 Gestión de Inventario
- **Registro de artículos**: Añadir nuevos productos con detalles completos
- **Control de existencias**: Monitoreo en tiempo real de cantidades disponibles
- **Retiros y devoluciones**: Gestionar salidas y devoluciones de artículos
- **Búsqueda avanzada**: Filtrar artículos por nombre, categoría y estado
- **Historial completo**: Registro detallado de todas las operaciones

### 👥 Asignación de Personal
- Asociar artículos a cargos específicos (Asistente, Coordinador, Analista, etc.)
- Rastrear quién tiene qué artículos
- Validación de usuarios para auditoría

### 📊 Reportes y Análisis
- Generación de reportes en tiempo real
- Estadísticas de uso por categoría
- Exportación de datos para análisis externo
- Estado detallado del inventario

### 🎨 Interfaz Moderna
- **Tema claro y oscuro**: Alternar entre modos oscuro y claro
- **Modo compacto**: Toggle para optimizar espacio en pantalla
- **Animaciones visuales**: Confirmación visual con ✓ verde al retirar artículos
- **Interfaz intuitiva**: Diseño limpio con organización por pestañas

### 📧 Notificaciones
- Envío automático de correos con reportes
- Alertas de bajo inventario
- Configuración de destinatarios personalizados
- Integración con Gmail SMTP

### ⚙️ Configuración
- Ajustes de tema y presentación
- Configuración de correos y notificaciones
- Almacenamiento local en `%LOCALAPPDATA%`
- Base de datos SQLite independiente

---

## 🚀 Instalación

### Opción 1: Ejecutable (.exe)
1. Descarga el archivo `inventario.exe` de la carpeta `instaladores/`
2. Ejecuta el archivo
3. Sigue las instrucciones del instalador
4. El programa se instalará en tu equipo

### Opción 2: Desde Código Fuente
**Requisitos previos:**
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

**Pasos:**
```bash
# 1. Clonar o descargar el proyecto
cd "REGISTRO INVENTARIOS"

# 2. Instalar dependencias
pip install PyQt6

# 3. Ejecutar el programa
python inventario.py
```

---

## 📖 Uso Rápido

### Añadir un Artículo
1. Ve a la pestaña **Artículos**
2. Completa los campos: nombre, categoría, cantidad
3. Haz clic en **Agregar Artículo**

### Retirar un Artículo
1. Selecciona el artículo en la tabla
2. Indica la cantidad a retirar
3. Selecciona el cargo responsable
4. Confirma la operación
5. Verás una animación ✓ verde de confirmación

### Generar Reporte
1. Ve a la pestaña **Reportes**
2. Selecciona el período deseado
3. Haz clic en **Generar Reporte**
4. Opcionalmente envíalo por correo automático

### Cambiar Tema
- En el menú de configuración, selecciona entre **Tema Oscuro** o **Tema Claro**
- Los cambios se aplican inmediatamente

---

## 🗂️ Estructura del Proyecto

```
REGISTRO INVENTARIOS/
├── inventario.py              # Código principal del sistema
├── inventario_config.json     # Configuración (email, tema, etc.)
├── inventario.spec            # Especificación para PyInstaller
├── inventario.iss             # Script del instalador
├── README.md                  # Este archivo
├── SISTEMA.md                 # Documentación técnica detallada
├── Logo.ico                   # Icono de la aplicación
├── build/                     # Archivos compilados
└── instaladores/              # Ejecutables y instaladores
```

---

## ⚙️ Configuración

### Archivo: `inventario_config.json`

```json
{
  "email_remitente": "tu_email@gmail.com",
  "email_password": "contraseña_app_gmail",
  "email_destinatario": "destino@ejemplo.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "envio_automatico": true,
  "tema": "oscuro"
}
```

**Parámetros:**
- `email_remitente`: Correo desde el cual se envían notificaciones
- `email_password`: Contraseña de aplicación de Gmail (no la contraseña normal)
- `email_destinatario`: Correo que recibe los reportes
- `smtp_server`: Servidor SMTP (defecto: Gmail)
- `smtp_port`: Puerto SMTP (defecto: 587 para Gmail)
- `envio_automatico`: Activar/desactivar envío automático de reportes
- `tema`: Tema visual ("oscuro" o "claro")

---

## 🔐 Seguridad

- **Base de datos SQLite**: Almacenada de forma segura en `%LOCALAPPDATA%\Sistema de Inventario\`
- **Contraseñas**: Nunca se guardan en texto plano (usa contraseñas de aplicación)
- **Auditoría**: Registro completo de operaciones con usuario y fecha/hora
- **Hash**: Validación de integridad de datos

---

## 📋 Requisitos

- **Sistema Operativo**: Windows 7 o superior
- **Python**: 3.8+ (si ejecutas desde código fuente)
- **Dependencias**: PyQt6
- **RAM**: Mínimo 512 MB
- **Espacio**: ~50 MB

---

## 🐛 Solución de Problemas

### El programa no inicia
- Verifica que tengas Python 3.8+ instalado
- Instala PyQt6: `pip install PyQt6`
- Reinicia la aplicación

### No se envían correos automáticos
- Verifica la configuración en `inventario_config.json`
- Usa una contraseña de aplicación de Gmail, no tu contraseña normal
- Activa "Acceso a apps menos seguras" en tu cuenta de Gmail

### La base de datos se daña
- Se restaurará automáticamente en el próximo inicio
- Los datos previos estarán en `%LOCALAPPDATA%\Sistema de Inventario\`

---



## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.