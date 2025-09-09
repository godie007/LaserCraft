# ⚙️ Configuración Avanzada - LaserCraft Studio

Esta guía te ayudará a configurar LaserCraft Studio para obtener los mejores resultados con tu LASER TREE 10W.

## 🔥 Configuración del Láser

### 📊 Parámetros de Potencia

#### Para LASER TREE 10W (10000 mW):

| Material | Grosor | Potencia | Velocidad | Pasadas | Notas |
|----------|--------|----------|-----------|---------|-------|
| **Madera Blanda** | 3mm | 80% | 150 mm/min | 3 | Pino, balsa |
| **Madera Blanda** | 6mm | 90% | 100 mm/min | 5 | Pino, balsa |
| **Madera Blanda** | 10mm | 100% | 30 mm/min | 6 | Máximo recomendado |
| **Madera Dura** | 3mm | 85% | 120 mm/min | 4 | Roble, haya |
| **Madera Dura** | 6mm | 95% | 60 mm/min | 6 | Roble, haya |
| **Acrílico** | 3mm | 80% | 100 mm/min | 2 | Transparente |
| **Acrílico** | 5mm | 90% | 50 mm/min | 3 | Transparente |
| **Acrílico** | 8mm | 100% | 25 mm/min | 4 | Máximo recomendado |
| **MDF** | 3mm | 75% | 150 mm/min | 2 | Fácil de cortar |
| **MDF** | 6mm | 90% | 80 mm/min | 3 | Fácil de cortar |
| **Contrachapado** | 3mm | 80% | 120 mm/min | 2 | Buena calidad |
| **Contrachapado** | 6mm | 95% | 60 mm/min | 3 | Buena calidad |
| **Cartón** | 2-5mm | 40% | 300 mm/min | 1 | Muy rápido |
| **Cuero** | 1-3mm | 50% | 200 mm/min | 1 | Cuidado con el olor |
| **Tela** | 1-2mm | 30% | 400 mm/min | 1 | Muy rápido |
| **Papel** | 0.1-0.5mm | 20% | 500 mm/min | 1 | Extremadamente rápido |

### 🎯 Configuración de Grabado

#### Parámetros Recomendados:

```python
# Configuración base para grabado
laser_power_max = 70.0    # 70% de potencia
num_layers = 3            # 3 pasadas
feed_rate = 200.0         # 200 mm/min
line_height = 0.3         # 0.3mm entre líneas
focus_height = 0.0        # Sin offset de enfoque
```

#### Configuraciones por Material:

**Madera:**
- **Potencia:** 60-80%
- **Velocidad:** 150-300 mm/min
- **Pasadas:** 2-4
- **Altura de línea:** 0.3-0.6mm

**Acrílico:**
- **Potencia:** 50-70%
- **Velocidad:** 200-400 mm/min
- **Pasadas:** 1-2
- **Altura de línea:** 0.2-0.4mm

**MDF:**
- **Potencia:** 60-75%
- **Velocidad:** 150-250 mm/min
- **Pasadas:** 2-3
- **Altura de línea:** 0.3-0.5mm

## 🖼️ Configuración de Procesamiento de Imágenes

### 🎛️ Parámetros de Procesamiento

#### Desenfoque Gaussiano:
```python
blur_kernel = 3  # Suavizado moderado
# Valores recomendados:
# 0 = Sin desenfoque (imágenes muy limpias)
# 3 = Desenfoque moderado (recomendado)
# 5 = Desenfoque fuerte (imágenes con mucho ruido)
```

#### Método de Umbralización:
- **Otsu:** Automático, bueno para la mayoría de imágenes
- **Adaptativo:** Se adapta a la imagen localmente
- **Simple:** Umbral fijo (127), para imágenes de alto contraste

#### Área Mínima:
```python
min_area = 100  # Filtra contornos pequeños
# Valores recomendados:
# 50 = Muchos detalles pequeños
# 100 = Balance (recomendado)
# 200 = Menos detalles, más simple
# 500 = Solo formas grandes
```

#### Factor de Simplificación:
```python
simplify_factor = 0.02  # Simplificación moderada
# Valores recomendados:
# 0.01 = Máximo detalle
# 0.02 = Balance (recomendado)
# 0.05 = Menos detalle, más rápido
# 0.1 = Muy simple
```

### 🎨 Presets de Procesamiento

#### Superficial Rápido:
```python
blur_kernel = 5
threshold_method = 'simple'
min_area = 200
simplify_factor = 0.05
fill_spacing = 4
laser_power = 25
feed_rate = 800
```

#### Calidad Media:
```python
blur_kernel = 3
threshold_method = 'simple'
min_area = 100
simplify_factor = 0.02
fill_spacing = 2
laser_power = 50
feed_rate = 400
```

#### Alta Calidad:
```python
blur_kernel = 1
threshold_method = 'otsu'
min_area = 50
simplify_factor = 0.01
fill_spacing = 1
laser_power = 75
feed_rate = 200
```

## ✂️ Configuración de Corte Láser

### 📏 Parámetros de Corte

#### Corte Simple:
```python
cut_distance = 50.0    # 50mm de longitud
cut_depth = 2.0        # 2mm de profundidad
cut_angle = 0.0        # 0° = horizontal
start_x = 0.0          # Posición X inicial
start_y = 0.0          # Posición Y inicial
cut_power = 85.0       # 85% de potencia
cut_speed = 120.0      # 120 mm/min
```

#### Múltiples Cortes:
```python
cuts = [
    {
        'distance': 50.0,
        'depth': 2.0,
        'angle': 0.0,
        'start_x': 0.0,
        'start_y': 0.0
    },
    {
        'distance': 30.0,
        'depth': 2.0,
        'angle': 90.0,
        'start_x': 50.0,
        'start_y': 0.0
    }
]
```

### 📐 Ángulos de Corte

- **0°:** Horizontal (izquierda a derecha)
- **90°:** Vertical (abajo a arriba)
- **45°:** Diagonal
- **180°:** Horizontal (derecha a izquierda)
- **270°:** Vertical (arriba a abajo)

## 🔧 Configuración del Sistema

### 🖥️ Configuración del Backend

#### Archivo `backend/app.py`:
```python
# Configuración del servidor
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'previews'

# Configuración CORS
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
```

#### Variables de Entorno:
```env
# .env en directorio backend/
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
MAX_FILE_SIZE=16777216
```

### 🎨 Configuración del Frontend

#### Archivo `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

## 🎯 Optimización de Rendimiento

### ⚡ Backend:
- **Multiprocessing:** Para procesamiento de imágenes grandes
- **Caching:** Para archivos G-code generados
- **Compresión:** Para respuestas de API grandes

### 🖥️ Frontend:
- **Lazy Loading:** Para componentes pesados
- **Memoization:** Para cálculos complejos
- **Virtual Scrolling:** Para listas largas

## 🔒 Configuración de Seguridad

### 🛡️ Backend:
```python
# Validación de archivos
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Sanitización de nombres de archivo
from werkzeug.utils import secure_filename
```

### 🔐 Frontend:
```typescript
// Validación de entrada
const validateInput = (value: string) => {
  return value.length > 0 && value.length < 1000;
};
```

## 📊 Monitoreo y Logs

### 📝 Logs del Backend:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lasercraft.log'),
        logging.StreamHandler()
    ]
)
```

### 🔍 Logs del Frontend:
```typescript
// En el navegador (F12 → Console)
console.log('LaserCraft Studio - Debug Info');
```

## 🚀 Configuración de Producción

### 🖥️ Backend (Producción):
```python
# Configuración para producción
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Usar servidor WSGI
from waitress import serve
serve(app, host='0.0.0.0', port=5000)
```

### 🎨 Frontend (Producción):
```bash
# Build para producción
npm run build

# Servir archivos estáticos
npm run preview
```

---

**💡 Consejo:** Siempre prueba las configuraciones con materiales de prueba antes de usar materiales valiosos.
