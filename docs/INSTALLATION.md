# 🚀 Guía de Instalación - LaserCraft Studio

Esta guía te ayudará a instalar y configurar LaserCraft Studio en tu sistema.

## 📋 Prerrequisitos

### 🖥️ Sistema Operativo
- **Windows 10/11** (recomendado)
- **macOS 10.15+**
- **Ubuntu 18.04+** / **Debian 10+**

### 🔧 Software Requerido
- **Python 3.8+** - [Descargar Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Descargar Node.js](https://nodejs.org/)
- **Git** - [Descargar Git](https://git-scm.com/)

### ⚡ Hardware Recomendado
- **RAM:** Mínimo 4GB, recomendado 8GB+
- **Almacenamiento:** 2GB libres
- **Procesador:** Dual-core 2.0GHz+
- **Láser:** LASER TREE 10W (o compatible)

## 🔧 Instalación Paso a Paso

### 1️⃣ Clonar el Repositorio

```bash
# Clonar desde GitHub
git clone https://github.com/godie007/LaserCraft.git
cd LaserCraft
```

### 2️⃣ Configurar el Backend (Python)

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3️⃣ Configurar el Frontend (React)

```bash
# Navegar al directorio frontend
cd ../frontend

# Instalar dependencias
npm install
```

### 4️⃣ Verificar la Instalación

```bash
# Verificar Python
python --version
# Debería mostrar: Python 3.8.x o superior

# Verificar Node.js
node --version
# Debería mostrar: v16.x.x o superior

# Verificar npm
npm --version
# Debería mostrar: 8.x.x o superior
```

## 🎯 Ejecutar la Aplicación

### 🖥️ Opción 1: Ejecución Manual

```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 🖥️ Opción 2: Scripts Automatizados

#### Windows:
```bash
# Ejecutar backend
start_backend.bat

# Ejecutar frontend (en otra terminal)
start_frontend.bat
```

#### macOS/Linux:
```bash
# Ejecutar backend
./start_backend.sh

# Ejecutar frontend (en otra terminal)
./start_frontend.sh
```

## 🌐 Acceder a la Aplicación

Una vez que ambos servicios estén ejecutándose:

1. **Backend:** http://localhost:5000
2. **Frontend:** http://localhost:3000
3. **Aplicación:** Abre http://localhost:3000 en tu navegador

## ⚙️ Configuración Avanzada

### 🔧 Variables de Entorno

Crea un archivo `.env` en el directorio `backend/`:

```env
# Configuración del servidor
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Configuración de archivos
MAX_FILE_SIZE=16777216
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output
PREVIEW_FOLDER=previews

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 🎨 Personalización de la Interfaz

Puedes personalizar la interfaz editando:

- **Colores:** `frontend/src/App.css`
- **Componentes:** `frontend/src/App.tsx`
- **Configuración:** `frontend/vite.config.ts`

## 🐛 Solución de Problemas

### ❌ Error: "Python no encontrado"
```bash
# Verificar instalación de Python
python --version
# Si no funciona, reinstalar Python desde python.org
```

### ❌ Error: "Node.js no encontrado"
```bash
# Verificar instalación de Node.js
node --version
# Si no funciona, reinstalar Node.js desde nodejs.org
```

### ❌ Error: "Puerto en uso"
```bash
# Cambiar puerto del backend
cd backend
python app.py --port 5001

# Cambiar puerto del frontend
cd frontend
npm run dev -- --port 3001
```

### ❌ Error: "Dependencias no encontradas"
```bash
# Reinstalar dependencias del backend
cd backend
pip install -r requirements.txt --force-reinstall

# Reinstalar dependencias del frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### ❌ Error: "CORS"
```bash
# Verificar que el backend esté ejecutándose en puerto 5000
# Verificar que el frontend esté ejecutándose en puerto 3000
# Verificar configuración de CORS en app.py
```

## 🔄 Actualización

Para actualizar LaserCraft Studio:

```bash
# Obtener últimos cambios
git pull origin main

# Actualizar dependencias del backend
cd backend
pip install -r requirements.txt --upgrade

# Actualizar dependencias del frontend
cd ../frontend
npm update
```

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. **Revisar logs:** Verifica la consola del navegador (F12)
2. **Verificar puertos:** Asegúrate de que los puertos 3000 y 5000 estén libres
3. **Crear issue:** Reporta el problema en [GitHub Issues](https://github.com/godie007/LaserCraft/issues)
4. **Documentación:** Revisa la documentación completa en `docs/`

## ✅ Verificación Final

Una vez instalado correctamente, deberías poder:

- ✅ Acceder a http://localhost:3000
- ✅ Ver la interfaz de LaserCraft Studio
- ✅ Configurar parámetros de grabado
- ✅ Generar G-code desde texto
- ✅ Procesar imágenes
- ✅ Configurar cortes láser
- ✅ Ver vista previa 3D

---

**¡Felicidades!** 🎉 LaserCraft Studio está listo para usar con tu LASER TREE 10W.
