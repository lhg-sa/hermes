# Hermes - Guía de Instalación y Configuración

## Requisitos Previos

- Frappe Framework instalado (versón 14+)
- Python 3.10+
- Node.js 18+
- npm 9+

---

## Instalación del Proyecto

### 1. Instalar la Aplicación Hermess

```bash
# Ir al directorio de apps de frappe-bench
cd /home/frappe/frappe-bench/apps

# Clonar o copiar la carpeta hermes
# (Asegúrate de tener la estructura correcta)
```

### 2. Instalar Dependencias Python

```bash
# Desde el directorio frappe-bench
cd /home/frappe/frappe-bench

# Instalar la app
bench get-app hermes --overwrite

# O si es una instalación nueva
bench get-app hermes
```

### 3. Instalar Dependencias del Frontend

```bash
# Ir al directorio del frontend
cd /home/frappe/frappe-bench/apps/hermes/frontend

# Instalar dependencias npm
npm install
```

### 4. Construir el Frontend

```bash
# Construir para producción
npm run build

# Esto generará los archivos en:
# /home/frappe/frappe-bench/apps/hermes/hermes/public/hermes/
```

### 5. Configurar el Sitio

```bash
# Si es sitio nuevo
bench new-site hermes.local

# Instalar app en sitio
bench --site hermes.local install-app hermes

# Configurar ruta en nginx (si es necesario)
bench setup add-ons hermes
```

### 6. Iniciar Servicios

```bash
# Reiniciar bench
sudo bench restart

# O reiniciar servicios específicos
bench start
```

---

## Configuraciones Necesarias

### Doctypes Requeridos

Asegúrate de tener los siguientes Tipos de Documento (Doctype) configurados:

1. **Room** (habitación)
   - Campos: habitacion, distribucion, costo, habilitado

2. **Reservation** (reserva)
   - Campos: cliente, customer_name, habitacion, fecha_entrada, fecha_salida, estado_reserva, precio_base, total_abonado, total_pendiente, total_global, notas

3. **Customer** (cliente)
   - Usar campos personalizados para: teléfono y NIT

### Permisos

Verifica que los roles tengan los permisos necesarios:
- Permisos de lectura/escritura en Room
- Permisos de lectura/escritura en Reservation
- Permisos de lectura en Customer

---

## Configuraciones Adicionales

### iOS / Safari

Para evitar pantallas en blanco en iOS:

1. Viewport meta tag ya configurado:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
```

2. El CSS ya incluye soporte para `min-height: 100dvh` (dynamic viewport height)

### API Endpoints Disponibles

El backend proporciona las siguientes APIs:

| Función | Descripción |
|---------|-------------|
| `hermes.api.get_app` | Servir la app PWA |
| `hermes.api.check_session` | Verificar sesión |
| `hermes.api.get_rooms` | Obtener habitaciones |
| `hermes.api.get_week_availability` | Disponibilidad semanal |
| `hermes.api.get_available_rooms_for_dates` | Habitaciones disponibles |
| `hermes.api.search_customers` | Buscar clientes |
| `hermes.api.create_customer` | Crear cliente |
| `hermes.api.create_reservation` | Crear reserva |
| `hermes.api.get_reservation` | Obtener reserva |
| `hermes.api.update_reservation` | Actualizar reserva |
| `hermes.api.cancel_reservation` | Cancelar reserva |
| `hermes.api.get_recent_reservations` | Últimas reservas |

---

## Solución de Problemas

### La app no carga
1. Verificar que el build se generó correctamente
2. Revisar permisos de archivos
3. Verificar que la ruta `/hermes/` esté configurada

### Sesión expira frecuentemente
1. Verificar que `checkAuth` funciona correctamente
2. Revisar configuración de cookies en Frappe

### iOS muestra pantalla blanca
1. Asegurarse de estar usando HTTPS
2. Verificar manifest.json esté sirviendo correctamente

### Error al crear reservas
1. Verificar que los campos personalizados existen
2. Revisar permisos del rol de usuario

---

## Estructura del Proyecto

```
hermes/
├── frontend/                 # Vue.js 3 Frontend
│   ├── src/
│   │   ├── views/          # Vistas (Availability, Reservations, Reports, etc.)
│   │   ├── components/    # Componentes reutilizables
│   │   ├── composables/   # Composables de Vue
│   │   ├── utils/         # Utilidades (frappe.js)
│   │   ├── styles/        # Estilos CSS
│   │   └── router/        # Configuración de rutas
│   ├── public/            # Archivos públicos
│   └── package.json       # Dependencias npm
│
├── hermes/                 # Python/Frappe Backend
│   ├── api.py             # Funciones API
│   ├── hooks.py           # Hooks de Frappe
│   ├── doctype/           # Tipos de documento
│   └── public/            # Archivos públicos (build del frontend)
│
└── README.md              # Este archivo
```

---

## Notas de Desarrollo

### Modo Desarrollo

```bash
# Frontend
cd /home/frappe/frappe-bench/apps/hermes/frontend
npm run dev

# Backend (recargar automáticamente)
bench start
```

### Traducciones

Las traducciones están en:
`/frontend/src/composables/useI18n.js`

### Estilos

Los estilos usan TailwindCSS y variables CSS en:
- `/frontend/src/styles/variables.css`
- `/frontend/src/theme/index.css`
