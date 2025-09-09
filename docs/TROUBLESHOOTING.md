# 🐛 Troubleshooting - LaserCraft Studio

Guía completa para resolver problemas comunes en LaserCraft Studio.

## 🚨 Problemas de Instalación

### ❌ Error: "Python no encontrado"

**Síntomas:**
```
'python' no se reconoce como un comando interno o externo
```

**Solución:**
1. Descargar Python desde [python.org](https://www.python.org/downloads/)
2. Instalar con "Add to PATH" marcado
3. Reiniciar terminal
4. Verificar: `python --version`

### ❌ Error: "Node.js no encontrado"

**Síntomas:**
```
'node' no se reconoce como un comando interno o externo
```

**Solución:**
1. Descargar Node.js desde [nodejs.org](https://nodejs.org/)
2. Instalar versión LTS
3. Reiniciar terminal
4. Verificar: `node --version`

### ❌ Error: "Dependencias no se instalan"

**Síntomas:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solución:**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt --force-reinstall

# Si persiste, usar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## 🌐 Problemas de Conexión

### ❌ Error: "Cannot connect to backend"

**Síntomas:**
- Frontend no puede conectar al backend
- Error 404 en requests a `/api/*`

**Solución:**
1. Verificar que el backend esté ejecutándose:
   ```bash
   cd backend
   python app.py
   ```
2. Verificar puerto 5000 esté libre:
   ```bash
   netstat -an | findstr :5000  # Windows
   lsof -i :5000  # macOS/Linux
   ```
3. Verificar CORS en `backend/app.py`:
   ```python
   CORS(app, origins=['http://localhost:3000'])
   ```

### ❌ Error: "CORS policy"

**Síntomas:**
```
Access to fetch at 'http://localhost:5000/api/generate' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solución:**
1. Verificar configuración CORS en `backend/app.py`
2. Reiniciar backend
3. Limpiar caché del navegador (Ctrl+F5)

### ❌ Error: "Port already in use"

**Síntomas:**
```
Address already in use
```

**Solución:**
```bash
# Cambiar puerto del backend
cd backend
python app.py --port 5001

# Cambiar puerto del frontend
cd frontend
npm run dev -- --port 3001
```

## 🖼️ Problemas de Procesamiento de Imágenes

### ❌ Error: "Image not processed"

**Síntomas:**
- Imagen no se procesa
- Error al subir imagen

**Solución:**
1. Verificar formato de imagen (JPG, PNG, BMP, TIFF)
2. Verificar tamaño (máximo 16MB)
3. Verificar permisos de escritura en `backend/uploads/`
4. Revisar logs del backend

### ❌ Error: "No contours found"

**Síntomas:**
- Imagen se sube pero no se encuentran contornos
- Mensaje "No se pudieron extraer contornos"

**Solución:**
1. Ajustar parámetros de procesamiento:
   - Reducir `min_area` (ej: 50 en lugar de 100)
   - Cambiar `threshold_method` a "otsu"
   - Ajustar `blur_kernel` (ej: 1 en lugar de 3)
2. Usar imagen con más contraste
3. Probar con imagen en blanco y negro

### ❌ Error: "Preview not generated"

**Síntomas:**
- Vista previa no se genera
- Error 404 en `/api/preview/*`

**Solución:**
1. Verificar directorio `backend/previews/` existe
2. Verificar permisos de escritura
3. Revisar logs del backend

## ✂️ Problemas de Corte Láser

### ❌ Error: "Cut parameters invalid"

**Síntomas:**
- Error al generar corte
- Parámetros no válidos

**Solución:**
1. Verificar valores numéricos:
   - `cut_distance` > 0
   - `cut_depth` > 0
   - `cut_angle` entre 0 y 360
   - `cut_power` entre 1 y 100
2. Usar presets predefinidos
3. Verificar que `table_width` y `table_height` sean positivos

### ❌ Error: "Multiple cuts empty"

**Síntomas:**
- Error al generar múltiples cortes
- Lista de cortes vacía

**Solución:**
1. Agregar al menos un corte
2. Verificar que cada corte tenga:
   - `distance` > 0
   - `depth` > 0
   - `angle` válido

## 🎯 Problemas de Generación de G-code

### ❌ Error: "G-code generation failed"

**Síntomas:**
- Error al generar G-code
- Archivo no se crea

**Solución:**
1. Verificar directorio `backend/output/` existe
2. Verificar permisos de escritura
3. Revisar logs del backend
4. Verificar parámetros válidos

### ❌ Error: "Download failed"

**Síntomas:**
- Archivo G-code no se descarga
- Error 404 en descarga

**Solución:**
1. Verificar que el archivo existe en `backend/output/`
2. Refrescar página (Ctrl+F5)
3. Verificar URL de descarga
4. Revisar logs del backend

## 🖥️ Problemas de Interfaz

### ❌ Error: "Component not rendering"

**Síntomas:**
- Componentes no se muestran
- Página en blanco

**Solución:**
1. Verificar consola del navegador (F12)
2. Limpiar caché del navegador
3. Reinstalar dependencias:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### ❌ Error: "3D preview not working"

**Síntomas:**
- Vista previa 3D no se carga
- Error en Three.js

**Solución:**
1. Verificar que hay G-code generado
2. Verificar consola del navegador
3. Actualizar navegador
4. Verificar WebGL habilitado

## 🔧 Problemas de Rendimiento

### ❌ Error: "Application slow"

**Síntomas:**
- Aplicación muy lenta
- Timeouts en requests

**Solución:**
1. Verificar recursos del sistema (RAM, CPU)
2. Cerrar otras aplicaciones
3. Reducir tamaño de imágenes
4. Usar parámetros de procesamiento más simples

### ❌ Error: "Memory issues"

**Síntomas:**
- Aplicación se cuelga
- Error de memoria

**Solución:**
1. Reiniciar aplicación
2. Limpiar archivos temporales
3. Reducir tamaño de imágenes
4. Aumentar RAM del sistema

## 📱 Problemas de Navegador

### ❌ Error: "Browser not supported"

**Síntomas:**
- Aplicación no funciona
- Errores de JavaScript

**Solución:**
1. Usar navegador moderno:
   - Chrome 90+
   - Firefox 88+
   - Safari 14+
   - Edge 90+
2. Habilitar JavaScript
3. Habilitar WebGL
4. Limpiar caché y cookies

### ❌ Error: "WebGL not available"

**Síntomas:**
- Vista previa 3D no funciona
- Error de WebGL

**Solución:**
1. Habilitar WebGL en navegador
2. Actualizar drivers de gráficos
3. Verificar hardware compatible
4. Usar navegador diferente

## 🔍 Debugging

### 📝 Logs del Backend

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)

# Ver logs en consola
python app.py
```

### 🖥️ Logs del Frontend

```javascript
// En consola del navegador (F12)
console.log('Debug info:', data);

// Verificar requests
fetch('/api/health')
  .then(response => response.json())
  .then(data => console.log('API Status:', data));
```

### 🔧 Herramientas de Debug

1. **Backend:** Logs en consola
2. **Frontend:** F12 → Console
3. **Network:** F12 → Network
4. **Performance:** F12 → Performance

## 📞 Soporte

### 🆘 Obtener Ayuda

1. **Revisar esta guía** primero
2. **Buscar en issues** de GitHub
3. **Crear nuevo issue** con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs de error
   - Información del sistema

### 📋 Información para Reportar

```bash
# Información del sistema
python --version
node --version
npm --version

# Logs del backend
cd backend
python app.py

# Logs del frontend
cd frontend
npm run dev
```

### 🐛 Reportar Bug

```markdown
**Descripción del problema:**
[Descripción clara del problema]

**Pasos para reproducir:**
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Comportamiento esperado:**
[Lo que debería pasar]

**Comportamiento actual:**
[Lo que está pasando]

**Información del sistema:**
- OS: [Windows/macOS/Linux]
- Python: [versión]
- Node.js: [versión]
- Navegador: [versión]

**Logs de error:**
[Pegar logs aquí]
```

---

**💡 Consejo:** Siempre incluye logs de error y información del sistema al reportar problemas.
