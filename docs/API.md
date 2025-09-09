# 🔧 API Reference - LaserCraft Studio

Documentación completa de la API REST de LaserCraft Studio.

## 🌐 Base URL

```
http://localhost:5000/api
```

## 📋 Endpoints Disponibles

### 🎯 Generación de G-code

#### `POST /api/generate`
Genera G-code desde texto.

**Request Body:**
```json
{
  "text": "CODYTION",
  "table_width": 50.0,
  "table_height": 50.0,
  "font_size": 8.0,
  "line_height": 0.7,
  "feed_rate": 60.0,
  "font_name": "Arial",
  "laser_power_max": 100.0,
  "num_layers": 30,
  "focus_height": 0.0,
  "center_text": false
}
```

**Response:**
```json
{
  "success": true,
  "filename": "laser_output_20250108_143022.gcode",
  "filepath": "backend/output/laser_output_20250108_143022.gcode",
  "total_lines": 1250,
  "download_url": "/api/download/laser_output_20250108_143022.gcode"
}
```

#### `POST /api/generate-cut`
Genera G-code para corte láser.

**Request Body:**
```json
{
  "cut_distance": 50.0,
  "cut_depth": 2.0,
  "cut_angle": 0.0,
  "start_x": 0.0,
  "start_y": 0.0,
  "cut_power": 85.0,
  "cut_speed": 120.0,
  "table_width": 50.0,
  "table_height": 50.0
}
```

**Response:**
```json
{
  "success": true,
  "filename": "laser_cut_20250108_143022.gcode",
  "filepath": "backend/output/laser_cut_20250108_143022.gcode",
  "total_lines": 45,
  "download_url": "/api/download/laser_cut_20250108_143022.gcode",
  "cut_info": {
    "distance": 50.0,
    "depth": 2.0,
    "angle": 0.0,
    "start_position": [0.0, 0.0],
    "power": 85.0,
    "speed": 120.0
  }
}
```

#### `POST /api/generate-multiple-cuts`
Genera G-code para múltiples cortes láser.

**Request Body:**
```json
{
  "cuts": [
    {
      "distance": 50.0,
      "depth": 2.0,
      "angle": 0.0,
      "start_x": 0.0,
      "start_y": 0.0
    },
    {
      "distance": 30.0,
      "depth": 2.0,
      "angle": 90.0,
      "start_x": 50.0,
      "start_y": 0.0
    }
  ],
  "table_width": 50.0,
  "table_height": 50.0,
  "cut_power": 85.0,
  "cut_speed": 120.0
}
```

**Response:**
```json
{
  "success": true,
  "filename": "laser_multiple_cuts_20250108_143022.gcode",
  "filepath": "backend/output/laser_multiple_cuts_20250108_143022.gcode",
  "total_lines": 90,
  "download_url": "/api/download/laser_multiple_cuts_20250108_143022.gcode",
  "cuts_count": 2,
  "cut_power": 85.0,
  "cut_speed": 120.0
}
```

### 🖼️ Procesamiento de Imágenes

#### `POST /api/upload-image`
Sube una imagen para procesamiento.

**Request:** `multipart/form-data`
- `image`: Archivo de imagen (JPG, PNG, BMP, TIFF)

**Response:**
```json
{
  "success": true,
  "message": "Imagen subida correctamente",
  "filename": "image_20250108_143022.jpg",
  "filepath": "backend/uploads/image_20250108_143022.jpg",
  "image_info": {
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "mode": "RGB",
    "file_size": 245760,
    "aspect_ratio": 1.78
  }
}
```

#### `POST /api/process-image`
Procesa una imagen subida.

**Request Body:**
```json
{
  "filepath": "backend/uploads/image_20250108_143022.jpg",
  "table_width": 50.0,
  "table_height": 50.0,
  "blur_kernel": 3,
  "threshold_method": "simple",
  "min_area": 100,
  "simplify_factor": 0.02,
  "fill_spacing": 2,
  "figure_width": 50
}
```

**Response:**
```json
{
  "success": true,
  "message": "Imagen procesada correctamente",
  "preview_url": "/api/preview/preview_20250108_143022.png",
  "contours_count": 1250,
  "contours": [
    [10.5, 20.3],
    [15.2, 25.1],
    [20.8, 30.7]
  ]
}
```

#### `POST /api/generate-from-image`
Genera G-code desde imagen procesada.

**Request Body:**
```json
{
  "filepath": "backend/uploads/image_20250108_143022.jpg",
  "table_width": 50.0,
  "table_height": 50.0,
  "font_size": 8.0,
  "laser_power_max": 100.0,
  "num_layers": 1,
  "feed_rate": 300.0,
  "line_height": 0.7,
  "focus_height": 0.0,
  "center_text": false,
  "blur_kernel": 3,
  "threshold_method": "simple",
  "min_area": 100,
  "simplify_factor": 0.02,
  "fill_spacing": 2,
  "laser_power": 100,
  "feed_rate": 300,
  "figure_width": 50
}
```

**Response:**
```json
{
  "success": true,
  "message": "G-code generado correctamente desde imagen",
  "filename": "image_laser_output_20250108_143022.gcode",
  "download_url": "/api/download/image_laser_output_20250108_143022.gcode",
  "gcode": "G21\nG90\nM5\n..."
}
```

### 📁 Gestión de Archivos

#### `GET /api/files`
Lista archivos G-code generados.

**Response:**
```json
[
  {
    "filename": "laser_output_20250108_143022.gcode",
    "size": 12500,
    "created": "2025-01-08T14:30:22.123Z",
    "download_url": "/api/download/laser_output_20250108_143022.gcode"
  }
]
```

#### `GET /api/download/<filename>`
Descarga un archivo G-code.

**Response:** Archivo G-code como descarga

#### `POST /api/cleanup`
Limpia archivos G-code generados.

**Response:**
```json
{
  "success": true,
  "message": "Se eliminaron 5 archivos",
  "deleted_count": 5,
  "total_size_freed": 62500,
  "deleted_files": [
    {
      "filename": "laser_output_20250108_143022.gcode",
      "size": 12500,
      "created": "2025-01-08T14:30:22.123Z"
    }
  ]
}
```

### ⚙️ Configuración

#### `GET /api/presets`
Obtiene configuraciones predefinidas para grabado.

**Response:**
```json
{
  "wood_soft_3mm": {
    "name": "Madera Blanda 3mm",
    "description": "Pino, balsa 3mm - LASER TREE 10W",
    "parameters": {
      "laser_power_max": 80.0,
      "num_layers": 3,
      "feed_rate": 150.0,
      "line_height": 0.8,
      "focus_height": 0.0
    }
  }
}
```

#### `GET /api/cut-presets`
Obtiene configuraciones predefinidas para corte.

**Response:**
```json
{
  "wood_thin_3mm": {
    "name": "Madera Delgada (3mm)",
    "description": "Corte para madera de 3mm - LASER TREE 10W",
    "parameters": {
      "cut_power": 85.0,
      "cut_speed": 120.0,
      "cut_depth": 2.0
    }
  }
}
```

### 🔍 Utilidades

#### `GET /api/health`
Verifica el estado del API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T14:30:22.123Z",
  "version": "1.0.0"
}
```

#### `GET /api/preview/<filename>`
Obtiene vista previa de imagen procesada.

**Response:** Imagen PNG

## 📊 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 400 | Bad Request - Parámetros inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

## 🚨 Manejo de Errores

### Error 400 - Parámetros Inválidos
```json
{
  "error": "Parámetro requerido faltante: text"
}
```

### Error 404 - Archivo No Encontrado
```json
{
  "error": "Archivo no encontrado"
}
```

### Error 500 - Error del Servidor
```json
{
  "error": "Error interno del servidor"
}
```

## 🔧 Ejemplos de Uso

### 🐍 Python
```python
import requests

# Generar G-code desde texto
response = requests.post('http://localhost:5000/api/generate', json={
    'text': 'Hello World',
    'table_width': 50.0,
    'table_height': 50.0,
    'font_size': 8.0,
    'laser_power_max': 80.0
})

if response.status_code == 200:
    data = response.json()
    print(f"G-code generado: {data['filename']}")
```

### 🌐 JavaScript
```javascript
// Generar G-code desde texto
fetch('http://localhost:5000/api/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        text: 'Hello World',
        table_width: 50.0,
        table_height: 50.0,
        font_size: 8.0,
        laser_power_max: 80.0
    })
})
.then(response => response.json())
.then(data => {
    console.log('G-code generado:', data.filename);
});
```

### 📱 cURL
```bash
# Generar G-code desde texto
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello World",
    "table_width": 50.0,
    "table_height": 50.0,
    "font_size": 8.0,
    "laser_power_max": 80.0
  }'
```

## 🔒 Seguridad

### 🛡️ Validación de Entrada
- Todos los parámetros son validados
- Archivos son verificados por tipo y tamaño
- Nombres de archivo son sanitizados

### 📏 Límites
- **Tamaño máximo de archivo:** 16MB
- **Formatos de imagen permitidos:** JPG, PNG, BMP, TIFF
- **Tamaño máximo de texto:** 1000 caracteres

---

**💡 Nota:** Esta API está optimizada para el LASER TREE 10W. Ajusta los parámetros según tu láser específico.
