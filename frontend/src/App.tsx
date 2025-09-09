import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tabs,
  Tab,
  Tooltip
} from '@mui/material';
import {
  Download,
  PlayArrow,
  CheckCircle,
  Error,
  Warning,
  Settings,
  FileDownload,
  GetApp,
  ViewInAr,
  Code,
  DeleteSweep,
  Image,
  Upload,
  Visibility,
  ContentCut,
  Add,
  Remove
} from '@mui/icons-material';
import axios from 'axios';
import GCodePreview3D from './components/GCodePreview3D';

// Tipos TypeScript
interface LaserParameters {
  text: string;
  table_width: number;
  table_height: number;
  font_size: number;
  line_height: number;
  feed_rate: number;
  font_name: string;
  laser_power_max: number;
  num_layers: number;
  focus_height: number;
  center_text: boolean;
}

interface Preset {
  name: string;
  description: string;
  parameters: Partial<LaserParameters>;
}

interface GeneratedFile {
  filename: string;
  size: number;
  created: string;
  download_url: string;
}

interface ImageInfo {
  width: number;
  height: number;
  format: string;
  mode: string;
  file_size: number;
  aspect_ratio: number;
}

interface ImageProcessingParams {
  blur_kernel: number;
  threshold_method: string;
  min_area: number;
  simplify_factor: number;
  fill_spacing: number;
  laser_power: number;
  feed_rate: number;
  figure_width: number;
}

interface CutParameters {
  cut_distance: number;
  cut_depth: number;
  cut_angle: number;
  start_x: number;
  start_y: number;
  cut_power: number;
  cut_speed: number;
}

interface MultipleCut {
  distance: number;
  depth: number;
  angle: number;
  start_x?: number;
  start_y?: number;
}

interface CutPreset {
  name: string;
  description: string;
  parameters: Partial<CutParameters>;
}

const API_BASE_URL = 'http://localhost:5000/api';

const App: React.FC = () => {
  // Estados
  const [parameters, setParameters] = useState<LaserParameters>({
    text: 'CODYTION',
    table_width: 50.0,
    table_height: 50.0,
    font_size: 8.0,
    line_height: 0.7,
    feed_rate: 60.0,
    font_name: 'Arial',
    laser_power_max: 100.0,
    num_layers: 30,
    focus_height: 0.0,
    center_text: false
  });

  const [presets, setPresets] = useState<Record<string, Preset>>({});
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'warning', message: string } | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [generatedGCode, setGeneratedGCode] = useState<string>('');
  const [activeTab, setActiveTab] = useState(0);
  const [isCleaning, setIsCleaning] = useState(false);
  
  // Estados para corte láser
  const [cutPresets, setCutPresets] = useState<Record<string, CutPreset>>({});
  const [cutParameters, setCutParameters] = useState<CutParameters>({
    cut_distance: 50.0,
    cut_depth: 2.0,
    cut_angle: 0.0,
    start_x: 0.0,
    start_y: 0.0,
    cut_power: 85.0,
    cut_speed: 120.0
  });
  const [multipleCuts, setMultipleCuts] = useState<MultipleCut[]>([]);
  const [isGeneratingCut, setIsGeneratingCut] = useState(false);
  
  // Estados para procesamiento de imágenes
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imageInfo, setImageInfo] = useState<ImageInfo | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [uploadedFilePath, setUploadedFilePath] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [imageProcessingParams, setImageProcessingParams] = useState<ImageProcessingParams>({
    blur_kernel: 3,
    threshold_method: 'simple',
    min_area: 100,
    simplify_factor: 0.01,
    fill_spacing: 2,
    laser_power: 100,
    feed_rate: 300,
    figure_width: 50
  });

  // Cargar presets al montar el componente
  useEffect(() => {
    loadPresets();
    loadCutPresets();
    loadGeneratedFiles();
  }, []);

  const loadPresets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/presets`);
      setPresets(response.data);
    } catch (error) {
      console.error('Error loading presets:', error);
    }
  };

  const loadCutPresets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cut-presets`);
      setCutPresets(response.data);
    } catch (error) {
      console.error('Error loading cut presets:', error);
    }
  };

  const loadGeneratedFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files`);
      setGeneratedFiles(response.data);
    } catch (error) {
      console.error('Error loading files:', error);
    }
  };

  const handleParameterChange = (field: keyof LaserParameters, value: any) => {
    setParameters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const applyPreset = (presetKey: string) => {
    const preset = presets[presetKey];
    if (preset) {
      setParameters(prev => ({
        ...prev,
        ...preset.parameters
      }));
      setAlert({ type: 'success', message: `Preset "${preset.name}" aplicado` });
    }
  };

  const generateGCode = async () => {
    setIsGenerating(true);
    setAlert(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, parameters);
      
      if (response.data.success) {
        setAlert({ 
          type: 'success', 
          message: `G-code generado exitosamente: ${response.data.total_lines} líneas. Descargando archivo...` 
        });
        
        // Obtener el contenido del G-code para la vista previa
        try {
          const gcodeResponse = await axios.get(`${API_BASE_URL}/download/${response.data.filename}`, {
            responseType: 'text'
          });
          setGeneratedGCode(gcodeResponse.data);
          setActiveTab(3); // Cambiar a la pestaña de vista previa
        } catch (gcodeError) {
          console.error('Error obteniendo G-code para vista previa:', gcodeError);
        }
        
        // Descargar automáticamente el archivo generado
        setIsDownloading(true);
        const filename = response.data.filename;
        console.log('DEBUG TEXT - API_BASE_URL:', API_BASE_URL);
        console.log('DEBUG TEXT - filename:', filename);
        const downloadUrl = `${API_BASE_URL.replace('/api', '')}/api/download/${filename}`;
        console.log('DEBUG TEXT - downloadUrl construida:', downloadUrl);
        
        // Crear enlace temporal para descarga
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Limpiar el enlace después de un breve delay
        setTimeout(() => {
          document.body.removeChild(link);
          setIsDownloading(false);
          setAlert({ 
            type: 'success', 
            message: `G-code generado y descargado exitosamente: ${response.data.total_lines} líneas` 
          });
        }, 1000);
        
        loadGeneratedFiles(); // Recargar lista de archivos
      }
    } catch (error: any) {
      setAlert({ 
        type: 'error', 
        message: error.response?.data?.error || 'Error al generar G-code' 
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const validateGCode = async (filename: string) => {
    setIsValidating(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/validate`, { filename });
      setValidationResult(response.data);
      
      if (response.data.is_valid) {
        setAlert({ type: 'success', message: 'G-code válido - Sin comandos peligrosos en Z' });
      } else {
        setAlert({ type: 'warning', message: `G-code inválido - ${response.data.errors.length} errores encontrados` });
      }
    } catch (error: any) {
      setAlert({ 
        type: 'error', 
        message: error.response?.data?.error || 'Error al validar G-code' 
      });
    } finally {
      setIsValidating(false);
    }
  };

  const downloadFile = (filename: string) => {
    console.log('DEBUG MANUAL - API_BASE_URL:', API_BASE_URL);
    console.log('DEBUG MANUAL - filename:', filename);
    const downloadUrl = `${API_BASE_URL.replace('/api', '')}/api/download/${filename}`;
    console.log('DEBUG MANUAL - downloadUrl construida:', downloadUrl);
    
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    
    // Limpiar el enlace después de un breve delay
    setTimeout(() => {
      document.body.removeChild(link);
    }, 100);
  };

  const cleanupFiles = async () => {
    if (generatedFiles.length === 0) {
      setAlert({ type: 'warning', message: 'No hay archivos para limpiar' });
      return;
    }

    if (!window.confirm(`¿Estás seguro de que quieres eliminar todos los archivos generados? Se eliminarán ${generatedFiles.length} archivos.`)) {
      return;
    }

    setIsCleaning(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/cleanup`);
      
      if (response.data.success) {
        setAlert({ 
          type: 'success', 
          message: `Se eliminaron ${response.data.deleted_count} archivos (${(response.data.total_size_freed / 1024).toFixed(1)} KB liberados)` 
        });
        // Recargar la lista de archivos
        loadGeneratedFiles();
      } else {
        setAlert({ type: 'error', message: 'Error al limpiar archivos' });
      }
    } catch (error) {
      console.error('Error al limpiar archivos:', error);
      setAlert({ type: 'error', message: 'Error al limpiar archivos' });
    } finally {
      setIsCleaning(false);
    }
  };

  // Funciones para procesamiento de imágenes
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedImage(file);
      
      // Crear preview local
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadImage = async () => {
    if (!uploadedImage) {
      setAlert({ type: 'warning', message: 'Selecciona una imagen primero' });
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', uploadedImage);

      const response = await axios.post(`${API_BASE_URL}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setImageInfo(response.data.image_info);
        setUploadedFilePath(response.data.filepath);
        setAlert({ type: 'success', message: 'Imagen subida correctamente' });
      } else {
        setAlert({ type: 'error', message: 'Error al subir imagen' });
      }
    } catch (error) {
      console.error('Error al subir imagen:', error);
      setAlert({ type: 'error', message: 'Error al subir imagen' });
    } finally {
      setIsUploading(false);
    }
  };

  const processImage = async () => {
    if (!uploadedImage || !imageInfo || !uploadedFilePath) {
      setAlert({ type: 'warning', message: 'Sube una imagen primero' });
      return;
    }

    setIsProcessing(true);
    try {
      const requestData = {
        filepath: uploadedFilePath,
        table_width: parameters.table_width,
        table_height: parameters.table_height,
        ...imageProcessingParams
      };
      
      console.log('Enviando solicitud de procesamiento:', requestData);
      
      const response = await axios.post(`${API_BASE_URL}/process-image`, requestData);
      
      console.log('Respuesta recibida:', response.data);

      if (response.data.success) {
        setAlert({ 
          type: 'success', 
          message: `Imagen procesada correctamente. ${response.data.contours_count} contornos detectados` 
        });
        // Aquí podrías mostrar la vista previa del procesamiento
      } else {
        setAlert({ type: 'error', message: 'Error al procesar imagen' });
      }
    } catch (error) {
      console.error('Error al procesar imagen:', error);
      console.error('Response data:', response?.data);
      console.error('Response status:', response?.status);
      setAlert({ type: 'error', message: `Error al procesar imagen: ${error.message || 'Error desconocido'}` });
    } finally {
      setIsProcessing(false);
    }
  };

  const applyImagePreset = (presetType: string) => {
    const presets = {
      superficial_rapido: {
        blur_kernel: 5,
        threshold_method: 'simple',
        min_area: 200,
        simplify_factor: 0.05,
        fill_spacing: 4,
        laser_power: 25,
        feed_rate: 800,
        figure_width: 50
      },
      calidad_media: {
        blur_kernel: 3,
        threshold_method: 'simple',
        min_area: 100,
        simplify_factor: 0.02,
        fill_spacing: 2,
        laser_power: 50,
        feed_rate: 400,
        figure_width: 50
      },
      alta_calidad: {
        blur_kernel: 1,
        threshold_method: 'otsu',
        min_area: 50,
        simplify_factor: 0.01,
        fill_spacing: 1,
        laser_power: 75,
        feed_rate: 200,
        figure_width: 50
      },
      ultra_rapido: {
        blur_kernel: 7,
        threshold_method: 'simple',
        min_area: 500,
        simplify_factor: 0.1,
        fill_spacing: 6,
        laser_power: 40,
        feed_rate: 1200,
        figure_width: 50
      },
      madera: {
        blur_kernel: 3,
        threshold_method: 'simple',
        min_area: 150,
        simplify_factor: 0.03,
        fill_spacing: 2,
        laser_power: 60,
        feed_rate: 300,
        figure_width: 50
      },
      acrilico: {
        blur_kernel: 2,
        threshold_method: 'otsu',
        min_area: 80,
        simplify_factor: 0.015,
        fill_spacing: 1.5,
        laser_power: 45,
        feed_rate: 250,
        figure_width: 50
      },
      cuero: {
        blur_kernel: 4,
        threshold_method: 'simple',
        min_area: 120,
        simplify_factor: 0.04,
        fill_spacing: 3,
        laser_power: 30,
        feed_rate: 350,
        figure_width: 50
      },
      papel: {
        blur_kernel: 5,
        threshold_method: 'simple',
        min_area: 300,
        simplify_factor: 0.08,
        fill_spacing: 5,
        laser_power: 15,
        feed_rate: 600,
        figure_width: 50
      }
    };

    const preset = presets[presetType as keyof typeof presets];
    if (preset) {
      setImageProcessingParams(preset);
      
      const presetNames = {
        superficial_rapido: 'Superficial Rápido',
        calidad_media: 'Calidad Media',
        alta_calidad: 'Alta Calidad',
        ultra_rapido: 'Ultra Rápido',
        madera: 'Madera',
        acrilico: 'Acrílico',
        cuero: 'Cuero',
        papel: 'Papel/Cartón'
      };
      
      setAlert({ 
        type: 'success', 
        message: `Configuración "${presetNames[presetType as keyof typeof presetNames]}" aplicada correctamente` 
      });
    }
  };

  const generateGCodeFromImage = async () => {
    if (!uploadedImage || !imageInfo || !uploadedFilePath) {
      setAlert({ type: 'warning', message: 'Sube y procesa una imagen primero' });
      return;
    }

    setIsGenerating(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-from-image`, {
        filepath: uploadedFilePath,
        table_width: parameters.table_width,
        table_height: parameters.table_height,
        font_size: parameters.font_size,
        laser_power_max: parameters.laser_power_max,
        num_layers: parameters.num_layers,
        feed_rate: parameters.feed_rate,
        line_height: parameters.line_height,
        focus_height: parameters.focus_height,
        center_text: parameters.center_text,
        ...imageProcessingParams
      });

      if (response.data.success) {
        setGeneratedGCode(response.data.gcode);
        setAlert({ type: 'success', message: 'G-code generado correctamente desde imagen' });
        
        // Descargar archivo automáticamente
        console.log('DEBUG - API_BASE_URL:', API_BASE_URL);
        console.log('DEBUG - response.data.download_url:', response.data.download_url);
        const downloadUrl = `${API_BASE_URL.replace('/api', '')}${response.data.download_url}`;
        console.log('DEBUG - downloadUrl construida:', downloadUrl);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = response.data.filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Cambiar a vista previa 3D
        setActiveTab(3);
        
        // Recargar lista de archivos
        loadGeneratedFiles();
      } else {
        setAlert({ type: 'error', message: 'Error al generar G-code desde imagen' });
      }
    } catch (error) {
      console.error('Error al generar G-code desde imagen:', error);
      setAlert({ type: 'error', message: 'Error al generar G-code desde imagen' });
    } finally {
      setIsGenerating(false);
    }
  };

  // Funciones para corte láser
  const handleCutParameterChange = (field: keyof CutParameters, value: any) => {
    setCutParameters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const applyCutPreset = (presetKey: string) => {
    const preset = cutPresets[presetKey];
    if (preset) {
      setCutParameters(prev => ({
        ...prev,
        ...preset.parameters
      }));
      setAlert({ type: 'success', message: `Preset de corte "${preset.name}" aplicado` });
    }
  };

  const generateCutGCode = async () => {
    setIsGeneratingCut(true);
    setAlert(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-cut`, {
        ...cutParameters,
        table_width: parameters.table_width,
        table_height: parameters.table_height
      });
      
      if (response.data.success) {
        setAlert({ 
          type: 'success', 
          message: `G-code de corte generado exitosamente: ${response.data.total_lines} líneas. Descargando archivo...` 
        });
        
        // Obtener el contenido del G-code para la vista previa
        try {
          const gcodeResponse = await axios.get(`${API_BASE_URL}/download/${response.data.filename}`, {
            responseType: 'text'
          });
          setGeneratedGCode(gcodeResponse.data);
          setActiveTab(4); // Cambiar a la pestaña de G-code
        } catch (gcodeError) {
          console.error('Error obteniendo G-code para vista previa:', gcodeError);
        }
        
        // Descargar automáticamente el archivo generado
        setIsDownloading(true);
        const filename = response.data.filename;
        const downloadUrl = `${API_BASE_URL.replace('/api', '')}/api/download/${filename}`;
        
        // Crear enlace temporal para descarga
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Limpiar el enlace después de un breve delay
        setTimeout(() => {
          document.body.removeChild(link);
          setIsDownloading(false);
          setAlert({ 
            type: 'success', 
            message: `G-code de corte generado y descargado exitosamente: ${response.data.total_lines} líneas` 
          });
        }, 1000);
        
        loadGeneratedFiles(); // Recargar lista de archivos
      }
    } catch (error: any) {
      setAlert({ 
        type: 'error', 
        message: error.response?.data?.error || 'Error al generar G-code de corte' 
      });
    } finally {
      setIsGeneratingCut(false);
    }
  };

  const addMultipleCut = () => {
    setMultipleCuts(prev => [...prev, {
      distance: 50.0,
      depth: 2.0,
      angle: 0.0,
      start_x: 0.0,
      start_y: 0.0
    }]);
  };

  const removeMultipleCut = (index: number) => {
    setMultipleCuts(prev => prev.filter((_, i) => i !== index));
  };

  const updateMultipleCut = (index: number, field: keyof MultipleCut, value: any) => {
    setMultipleCuts(prev => prev.map((cut, i) => 
      i === index ? { ...cut, [field]: value } : cut
    ));
  };

  const generateMultipleCutsGCode = async () => {
    if (multipleCuts.length === 0) {
      setAlert({ type: 'warning', message: 'Agrega al menos un corte' });
      return;
    }

    setIsGeneratingCut(true);
    setAlert(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-multiple-cuts`, {
        cuts: multipleCuts,
        table_width: parameters.table_width,
        table_height: parameters.table_height,
        cut_power: cutParameters.cut_power,
        cut_speed: cutParameters.cut_speed
      });
      
      if (response.data.success) {
        setAlert({ 
          type: 'success', 
          message: `G-code de ${response.data.cuts_count} cortes generado exitosamente: ${response.data.total_lines} líneas. Descargando archivo...` 
        });
        
        // Obtener el contenido del G-code para la vista previa
        try {
          const gcodeResponse = await axios.get(`${API_BASE_URL}/download/${response.data.filename}`, {
            responseType: 'text'
          });
          setGeneratedGCode(gcodeResponse.data);
          setActiveTab(4); // Cambiar a la pestaña de G-code
        } catch (gcodeError) {
          console.error('Error obteniendo G-code para vista previa:', gcodeError);
        }
        
        // Descargar automáticamente el archivo generado
        setIsDownloading(true);
        const filename = response.data.filename;
        const downloadUrl = `${API_BASE_URL.replace('/api', '')}/api/download/${filename}`;
        
        // Crear enlace temporal para descarga
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Limpiar el enlace después de un breve delay
        setTimeout(() => {
          document.body.removeChild(link);
          setIsDownloading(false);
          setAlert({ 
            type: 'success', 
            message: `G-code de ${response.data.cuts_count} cortes generado y descargado exitosamente: ${response.data.total_lines} líneas` 
          });
        }, 1000);
        
        loadGeneratedFiles(); // Recargar lista de archivos
      }
    } catch (error: any) {
      setAlert({ 
        type: 'error', 
        message: error.response?.data?.error || 'Error al generar G-code de múltiples cortes' 
      });
    } finally {
      setIsGeneratingCut(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          🎨⚡ LaserCraft Studio
        </Typography>
        <Typography variant="h6" component="h2" gutterBottom align="center" color="text.secondary" sx={{ mb: 2 }}>
          Aplicación Web Profesional de Generación de G-code para Grabado Láser
        </Typography>
        
        <Typography variant="h5" align="center" color="primary.main" sx={{ mb: 2, fontWeight: 'bold' }}>
          🔥 LASER TREE 10W (10000 mW) - Optimizado
        </Typography>
        
        <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Transformando ideas en realidad con precisión láser • Texto • Imágenes • Cortes • Vista 3D
        </Typography>

        {alert && (
          <Alert 
            severity={alert.type} 
            sx={{ mb: 3 }}
            onClose={() => setAlert(null)}
          >
            {alert.message}
          </Alert>
        )}

        {/* Pestañas */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab 
              icon={<Settings />} 
              label="Configuración" 
              iconPosition="start"
            />
            <Tab 
              icon={<Image />} 
              label="Procesar Imagen" 
              iconPosition="start"
            />
            <Tab 
              icon={<ContentCut />} 
              label="Corte Láser" 
              iconPosition="start"
            />
            <Tab 
              icon={<ViewInAr />} 
              label="Vista Previa 3D" 
              iconPosition="start"
              disabled={!generatedGCode}
            />
            <Tab 
              icon={<Code />} 
              label="G-code" 
              iconPosition="start"
              disabled={!generatedGCode}
            />
          </Tabs>
        </Box>

        {/* Contenido de las pestañas */}
        {activeTab === 0 && (
          <Grid container spacing={4}>
            {/* Panel de Parámetros */}
            <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  <Settings sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Parámetros del Láser
                </Typography>
                
                <Grid container spacing={3}>
                  {/* Texto */}
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Texto a grabar"
                      value={parameters.text}
                      onChange={(e) => handleParameterChange('text', e.target.value)}
                      variant="outlined"
                    />
                  </Grid>

                  {/* Dimensiones de tabla */}
                  <Grid item xs={6}>
                    <Tooltip title="Ancho de Tabla: Dimensiones del área de trabajo del láser en milímetros. Define el límite máximo de ancho para el grabado." arrow>
                      <TextField
                        fullWidth
                        label="Ancho de tabla (mm)"
                        type="number"
                        value={parameters.table_width}
                        onChange={(e) => handleParameterChange('table_width', parseFloat(e.target.value))}
                        variant="outlined"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip title="Alto de Tabla: Dimensiones del área de trabajo del láser en milímetros. Define el límite máximo de alto para el grabado." arrow>
                      <TextField
                        fullWidth
                        label="Alto de tabla (mm)"
                        type="number"
                        value={parameters.table_height}
                        onChange={(e) => handleParameterChange('table_height', parseFloat(e.target.value))}
                        variant="outlined"
                      />
                    </Tooltip>
                  </Grid>

                  {/* Configuración de fuente */}
                  <Grid item xs={6}>
                    <Tooltip title="Tamaño de Fuente: Altura del texto en milímetros. Valores más grandes = texto más grande. Recomendado: 6-12 mm para la mayoría de aplicaciones." arrow>
                      <TextField
                        fullWidth
                        label="Tamaño de fuente (mm)"
                        type="number"
                        value={parameters.font_size}
                        onChange={(e) => handleParameterChange('font_size', parseFloat(e.target.value))}
                        variant="outlined"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip title="Tipo de Fuente: Estilo de letra para el texto. Arial: moderna y legible, Times New Roman: clásica, Courier New: monoespaciada." arrow>
                      <FormControl fullWidth>
                        <InputLabel>Fuente</InputLabel>
                        <Select
                          value={parameters.font_name}
                          onChange={(e) => handleParameterChange('font_name', e.target.value)}
                          label="Fuente"
                        >
                          <MenuItem value="Arial">Arial</MenuItem>
                          <MenuItem value="Times New Roman">Times New Roman</MenuItem>
                          <MenuItem value="Courier New">Courier New</MenuItem>
                        </Select>
                      </FormControl>
                    </Tooltip>
                  </Grid>

                  {/* Configuración del láser */}
                  <Grid item xs={6}>
                    <Tooltip title="Potencia Máxima: Potencia máxima del láser para grabado de texto. Recomendado: 50-100% según el material. Valores más altos = grabado más profundo." arrow>
                      <TextField
                        fullWidth
                        label="Potencia máxima (%)"
                        type="number"
                        value={parameters.laser_power_max}
                        onChange={(e) => handleParameterChange('laser_power_max', parseFloat(e.target.value))}
                        variant="outlined"
                        inputProps={{ min: 1, max: 100 }}
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip title="Número de Pasadas: Cantidad de veces que el láser pasa sobre la misma línea. Más pasadas = grabado más profundo. Recomendado: 1-5 para la mayoría de materiales." arrow>
                      <TextField
                        fullWidth
                        label="Número de pasadas"
                        type="number"
                        value={parameters.num_layers}
                        onChange={(e) => handleParameterChange('num_layers', parseInt(e.target.value))}
                        variant="outlined"
                        inputProps={{ min: 1, max: 100 }}
                      />
                    </Tooltip>
                  </Grid>

                  {/* Velocidad y altura */}
                  <Grid item xs={6}>
                    <Tooltip title="Velocidad de Alimentación: Velocidad de movimiento del láser para grabado de texto. Valores más bajos = mejor calidad pero más lento. Recomendado: 60-300 mm/min." arrow>
                      <TextField
                        fullWidth
                        label="Velocidad (mm/min)"
                        type="number"
                        value={parameters.feed_rate}
                        onChange={(e) => handleParameterChange('feed_rate', parseFloat(e.target.value))}
                        variant="outlined"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6}>
                    <Tooltip title="Altura de Línea: Espaciado vertical entre líneas de texto. Valores más altos = más espacio entre líneas. Recomendado: 0.5-1.0 mm para buena legibilidad." arrow>
                      <TextField
                        fullWidth
                        label="Altura de línea (mm)"
                        type="number"
                        step="0.1"
                        value={parameters.line_height}
                        onChange={(e) => handleParameterChange('line_height', parseFloat(e.target.value))}
                        variant="outlined"
                      />
                    </Tooltip>
                  </Grid>

                  {/* Opciones */}
                  <Grid item xs={12}>
                    <Tooltip title="Centrar Texto: Centra el texto en el área de trabajo. Si está desactivado, el texto empieza desde la esquina inferior izquierda (HOME)." arrow>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={parameters.center_text}
                            onChange={(e) => handleParameterChange('center_text', e.target.checked)}
                          />
                        }
                        label="Centrar texto en la tabla"
                      />
                    </Tooltip>
                  </Grid>
                </Grid>
              </CardContent>
              
              <CardActions>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={isGenerating || isDownloading ? <CircularProgress size={20} /> : <GetApp />}
                  onClick={generateGCode}
                  disabled={isGenerating || isDownloading}
                  fullWidth
                >
                  {isGenerating ? 'Generando...' : isDownloading ? 'Descargando...' : 'Generar y Descargar G-code'}
                </Button>
              </CardActions>
            </Card>
          </Grid>

          {/* Panel de Presets */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Configuraciones Predefinidas
                </Typography>
                
                {Object.entries(presets).map(([key, preset]) => (
                  <Box key={key} sx={{ mb: 2 }}>
                    <Button
                      variant="outlined"
                      fullWidth
                      onClick={() => applyPreset(key)}
                      sx={{ mb: 1 }}
                    >
                      {preset.name}
                    </Button>
                    <Typography variant="caption" color="text.secondary">
                      {preset.description}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>

            {/* Archivos Generados */}
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Archivos Generados
                  </Typography>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={isCleaning ? <CircularProgress size={16} /> : <DeleteSweep />}
                    onClick={cleanupFiles}
                    disabled={isCleaning || generatedFiles.length === 0}
                    size="small"
                  >
                    {isCleaning ? 'Limpiando...' : 'Limpiar Todo'}
                  </Button>
                </Box>
                
                <List dense>
                  {generatedFiles.slice(0, 5).map((file) => (
                    <ListItem key={file.filename} divider>
                      <ListItemText
                        primary={file.filename}
                        secondary={`${(file.size / 1024).toFixed(1)} KB`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => downloadFile(file.filename)}
                          size="small"
                        >
                          <Download />
                        </IconButton>
                        <IconButton
                          edge="end"
                          onClick={() => validateGCode(file.filename)}
                          size="small"
                          disabled={isValidating}
                        >
                          {isValidating ? <CircularProgress size={16} /> : <CheckCircle />}
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Pestaña de Procesamiento de Imágenes */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
              <Image sx={{ mr: 1, verticalAlign: 'middle' }} />
              Procesar Imagen
            </Typography>
            
            <Grid container spacing={3}>
              {/* Carga de Imagen */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Cargar Imagen
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <input
                        accept="image/*"
                        style={{ display: 'none' }}
                        id="image-upload"
                        type="file"
                        onChange={handleImageUpload}
                      />
                      <label htmlFor="image-upload">
                        <Button
                          variant="outlined"
                          component="span"
                          startIcon={<Upload />}
                          fullWidth
                        >
                          Seleccionar Imagen
                        </Button>
                      </label>
                    </Box>
                    
                    {imagePreview && (
                      <Box sx={{ mb: 2 }}>
                        <img
                          src={imagePreview}
                          alt="Preview"
                          style={{
                            width: '100%',
                            maxHeight: '200px',
                            objectFit: 'contain',
                            border: '1px solid #ccc',
                            borderRadius: '4px'
                          }}
                        />
                      </Box>
                    )}
                    
                    {imageInfo && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Información de la Imagen:
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Dimensiones: {imageInfo.width} x {imageInfo.height}px<br/>
                          Formato: {imageInfo.format}<br/>
                          Tamaño: {(imageInfo.file_size / 1024).toFixed(1)} KB<br/>
                          Proporción: {imageInfo.aspect_ratio.toFixed(2)}
                        </Typography>
                      </Box>
                    )}
                    
                    <Button
                      variant="contained"
                      onClick={uploadImage}
                      disabled={!uploadedImage || isUploading}
                      startIcon={isUploading ? <CircularProgress size={16} /> : <Upload />}
                      fullWidth
                    >
                      {isUploading ? 'Subiendo...' : 'Subir Imagen'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Configuraciones Predefinidas */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Configuraciones Predefinidas
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Selecciona una configuración predefinida para diferentes tipos de grabado
                    </Typography>
                    
                    <Grid container spacing={1}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado superficial y rápido para marcas ligeras en materiales sensibles" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('superficial_rapido')}
                            sx={{ mb: 1 }}
                          >
                            🔥 Superficial Rápido
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado de calidad media para la mayoría de aplicaciones" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('calidad_media')}
                            sx={{ mb: 1 }}
                          >
                            ⚡ Calidad Media
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado profundo y detallado para máxima calidad" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('alta_calidad')}
                            sx={{ mb: 1 }}
                          >
                            💎 Alta Calidad
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado ultra rápido para producción en masa" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('ultra_rapido')}
                            sx={{ mb: 1 }}
                          >
                            🚀 Ultra Rápido
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado para madera con potencia y velocidad optimizadas" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('madera')}
                            sx={{ mb: 1 }}
                          >
                            🌳 Madera
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado para acrílico con parámetros específicos" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('acrilico')}
                            sx={{ mb: 1 }}
                          >
                            🔷 Acrílico
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado para cuero con potencia reducida" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('cuero')}
                            sx={{ mb: 1 }}
                          >
                            🐄 Cuero
                          </Button>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12} sm={6} md={3}>
                        <Tooltip title="Grabado para papel y cartón con potencia muy baja" arrow>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => applyImagePreset('papel')}
                            sx={{ mb: 1 }}
                          >
                            📄 Papel/Cartón
                          </Button>
                        </Tooltip>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Parámetros de Procesamiento */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Parámetros de Procesamiento
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Tooltip title="Desenfoque Gaussiano: Suaviza la imagen para reducir ruido. Valores más altos = más suavizado. Recomendado: 3-5 para imágenes normales, 0 para imágenes ya limpias." arrow>
                          <TextField
                            label="Desenfoque"
                            type="number"
                            value={imageProcessingParams.blur_kernel}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              blur_kernel: parseInt(e.target.value) || 3
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0, max: 15, step: 2 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Método de Umbralización: Determina cómo convertir la imagen a blanco y negro. Simple: umbral fijo (127), Otsu: automático, Adaptativo: se adapta a la imagen localmente." arrow>
                          <FormControl fullWidth size="small">
                            <InputLabel>Método de Umbral</InputLabel>
                            <Select
                              value={imageProcessingParams.threshold_method}
                              onChange={(e) => setImageProcessingParams({
                                ...imageProcessingParams,
                                threshold_method: e.target.value
                              })}
                              label="Método de Umbral"
                            >
                              <MenuItem value="otsu">Otsu</MenuItem>
                              <MenuItem value="adaptive">Adaptativo</MenuItem>
                              <MenuItem value="simple">Simple</MenuItem>
                            </Select>
                          </FormControl>
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Área Mínima: Filtra contornos pequeños (ruido). Valores más altos = menos detalles pequeños. Recomendado: 100-500 para imágenes normales, 10-50 para imágenes con muchos detalles finos." arrow>
                          <TextField
                            label="Área Mínima"
                            type="number"
                            value={imageProcessingParams.min_area}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              min_area: parseInt(e.target.value) || 100
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 10, max: 1000 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Factor de Simplificación: Reduce la complejidad de los contornos. Valores más altos = contornos más simples. Recomendado: 0.01-0.05 para preservar detalles, 0.05-0.1 para contornos más simples." arrow>
                          <TextField
                            label="Factor de Simplificación"
                            type="number"
                            step="0.01"
                            value={imageProcessingParams.simplify_factor}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              simplify_factor: parseFloat(e.target.value) || 0.02
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0.01, max: 0.1, step: 0.01 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Espaciado de Relleno: Distancia entre líneas de grabado. Valores más bajos = grabado más denso y detallado. Recomendado: 1-2 para alta calidad, 3-5 para grabado más rápido." arrow>
                          <TextField
                            label="Espaciado de Relleno (px)"
                            type="number"
                            value={imageProcessingParams.fill_spacing}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              fill_spacing: parseInt(e.target.value) || 2
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 1, max: 10, step: 1 }}
                            helperText="Menor = más denso, Mayor = más rápido"
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Potencia del Láser: Intensidad del láser para el grabado. Valores más altos = grabado más profundo. Recomendado: 25-50% para materiales sensibles, 50-75% para madera, 75-100% para materiales duros." arrow>
                          <TextField
                            label="Potencia del Láser (%)"
                            type="number"
                            value={imageProcessingParams.laser_power}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              laser_power: parseInt(e.target.value) || 100
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 1, max: 100, step: 1 }}
                            helperText="1-100% de potencia del láser"
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Velocidad de Grabado: Velocidad de movimiento del láser. Valores más bajos = mejor calidad pero más lento. Recomendado: 200-500 mm/min para grabado de calidad, 500-1000 mm/min para grabado rápido." arrow>
                          <TextField
                            label="Velocidad de Grabado (mm/min)"
                            type="number"
                            value={imageProcessingParams.feed_rate}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              feed_rate: parseInt(e.target.value) || 300
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 50, max: 2000, step: 10 }}
                            helperText="50-2000 mm/min, menor = más lento pero mejor calidad"
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Ancho de Figura: Ancho deseado de la figura en milímetros. La altura se ajustará automáticamente para mantener la relación de aspecto original de la imagen." arrow>
                          <TextField
                            label="Ancho de Figura (mm)"
                            type="number"
                            value={imageProcessingParams.figure_width}
                            onChange={(e) => setImageProcessingParams({
                              ...imageProcessingParams,
                              figure_width: parseFloat(e.target.value) || 50
                            })}
                            fullWidth
                            size="small"
                            inputProps={{ min: 1, max: 200, step: 1 }}
                            helperText="1-200 mm, mantiene proporción original"
                          />
                        </Tooltip>
                      </Grid>
                    </Grid>
                    
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        onClick={processImage}
                        disabled={!imageInfo || isProcessing}
                        startIcon={isProcessing ? <CircularProgress size={16} /> : <Visibility />}
                        fullWidth
                      >
                        {isProcessing ? 'Procesando...' : 'Procesar Imagen'}
                      </Button>
                      
                      <Button
                        variant="contained"
                        onClick={generateGCodeFromImage}
                        disabled={!imageInfo || isGenerating}
                        startIcon={isGenerating ? <CircularProgress size={16} /> : <PlayArrow />}
                        fullWidth
                      >
                        {isGenerating ? 'Generando...' : 'Generar G-code'}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Pestaña de Corte Láser */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
              <ContentCut sx={{ mr: 1, verticalAlign: 'middle' }} />
              Corte Láser - LASER TREE 10W
            </Typography>
            
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>LASER TREE 10W (10000 mW):</strong> Optimizado para cortes precisos en materiales delgados.
                <br />
                <strong>Capacidades máximas:</strong> Madera hasta 10mm, Acrílico hasta 8mm, MDF hasta 6mm
                <br />
                <strong>Recomendado:</strong> Usa los presets específicos para tu material y grosor
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              {/* Configuración de Corte Simple */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Corte Simple
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Tooltip title="Distancia del corte en milímetros. Define qué tan largo será el corte." arrow>
                          <TextField
                            label="Distancia (mm)"
                            type="number"
                            value={cutParameters.cut_distance}
                            onChange={(e) => handleCutParameterChange('cut_distance', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 1, max: 1000, step: 0.1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Profundidad del corte en milímetros. Define cuántas pasadas hará el láser." arrow>
                          <TextField
                            label="Profundidad (mm)"
                            type="number"
                            value={cutParameters.cut_depth}
                            onChange={(e) => handleCutParameterChange('cut_depth', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0.1, max: 50, step: 0.1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Ángulo del corte en grados. 0° = horizontal, 90° = vertical, 45° = diagonal." arrow>
                          <TextField
                            label="Ángulo (°)"
                            type="number"
                            value={cutParameters.cut_angle}
                            onChange={(e) => handleCutParameterChange('cut_angle', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0, max: 360, step: 1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Posición X inicial del corte en milímetros." arrow>
                          <TextField
                            label="Posición X (mm)"
                            type="number"
                            value={cutParameters.start_x}
                            onChange={(e) => handleCutParameterChange('start_x', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0, max: 1000, step: 0.1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Posición Y inicial del corte en milímetros." arrow>
                          <TextField
                            label="Posición Y (mm)"
                            type="number"
                            value={cutParameters.start_y}
                            onChange={(e) => handleCutParameterChange('start_y', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 0, max: 1000, step: 0.1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Tooltip title="Potencia del láser para el corte en porcentaje." arrow>
                          <TextField
                            label="Potencia (%)"
                            type="number"
                            value={cutParameters.cut_power}
                            onChange={(e) => handleCutParameterChange('cut_power', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 1, max: 100, step: 1 }}
                          />
                        </Tooltip>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Tooltip title="Velocidad del corte en milímetros por minuto." arrow>
                          <TextField
                            label="Velocidad (mm/min)"
                            type="number"
                            value={cutParameters.cut_speed}
                            onChange={(e) => handleCutParameterChange('cut_speed', parseFloat(e.target.value))}
                            fullWidth
                            size="small"
                            inputProps={{ min: 10, max: 2000, step: 10 }}
                          />
                        </Tooltip>
                      </Grid>
                    </Grid>
                    
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="contained"
                        onClick={generateCutGCode}
                        disabled={isGeneratingCut}
                        startIcon={isGeneratingCut ? <CircularProgress size={16} /> : <ContentCut />}
                        fullWidth
                      >
                        {isGeneratingCut ? 'Generando...' : 'Generar Corte Simple'}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Presets de Corte */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Configuraciones Predefinidas
                    </Typography>
                    
                    {Object.entries(cutPresets).map(([key, preset]) => (
                      <Box key={key} sx={{ mb: 2 }}>
                        <Button
                          variant="outlined"
                          fullWidth
                          onClick={() => applyCutPreset(key)}
                          sx={{ mb: 1 }}
                        >
                          {preset.name}
                        </Button>
                        <Typography variant="caption" color="text.secondary">
                          {preset.description}
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Múltiples Cortes */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        Múltiples Cortes
                      </Typography>
                      <Button
                        variant="outlined"
                        startIcon={<Add />}
                        onClick={addMultipleCut}
                        size="small"
                      >
                        Agregar Corte
                      </Button>
                    </Box>
                    
                    {multipleCuts.length === 0 ? (
                      <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
                        No hay cortes configurados. Haz clic en "Agregar Corte" para comenzar.
                      </Typography>
                    ) : (
                      <Grid container spacing={2}>
                        {multipleCuts.map((cut, index) => (
                          <Grid item xs={12} md={6} key={index}>
                            <Card variant="outlined">
                              <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                  <Typography variant="subtitle1">
                                    Corte {index + 1}
                                  </Typography>
                                  <IconButton
                                    size="small"
                                    onClick={() => removeMultipleCut(index)}
                                    color="error"
                                  >
                                    <Remove />
                                  </IconButton>
                                </Box>
                                
                                <Grid container spacing={1}>
                                  <Grid item xs={6}>
                                    <TextField
                                      label="Distancia"
                                      type="number"
                                      value={cut.distance}
                                      onChange={(e) => updateMultipleCut(index, 'distance', parseFloat(e.target.value))}
                                      fullWidth
                                      size="small"
                                      inputProps={{ min: 1, max: 1000, step: 0.1 }}
                                    />
                                  </Grid>
                                  <Grid item xs={6}>
                                    <TextField
                                      label="Profundidad"
                                      type="number"
                                      value={cut.depth}
                                      onChange={(e) => updateMultipleCut(index, 'depth', parseFloat(e.target.value))}
                                      fullWidth
                                      size="small"
                                      inputProps={{ min: 0.1, max: 50, step: 0.1 }}
                                    />
                                  </Grid>
                                  <Grid item xs={6}>
                                    <TextField
                                      label="Ángulo"
                                      type="number"
                                      value={cut.angle}
                                      onChange={(e) => updateMultipleCut(index, 'angle', parseFloat(e.target.value))}
                                      fullWidth
                                      size="small"
                                      inputProps={{ min: 0, max: 360, step: 1 }}
                                    />
                                  </Grid>
                                  <Grid item xs={6}>
                                    <TextField
                                      label="X Inicial"
                                      type="number"
                                      value={cut.start_x || 0}
                                      onChange={(e) => updateMultipleCut(index, 'start_x', parseFloat(e.target.value))}
                                      fullWidth
                                      size="small"
                                      inputProps={{ min: 0, max: 1000, step: 0.1 }}
                                    />
                                  </Grid>
                                  <Grid item xs={6}>
                                    <TextField
                                      label="Y Inicial"
                                      type="number"
                                      value={cut.start_y || 0}
                                      onChange={(e) => updateMultipleCut(index, 'start_y', parseFloat(e.target.value))}
                                      fullWidth
                                      size="small"
                                      inputProps={{ min: 0, max: 1000, step: 0.1 }}
                                    />
                                  </Grid>
                                </Grid>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>
                    )}
                    
                    {multipleCuts.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Button
                          variant="contained"
                          onClick={generateMultipleCutsGCode}
                          disabled={isGeneratingCut}
                          startIcon={isGeneratingCut ? <CircularProgress size={16} /> : <ContentCut />}
                          fullWidth
                        >
                          {isGeneratingCut ? 'Generando...' : `Generar ${multipleCuts.length} Cortes`}
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Pestaña de Vista Previa 3D */}
        {activeTab === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
              <ViewInAr sx={{ mr: 1, verticalAlign: 'middle' }} />
              Vista Previa 3D
            </Typography>
            <GCodePreview3D
              gcodeData={generatedGCode}
              tableWidth={parameters.table_width}
              tableHeight={parameters.table_height}
              numLayers={parameters.num_layers}
              lineHeight={parameters.line_height}
            />
          </Box>
        )}

        {/* Pestaña de G-code */}
        {activeTab === 4 && (
          <Box>
            <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
              <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
              Código G Generado
            </Typography>
            <Paper sx={{ p: 2, maxHeight: '600px', overflow: 'auto' }}>
              <pre style={{ 
                fontFamily: 'monospace', 
                fontSize: '12px', 
                lineHeight: '1.4',
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {generatedGCode || 'No hay G-code generado'}
              </pre>
            </Paper>
          </Box>
        )}

        {/* Resultado de Validación */}
        {validationResult && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resultado de Validación
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {validationResult.is_valid ? (
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                ) : (
                  <Error color="error" sx={{ mr: 1 }} />
                )}
                <Typography variant="h6" color={validationResult.is_valid ? 'success.main' : 'error.main'}>
                  {validationResult.is_valid ? 'VÁLIDO' : 'INVÁLIDO'}
                </Typography>
              </Box>

              {validationResult.errors && validationResult.errors.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="error" gutterBottom>
                    Errores encontrados:
                  </Typography>
                  {validationResult.errors.map((error: string, index: number) => (
                    <Chip key={index} label={error} color="error" size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              )}

              {validationResult.warnings && validationResult.warnings.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="warning.main" gutterBottom>
                    Advertencias:
                  </Typography>
                  {validationResult.warnings.map((warning: string, index: number) => (
                    <Chip key={index} label={warning} color="warning" size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        )}
      </Paper>
    </Container>
  );
};

export default App;