# 🎨⚡ LaserCraft Studio

<div align="center">

![LaserCraft Studio](https://img.shields.io/badge/LaserCraft-Studio-blue?style=for-the-badge&logo=laser)
![LASER TREE 10W](https://img.shields.io/badge/LASER_TREE-10W-red?style=for-the-badge&logo=fire)
![React](https://img.shields.io/badge/React-18.0-blue?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)

**Aplicación Web Profesional de Generación de G-code para Grabado Láser**

*Optimizada para LASER TREE 10W (10000 mW)*

[![Demo](https://img.shields.io/badge/Ver_Demo-Live-brightgreen?style=for-the-badge)](https://github.com/godie007/LaserCraft)
[![Documentación](https://img.shields.io/badge/Documentación-README-orange?style=for-the-badge)](./docs/README.md)
[![Issues](https://img.shields.io/badge/Issues-Report-red?style=for-the-badge)](https://github.com/godie007/LaserCraft/issues)

</div>

---

## 🔥 Características Principales

### ✨ **Grabado de Texto Avanzado**
- 🎯 **Potencia optimizada** para LASER TREE 10W
- 📝 **Múltiples fuentes** (Arial, Times New Roman, Courier New)
- ⚙️ **Configuraciones predefinidas** para diferentes materiales
- 🎨 **Centrado automático** o posicionamiento manual

### 🖼️ **Procesamiento de Imágenes**
- 🖥️ **Vista previa en tiempo real** del procesamiento
- 🎛️ **Controles avanzados** de umbralización y simplificación
- 🔧 **Presets específicos** para diferentes materiales
- 📐 **Escalado automático** manteniendo proporciones

### ✂️ **Corte Láser Preciso**
- 📏 **Cortes simples y múltiples** con configuración individual
- 📐 **Ángulos personalizables** (0° a 360°)
- 🎯 **Profundidad configurable** con múltiples pasadas
- ⚡ **Presets optimizados** para cada material y grosor

### 🎮 **Vista Previa 3D**
- 🌐 **Visualización interactiva** del G-code generado
- 📊 **Representación realista** de las trayectorias del láser
- 🔍 **Zoom y rotación** para inspección detallada

---

## 🚀 Instalación Rápida

### 📋 Prerrequisitos
- **Python 3.8+**
- **Node.js 16+**
- **LASER TREE 10W** (o compatible)

### ⚡ Instalación en 3 pasos

```bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/godie007/LaserCraft.git
cd LaserCraft

# 2️⃣ Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# 3️⃣ Instalar dependencias del frontend
cd ../frontend
npm install
```

### 🎯 Ejecutar la aplicación

```bash
# Backend (Terminal 1)
cd backend
python app.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

**🌐 Abrir:** http://localhost:3000

---

## 🎨 Capturas de Pantalla

### 🏠 Pantalla Principal
![Pantalla Principal](./docs/images/1.png)
*Interfaz principal con todas las funcionalidades disponibles*

### ⚙️ Configuración de Grabado
![Configuración](./docs/images/2.png)
*Panel de configuración con presets optimizados para LASER TREE 10W*

### 🖼️ Procesamiento de Imágenes
![Procesamiento](./docs/images/3.png)
*Herramientas avanzadas de procesamiento de imágenes*

---

## 🔧 Configuraciones Optimizadas

### 📊 Presets para LASER TREE 10W

| Material | Grosor | Potencia | Velocidad | Pasadas |
|----------|--------|----------|-----------|---------|
| **Madera Blanda** | 3mm | 80% | 150 mm/min | 3 |
| **Madera Blanda** | 6mm | 90% | 100 mm/min | 5 |
| **Madera Dura** | 3mm | 85% | 120 mm/min | 4 |
| **Acrílico** | 3mm | 80% | 100 mm/min | 2 |
| **Acrílico** | 5mm | 90% | 50 mm/min | 3 |
| **MDF** | 3mm | 75% | 150 mm/min | 2 |
| **MDF** | 6mm | 90% | 80 mm/min | 3 |

### ⚡ Capacidades Máximas
- **Madera:** Hasta 10mm
- **Acrílico:** Hasta 8mm  
- **MDF:** Hasta 6mm
- **Cartón:** Hasta 5mm
- **Cuero:** Hasta 3mm

---

## 🛠️ Tecnologías Utilizadas

### 🖥️ Frontend
- **React 18** - Framework principal
- **TypeScript** - Tipado estático
- **Material-UI** - Componentes de interfaz
- **Three.js** - Visualización 3D
- **Vite** - Build tool moderno

### ⚙️ Backend
- **Python 3.8+** - Lenguaje principal
- **Flask** - Framework web
- **OpenCV** - Procesamiento de imágenes
- **NumPy** - Cálculos matemáticos
- **Matplotlib** - Generación de gráficos

### 🔧 Herramientas
- **Git** - Control de versiones
- **ESLint** - Linting de código
- **Prettier** - Formateo de código

---

## 📚 Documentación

- 📖 [Documentación Completa](./docs/README.md)
- 🎯 [Guía de Instalación](./docs/INSTALLATION.md)
- ⚙️ [Configuración Avanzada](./docs/CONFIGURATION.md)
- 🔧 [API Reference](./docs/API.md)
- 🐛 [Troubleshooting](./docs/TROUBLESHOOTING.md)

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. 🍴 Fork el proyecto
2. 🌿 Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push a la rama (`git push origin feature/AmazingFeature`)
5. 🔄 Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Diego** - [@godie007](https://github.com/godie007)

---

## 🙏 Agradecimientos

- **LASER TREE** por el excelente láser de 10W
- **Comunidad Open Source** por las librerías utilizadas
- **Contribuidores** que ayudan a mejorar el proyecto

---

<div align="center">

**⭐ Si te gusta este proyecto, ¡dale una estrella! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/godie007/LaserCraft?style=social)](https://github.com/godie007/LaserCraft/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/godie007/LaserCraft?style=social)](https://github.com/godie007/LaserCraft/network)

</div>