#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laser G-code Generator API
Backend Flask para generación de G-code para láser
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import json
import numpy as np
from datetime import datetime
from gcode_generator import LaserGCodeGenerator
from image_processor import ImageProcessor
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Configuración
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
PREVIEW_FOLDER = 'previews'
ALLOWED_EXTENSIONS = {'txt', 'gcode'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PREVIEW_FOLDER, exist_ok=True)

# Inicializar procesador de imágenes
image_processor = ImageProcessor()

def allowed_image_file(filename):
    """Verificar si el archivo es una imagen válida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def save_uploaded_file(file, folder):
    """Guardar archivo subido de forma segura"""
    if file and allowed_image_file(file.filename):
        filename = secure_filename(file.filename)
        # Agregar timestamp para evitar conflictos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filepath
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar estado del API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/generate', methods=['POST'])
def generate_gcode():
    """Generar G-code basado en parámetros"""
    try:
        data = request.get_json()
        
        # Validar parámetros requeridos
        required_params = ['text', 'table_width', 'table_height', 'font_size']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Parámetro requerido faltante: {param}'}), 400
        
        # Crear generador con parámetros
        generator = LaserGCodeGenerator(
            table_width=float(data['table_width']),
            table_height=float(data['table_height']),
            font_size=float(data['font_size']),
            line_height=float(data.get('line_height', 0.7)),
            feed_rate=float(data.get('feed_rate', 60.0)),
            font_name=data.get('font_name', 'Arial'),
            laser_power_max=float(data.get('laser_power_max', 100.0)),
            num_layers=int(data.get('num_layers', 30)),
            focus_height=float(data.get('focus_height', 0.0))
        )
        
        # Generar G-code
        gcode_lines = generator.generate_gcode(
            text=data['text'],
            center_text=data.get('center_text', False)
        )
        
        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"laser_output_{timestamp}.gcode"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        generator.save_gcode(gcode_lines, filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_lines': len(gcode_lines),
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Descargar archivo G-code generado"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_gcode():
    """Validar G-code para seguridad del eje Z"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Nombre de archivo requerido'}), 400
        
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Importar validador
        from validate_z_axis import ZAxisValidator
        
        validator = ZAxisValidator(filepath)
        is_valid, errors, warnings = validator.validate()
        
        return jsonify({
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Obtener configuraciones predefinidas para LASER TREE 10W"""
    presets = {
        'wood_soft_3mm': {
            'name': 'Madera Blanda 3mm',
            'description': 'Pino, balsa 3mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 80.0,
                'num_layers': 3,
                'feed_rate': 150.0,
                'line_height': 0.8,
                'focus_height': 0.0
            }
        },
        'wood_soft_6mm': {
            'name': 'Madera Blanda 6mm',
            'description': 'Pino, balsa 6mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 90.0,
                'num_layers': 5,
                'feed_rate': 100.0,
                'line_height': 0.7,
                'focus_height': 0.0
            }
        },
        'wood_hard_3mm': {
            'name': 'Madera Dura 3mm',
            'description': 'Roble, haya 3mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 85.0,
                'num_layers': 4,
                'feed_rate': 120.0,
                'line_height': 0.6,
                'focus_height': 0.0
            }
        },
        'wood_hard_6mm': {
            'name': 'Madera Dura 6mm',
            'description': 'Roble, haya 6mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 95.0,
                'num_layers': 6,
                'feed_rate': 80.0,
                'line_height': 0.5,
                'focus_height': 0.0
            }
        },
        'acrylic_3mm': {
            'name': 'Acrílico 3mm',
            'description': 'Grabado en acrílico 3mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 70.0,
                'num_layers': 2,
                'feed_rate': 200.0,
                'line_height': 0.3,
                'focus_height': 0.0
            }
        },
        'acrylic_5mm': {
            'name': 'Acrílico 5mm',
            'description': 'Grabado en acrílico 5mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 80.0,
                'num_layers': 3,
                'feed_rate': 150.0,
                'line_height': 0.4,
                'focus_height': 0.0
            }
        },
        'mdf_3mm': {
            'name': 'MDF 3mm',
            'description': 'Grabado en MDF 3mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 75.0,
                'num_layers': 3,
                'feed_rate': 180.0,
                'line_height': 0.5,
                'focus_height': 0.0
            }
        },
        'mdf_6mm': {
            'name': 'MDF 6mm',
            'description': 'Grabado en MDF 6mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 85.0,
                'num_layers': 4,
                'feed_rate': 120.0,
                'line_height': 0.6,
                'focus_height': 0.0
            }
        },
        'plywood_3mm': {
            'name': 'Contrachapado 3mm',
            'description': 'Grabado en contrachapado 3mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 80.0,
                'num_layers': 3,
                'feed_rate': 150.0,
                'line_height': 0.5,
                'focus_height': 0.0
            }
        },
        'plywood_6mm': {
            'name': 'Contrachapado 6mm',
            'description': 'Grabado en contrachapado 6mm - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 90.0,
                'num_layers': 4,
                'feed_rate': 100.0,
                'line_height': 0.6,
                'focus_height': 0.0
            }
        },
        'engraving_light': {
            'name': 'Grabado Ligero',
            'description': 'Grabado superficial - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 30.0,
                'num_layers': 1,
                'feed_rate': 400.0,
                'line_height': 0.2,
                'focus_height': 0.0
            }
        },
        'engraving_medium': {
            'name': 'Grabado Medio',
            'description': 'Grabado de profundidad media - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 50.0,
                'num_layers': 2,
                'feed_rate': 250.0,
                'line_height': 0.3,
                'focus_height': 0.0
            }
        },
        'engraving_deep': {
            'name': 'Grabado Profundo',
            'description': 'Grabado profundo - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 70.0,
                'num_layers': 3,
                'feed_rate': 150.0,
                'line_height': 0.4,
                'focus_height': 0.0
            }
        },
        'leather': {
            'name': 'Cuero',
            'description': 'Grabado en cuero - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 40.0,
                'num_layers': 1,
                'feed_rate': 300.0,
                'line_height': 0.3,
                'focus_height': 0.0
            }
        },
        'cardboard': {
            'name': 'Cartón',
            'description': 'Grabado en cartón - LASER TREE 10W',
            'parameters': {
                'laser_power_max': 25.0,
                'num_layers': 1,
                'feed_rate': 500.0,
                'line_height': 0.2,
                'focus_height': 0.0
            }
        }
    }
    
    return jsonify(presets)

@app.route('/api/files', methods=['GET'])
def list_files():
    """Listar archivos G-code generados"""
    try:
        files = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.gcode'):
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'download_url': f'/api/download/{filename}'
                })
        
        # Ordenar por fecha de creación (más reciente primero)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """Limpiar archivos G-code generados"""
    try:
        deleted_files = []
        deleted_count = 0
        total_size = 0
        
        # Limpiar archivos en el directorio de salida
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.gcode'):
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                try:
                    # Obtener información del archivo antes de eliminarlo
                    stat = os.stat(filepath)
                    file_size = stat.st_size
                    created = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    
                    # Eliminar el archivo
                    os.remove(filepath)
                    
                    deleted_files.append({
                        'filename': filename,
                        'size': file_size,
                        'created': created
                    })
                    deleted_count += 1
                    total_size += file_size
                    
                except Exception as e:
                    print(f"Error eliminando archivo {filename}: {e}")
                    continue
        
        return jsonify({
            'success': True,
            'message': f'Se eliminaron {deleted_count} archivos',
            'deleted_count': deleted_count,
            'total_size_freed': total_size,
            'deleted_files': deleted_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Subir imagen para procesamiento"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró archivo de imagen'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if not allowed_image_file(file.filename):
            return jsonify({'error': 'Formato de archivo no soportado'}), 400
        
        # Verificar tamaño del archivo
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'Archivo demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Guardar archivo
        filepath = save_uploaded_file(file, UPLOAD_FOLDER)
        if not filepath:
            return jsonify({'error': 'Error al guardar archivo'}), 500
        
        # Obtener información de la imagen
        image_info = image_processor.get_image_info(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Imagen subida correctamente',
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'image_info': image_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-image', methods=['POST'])
def process_image():
    """Procesar imagen y generar vista previa"""
    try:
        data = request.get_json()
        
        # Validar parámetros requeridos
        required_params = ['filepath', 'table_width', 'table_height']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Parámetro requerido faltante: {param}'}), 400
        
        filepath = data['filepath']
        table_width = float(data['table_width'])
        table_height = float(data['table_height'])
        
        # Parámetros opcionales
        blur_kernel = int(data.get('blur_kernel', 3))
        threshold_method = data.get('threshold_method', 'simple')
        min_area = int(data.get('min_area', 100))
        simplify_factor = float(data.get('simplify_factor', 0.02))
        fill_spacing = int(data.get('fill_spacing', 2))
        figure_width = float(data.get('figure_width', 50))
        
        # Verificar que el archivo existe
        if not os.path.exists(filepath):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Generar nombre para vista previa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_filename = f"preview_{timestamp}.png"
        preview_path = os.path.join(PREVIEW_FOLDER, preview_filename)
        
        # Procesar imagen y generar vista previa
        image_processor.save_preview(
            filepath, 
            preview_path,
            blur_kernel=blur_kernel,
            threshold_method=threshold_method,
            min_area=min_area
        )
        
        # Procesar imagen para obtener contornos
        contours = image_processor.process_image_to_contours(
            filepath,
            target_width=table_width,
            target_height=table_height,
            blur_kernel=blur_kernel,
            threshold_method=threshold_method,
            min_area=min_area,
            simplify_factor=simplify_factor,
            fill_spacing=fill_spacing,
            figure_width=figure_width
        )
        
        # Filtrar valores NaN para JSON
        valid_contours = []
        for point in contours:
            if not (np.isnan(point[0]) or np.isnan(point[1])):
                valid_contours.append([float(point[0]), float(point[1])])
        
        return jsonify({
            'success': True,
            'message': 'Imagen procesada correctamente',
            'preview_url': f'/api/preview/{preview_filename}',
            'contours_count': len(valid_contours),
            'contours': valid_contours
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-from-image', methods=['POST'])
def generate_gcode_from_image():
    """Generar G-code desde imagen procesada"""
    try:
        data = request.get_json()
        
        # Validar parámetros requeridos
        required_params = ['filepath', 'table_width', 'table_height', 'font_size']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Parámetro requerido faltante: {param}'}), 400
        
        filepath = data['filepath']
        table_width = float(data['table_width'])
        table_height = float(data['table_height'])
        font_size = float(data['font_size'])
        
        # Parámetros de procesamiento de imagen
        blur_kernel = int(data.get('blur_kernel', 3))
        threshold_method = data.get('threshold_method', 'simple')
        min_area = int(data.get('min_area', 100))
        simplify_factor = float(data.get('simplify_factor', 0.02))
        fill_spacing = int(data.get('fill_spacing', 2))
        laser_power = float(data.get('laser_power', 100.0))
        feed_rate = float(data.get('feed_rate', 300.0))
        figure_width = float(data.get('figure_width', 50))
        
        # Parámetros de láser
        laser_power_max = float(data.get('laser_power_max', 100.0))
        num_layers = int(data.get('num_layers', 1))
        line_height = float(data.get('line_height', 0.7))
        focus_height = float(data.get('focus_height', 0.0))
        
        # Verificar que el archivo existe
        if not os.path.exists(filepath):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Procesar imagen para obtener contornos
        contours = image_processor.process_image_to_contours(
            filepath,
            target_width=table_width,
            target_height=table_height,
            blur_kernel=blur_kernel,
            threshold_method=threshold_method,
            min_area=min_area,
            simplify_factor=simplify_factor,
            fill_spacing=fill_spacing,
            figure_width=figure_width
        )
        
        # Crear generador de G-code
        generator = LaserGCodeGenerator(
            table_width=table_width,
            table_height=table_height,
            font_size=font_size,
            laser_power_max=laser_power,  # Usar potencia específica de la imagen
            num_layers=num_layers,
            feed_rate=feed_rate,  # Usar velocidad específica de la imagen
            line_height=line_height,
            focus_height=focus_height
        )
        
        # Generar G-code desde contornos
        gcode = generator.generate_gcode_from_contours(contours)
        
        # Guardar archivo G-code
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_laser_output_{timestamp}.gcode"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(gcode)
        
        return jsonify({
            'success': True,
            'message': 'G-code generado correctamente desde imagen',
            'filename': filename,
            'download_url': f'/api/download/{filename}',
            'gcode': gcode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/<filename>')
def get_preview(filename):
    """Obtener vista previa de imagen procesada"""
    try:
        filepath = os.path.join(PREVIEW_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/png')
        else:
            return jsonify({'error': 'Vista previa no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-cut', methods=['POST'])
def generate_cut_gcode():
    """Generar G-code para corte láser"""
    try:
        data = request.get_json()
        
        # Validar parámetros requeridos
        required_params = ['cut_distance', 'cut_depth', 'cut_angle', 'table_width', 'table_height']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Parámetro requerido faltante: {param}'}), 400
        
        # Crear generador con parámetros básicos
        generator = LaserGCodeGenerator(
            table_width=float(data['table_width']),
            table_height=float(data['table_height']),
            font_size=8.0,  # No relevante para cortes
            line_height=0.7,  # No relevante para cortes
            feed_rate=float(data.get('cut_speed', 60.0)),
            font_name='Arial',  # No relevante para cortes
            laser_power_max=float(data.get('cut_power', 100.0)),
            num_layers=1,  # No relevante para cortes
            focus_height=float(data.get('focus_height', 0.0))
        )
        
        # Parámetros del corte
        cut_distance = float(data['cut_distance'])
        cut_depth = float(data['cut_depth'])
        cut_angle = float(data['cut_angle'])
        start_x = float(data.get('start_x', 0.0))
        start_y = float(data.get('start_y', 0.0))
        cut_power = float(data.get('cut_power', 100.0))
        cut_speed = float(data.get('cut_speed', 60.0))
        
        # Generar G-code para el corte
        gcode_lines = generator.generate_cut_gcode(
            cut_distance=cut_distance,
            cut_depth=cut_depth,
            cut_angle=cut_angle,
            start_x=start_x,
            start_y=start_y,
            cut_power=cut_power,
            cut_speed=cut_speed
        )
        
        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"laser_cut_{timestamp}.gcode"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        generator.save_gcode(gcode_lines, filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_lines': len(gcode_lines),
            'download_url': f'/api/download/{filename}',
            'cut_info': {
                'distance': cut_distance,
                'depth': cut_depth,
                'angle': cut_angle,
                'start_position': [start_x, start_y],
                'power': cut_power,
                'speed': cut_speed
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-multiple-cuts', methods=['POST'])
def generate_multiple_cuts_gcode():
    """Generar G-code para múltiples cortes láser"""
    try:
        data = request.get_json()
        
        # Validar parámetros requeridos
        required_params = ['cuts', 'table_width', 'table_height']
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Parámetro requerido faltante: {param}'}), 400
        
        cuts = data['cuts']
        if not isinstance(cuts, list) or len(cuts) == 0:
            return jsonify({'error': 'La lista de cortes no puede estar vacía'}), 400
        
        # Validar cada corte
        for i, cut in enumerate(cuts):
            required_cut_params = ['distance', 'depth', 'angle']
            for param in required_cut_params:
                if param not in cut:
                    return jsonify({'error': f'Corte {i+1}: parámetro requerido faltante: {param}'}), 400
        
        # Crear generador con parámetros básicos
        generator = LaserGCodeGenerator(
            table_width=float(data['table_width']),
            table_height=float(data['table_height']),
            font_size=8.0,  # No relevante para cortes
            line_height=0.7,  # No relevante para cortes
            feed_rate=float(data.get('cut_speed', 60.0)),
            font_name='Arial',  # No relevante para cortes
            laser_power_max=float(data.get('cut_power', 100.0)),
            num_layers=1,  # No relevante para cortes
            focus_height=float(data.get('focus_height', 0.0))
        )
        
        # Parámetros globales
        cut_power = float(data.get('cut_power', 100.0))
        cut_speed = float(data.get('cut_speed', 60.0))
        
        # Generar G-code para múltiples cortes
        gcode_lines = generator.generate_multiple_cuts_gcode(
            cuts=cuts,
            cut_power=cut_power,
            cut_speed=cut_speed
        )
        
        # Guardar archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"laser_multiple_cuts_{timestamp}.gcode"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        generator.save_gcode(gcode_lines, filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'total_lines': len(gcode_lines),
            'download_url': f'/api/download/{filename}',
            'cuts_count': len(cuts),
            'cut_power': cut_power,
            'cut_speed': cut_speed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cut-presets', methods=['GET'])
def get_cut_presets():
    """Obtener configuraciones predefinidas para corte láser LASER TREE 10W"""
    presets = {
        'wood_thin_3mm': {
            'name': 'Madera Delgada (3mm)',
            'description': 'Corte para madera de 3mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 85.0,
                'cut_speed': 120.0,
                'cut_depth': 2.0
            }
        },
        'wood_medium_6mm': {
            'name': 'Madera Media (6mm)',
            'description': 'Corte para madera de 6mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 95.0,
                'cut_speed': 60.0,
                'cut_depth': 4.0
            }
        },
        'wood_thick_10mm': {
            'name': 'Madera Gruesa (10mm)',
            'description': 'Corte para madera de 10mm - LASER TREE 10W (máximo recomendado)',
            'parameters': {
                'cut_power': 100.0,
                'cut_speed': 30.0,
                'cut_depth': 6.0
            }
        },
        'acrylic_thin_3mm': {
            'name': 'Acrílico Delgado (3mm)',
            'description': 'Corte para acrílico de 3mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 80.0,
                'cut_speed': 100.0,
                'cut_depth': 2.0
            }
        },
        'acrylic_medium_5mm': {
            'name': 'Acrílico Medio (5mm)',
            'description': 'Corte para acrílico de 5mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 90.0,
                'cut_speed': 50.0,
                'cut_depth': 3.0
            }
        },
        'acrylic_thick_8mm': {
            'name': 'Acrílico Grueso (8mm)',
            'description': 'Corte para acrílico de 8mm - LASER TREE 10W (máximo recomendado)',
            'parameters': {
                'cut_power': 100.0,
                'cut_speed': 25.0,
                'cut_depth': 4.0
            }
        },
        'cardboard': {
            'name': 'Cartón (2-5mm)',
            'description': 'Corte rápido para cartón - LASER TREE 10W',
            'parameters': {
                'cut_power': 40.0,
                'cut_speed': 300.0,
                'cut_depth': 1.0
            }
        },
        'leather': {
            'name': 'Cuero (1-3mm)',
            'description': 'Corte para cuero - LASER TREE 10W',
            'parameters': {
                'cut_power': 50.0,
                'cut_speed': 200.0,
                'cut_depth': 1.0
            }
        },
        'fabric': {
            'name': 'Tela (1-2mm)',
            'description': 'Corte para tela - LASER TREE 10W',
            'parameters': {
                'cut_power': 30.0,
                'cut_speed': 400.0,
                'cut_depth': 1.0
            }
        },
        'mdf_3mm': {
            'name': 'MDF (3mm)',
            'description': 'Corte para MDF de 3mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 75.0,
                'cut_speed': 150.0,
                'cut_depth': 2.0
            }
        },
        'mdf_6mm': {
            'name': 'MDF (6mm)',
            'description': 'Corte para MDF de 6mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 90.0,
                'cut_speed': 80.0,
                'cut_depth': 3.0
            }
        },
        'plywood_3mm': {
            'name': 'Contrachapado (3mm)',
            'description': 'Corte para contrachapado de 3mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 80.0,
                'cut_speed': 120.0,
                'cut_depth': 2.0
            }
        },
        'plywood_6mm': {
            'name': 'Contrachapado (6mm)',
            'description': 'Corte para contrachapado de 6mm - LASER TREE 10W',
            'parameters': {
                'cut_power': 95.0,
                'cut_speed': 60.0,
                'cut_depth': 3.0
            }
        },
        'balsa_wood': {
            'name': 'Madera Balsa (3-6mm)',
            'description': 'Corte para madera balsa - LASER TREE 10W',
            'parameters': {
                'cut_power': 60.0,
                'cut_speed': 200.0,
                'cut_depth': 2.0
            }
        },
        'paper': {
            'name': 'Papel (0.1-0.5mm)',
            'description': 'Corte para papel - LASER TREE 10W',
            'parameters': {
                'cut_power': 20.0,
                'cut_speed': 500.0,
                'cut_depth': 1.0
            }
        }
    }
    
    return jsonify(presets)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
