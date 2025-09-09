# LaserCraft Studio 🎨⚡

**Aplicación Web Profesional de Generación de G-code para Grabado Láser**

Una plataforma completa y moderna para crear código G de alta precisión para grabado láser, con soporte avanzado para texto, imágenes y visualización 3D interactiva.

## 🚀 Características

- **Generación de G-code desde texto**: Convierte texto en código G para grabado láser
- **Procesamiento de imágenes**: Vectoriza imágenes y genera G-code
- **Vista previa 3D**: Visualización interactiva del resultado final
- **Interfaz web moderna**: React.js con Material-UI
- **API REST**: Backend Flask con endpoints bien documentados
- **Compatibilidad GRBL**: G-code optimizado para controladores GRBL

## 📁 Estructura del Proyecto

```
lasercraft-studio/
├── backend/                 # Servidor Flask
│   ├── app.py              # Aplicación principal
│   ├── gcode_generator.py  # Generador de G-code
│   ├── image_processor.py  # Procesador de imágenes
│   ├── requirements.txt    # Dependencias Python
│   ├── output/            # Archivos G-code generados
│   ├── uploads/           # Imágenes subidas
│   └── previews/          # Vistas previas de procesamiento
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── App.tsx        # Componente principal
│   │   └── components/    # Componentes React
│   ├── package.json       # Dependencias Node.js
│   └── vite.config.ts     # Configuración Vite
├── legacy/                # Código legacy (referencia)
│   ├── src/               # Código original
│   └── run_laser_example.* # Scripts de ejemplo
├── docs/                  # Documentación consolidada
│   └── README.md          # Índice de documentación
├── PROJECT_OVERVIEW.md    # Visión general del proyecto
├── BRANDING.md           # Guía de marca e identidad
├── README.md             # Este archivo
└── .gitignore            # Archivos ignorados por Git
```

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- npm o yarn

### Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Uso

1. **Acceder a la aplicación**: `http://localhost:5173`
2. **Generar G-code desde texto**:
   - Ingresa el texto a grabar
   - Configura parámetros (dimensiones, potencia, velocidad)
   - Genera y descarga el G-code
3. **Procesar imágenes**:
   - Sube una imagen
   - Ajusta parámetros de procesamiento
   - Genera G-code vectorizado
4. **Vista previa 3D**: Visualiza el resultado antes de grabar

## ⚙️ Parámetros Configurables

### Parámetros de Láser
- **Potencia máxima**: 0-100%
- **Velocidad de avance**: mm/min
- **Número de capas**: Para grabado profundo
- **Altura de enfoque**: mm
- **Altura de línea**: mm

### Parámetros de Imagen
- **Kernel de desenfoque**: Para suavizado
- **Método de umbralización**: Otsu, adaptativo, simple
- **Área mínima**: Filtro de contornos pequeños
- **Factor de simplificación**: Reducción de puntos

## 🔧 API Endpoints

### Texto a G-code
- `POST /api/generate-gcode` - Generar G-code desde texto

### Procesamiento de Imágenes
- `POST /api/upload-image` - Subir imagen
- `POST /api/process-image` - Procesar imagen
- `POST /api/generate-from-image` - Generar G-code desde imagen

### Gestión de Archivos
- `GET /api/files` - Listar archivos generados
- `GET /api/download/<filename>` - Descargar archivo
- `DELETE /api/files/<filename>` - Eliminar archivo

### Configuración
- `GET /api/presets` - Obtener presets de configuración

## 📊 Compatibilidad

- **Controladores GRBL**: Compatible con firmware GRBL estándar
- **Formatos de imagen**: PNG, JPG, JPEG, BMP
- **Navegadores**: Chrome, Firefox, Safari, Edge (versiones modernas)

## 🐛 Solución de Problemas

### Problemas Comunes
1. **Error 404 en descarga**: Refrescar página (Ctrl+F5)
2. **Imagen no se procesa**: Verificar formato y tamaño
3. **G-code no compatible**: Usar presets recomendados

### Logs de Debug
- **Backend**: Logs en consola del servidor Flask
- **Frontend**: F12 → Console para logs de debug

## 📚 Documentación Adicional

- [Documentación del Backend](docs/backend/)
- [Documentación del Frontend](docs/frontend/)
- [Correcciones y Fixes](docs/fixes/)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Revisar la documentación en `docs/`
- Verificar logs de debug en la consola del navegador

---

**LaserCraft Studio** - Desarrollado con ❤️ para la comunidad de grabado láser

*Transformando ideas en realidad con precisión láser* ⚡🎨