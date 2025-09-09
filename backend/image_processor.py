#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de Imágenes para Vectorización
Convierte imágenes en contornos vectoriales para G-code
"""

import cv2
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt
import os
from typing import List, Tuple, Optional
import tempfile

class ImageProcessor:
    """Procesador de imágenes para vectorización"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Cargar imagen desde archivo"""
        try:
            # Cargar imagen con OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Convertir de BGR a RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            raise ValueError(f"Error al cargar la imagen: {str(e)}")
    
    def preprocess_image(self, image: np.ndarray, 
                        blur_kernel: int = 3,
                        threshold_method: str = 'otsu') -> np.ndarray:
        """Preprocesar imagen para vectorización"""
        try:
            # Convertir a escala de grises
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()
            
            # Aplicar desenfoque gaussiano para suavizar
            if blur_kernel > 0:
                gray = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
            
            # Aplicar umbralización invertida para detectar figuras negras sobre fondo claro
            if threshold_method == 'otsu':
                # Usar Otsu invertido para detectar figuras negras
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            elif threshold_method == 'adaptive':
                # Usar adaptive invertido para detectar figuras negras
                binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            else:
                # Umbralización simple invertida (figuras negras sobre fondo claro)
                # Si el píxel es más oscuro que 127, es figura (255), si no es fondo (0)
                _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Asegurar que binary sea uint8
            if binary.dtype != np.uint8:
                binary = binary.astype(np.uint8)
            
            # Operaciones morfológicas para limpiar
            kernel = np.ones((3, 3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            return binary
            
        except Exception as e:
            raise ValueError(f"Error en preprocesamiento: {str(e)}")
    
    def find_contours(self, binary_image: np.ndarray, 
                     min_area: int = 100,
                     simplify_factor: float = 0.02,
                     fill_spacing: int = 2) -> List[np.ndarray]:
        """Encontrar contornos en imagen binaria con patrón de relleno para grabado láser"""
        try:
            # Operaciones morfológicas suaves para preservar forma
            kernel_size = max(2, int(simplify_factor * 50))  # Kernel más conservador
            if kernel_size > 1:
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                # Solo cerrar huecos pequeños, sin dilatar/erosionar agresivamente
                binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
                # Abrir ligeramente para eliminar ruido
                binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                binary_image, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtrar contornos por área mínima
            filtered_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= min_area:
                    # Simplificación más conservadora para preservar forma
                    epsilon = simplify_factor * cv2.arcLength(contour, True)
                    simplified = cv2.approxPolyDP(contour, epsilon, True)
                    filtered_contours.append(simplified)
            
            # Ordenar contornos por área (más grande primero)
            filtered_contours.sort(key=cv2.contourArea, reverse=True)
            
            # Generar patrón de relleno para grabado láser
            fill_pattern = self._generate_fill_pattern(binary_image, filtered_contours, fill_spacing)
            
            return fill_pattern
            
        except Exception as e:
            raise ValueError(f"Error al encontrar contornos: {str(e)}")

    def _generate_fill_pattern(self, binary_image: np.ndarray, contours: List[np.ndarray], fill_spacing: int = 2) -> List[np.ndarray]:
        """Generar patrón de relleno para grabado láser completo - imprimir exactamente donde está el negro"""
        try:
            # Crear máscara de la figura
            mask = np.zeros(binary_image.shape, dtype=np.uint8)
            cv2.fillPoly(mask, contours, 255)
            
            # Generar líneas de relleno para imprimir exactamente la figura negra
            fill_lines = []
            
            # Usar el espaciado especificado por el usuario (sin optimización agresiva)
            spacing = max(1, fill_spacing)  # Mínimo 1px para preservar detalles
            
            # Líneas horizontales - imprimir donde está el negro
            for y in range(0, binary_image.shape[0], spacing):
                line = binary_image[y, :]
                intersections = []
                
                # Encontrar todos los píxeles negros (figura) en esta línea
                for x in range(len(line)):
                    if line[x] == 255:  # Píxel negro (figura)
                        intersections.append(x)
                
                # Crear líneas de relleno continuas
                if len(intersections) > 0:
                    # Agrupar píxeles consecutivos en segmentos
                    segments = []
                    current_segment = [intersections[0]]
                    
                    for i in range(1, len(intersections)):
                        if intersections[i] == intersections[i-1] + 1:
                            # Píxel consecutivo, agregar al segmento actual
                            current_segment.append(intersections[i])
                        else:
                            # Píxel no consecutivo, finalizar segmento actual
                            if len(current_segment) > 1:
                                segments.append(current_segment)
                            current_segment = [intersections[i]]
                    
                    # Agregar el último segmento
                    if len(current_segment) > 1:
                        segments.append(current_segment)
                    
                    # Crear líneas de relleno para cada segmento
                    for segment in segments:
                        if len(segment) > 1:
                            fill_line = []
                            for x in segment:
                                fill_line.append([x, y])
                            fill_lines.append(np.array(fill_line, dtype=np.float32))
            
            # Líneas verticales para detalles finos (solo si fill_spacing es muy pequeño)
            if fill_spacing <= 1:  # Solo para espaciados muy densos
                for x in range(0, binary_image.shape[1], spacing):
                    line = binary_image[:, x]
                    intersections = []
                    
                    for y in range(len(line)):
                        if line[y] == 255:  # Píxel negro (figura)
                            intersections.append(y)
                    
                    # Crear líneas de relleno continuas
                    if len(intersections) > 0:
                        # Agrupar píxeles consecutivos en segmentos
                        segments = []
                        current_segment = [intersections[0]]
                        
                        for i in range(1, len(intersections)):
                            if intersections[i] == intersections[i-1] + 1:
                                # Píxel consecutivo, agregar al segmento actual
                                current_segment.append(intersections[i])
                            else:
                                # Píxel no consecutivo, finalizar segmento actual
                                if len(current_segment) > 1:
                                    segments.append(current_segment)
                                current_segment = [intersections[i]]
                        
                        # Agregar el último segmento
                        if len(current_segment) > 1:
                            segments.append(current_segment)
                        
                        # Crear líneas de relleno para cada segmento
                        for segment in segments:
                            if len(segment) > 1:
                                fill_line = []
                                for y in segment:
                                    fill_line.append([x, y])
                                fill_lines.append(np.array(fill_line, dtype=np.float32))
            
            return fill_lines
            
        except Exception as e:
            raise ValueError(f"Error al generar patrón de relleno: {str(e)}")
    
    def contours_to_points(self, contours: List[np.ndarray]) -> List[Tuple[float, float]]:
        """Convertir contornos a puntos para G-code"""
        points = []
        
        for contour in contours:
            # Convertir contorno a puntos
            contour_points = []
            
            # Verificar si es un array de líneas de relleno (nuevo formato)
            if len(contour.shape) == 2 and contour.shape[1] == 2:
                # Es un array de puntos directos [x, y]
                for point in contour:
                    x, y = point[0], point[1]
                    contour_points.append((float(x), float(y)))
            else:
                # Es un contorno tradicional [[x, y]]
                for point in contour:
                    x, y = point[0]
                    contour_points.append((float(x), float(y)))
            
            # Para líneas de relleno, no cerrar el contorno
            if len(contour_points) > 2 and len(contour.shape) != 2:
                # Solo cerrar contornos tradicionales
                if contour_points[0] != contour_points[-1]:
                    contour_points.append(contour_points[0])
            
            points.extend(contour_points)
            
            # Agregar punto de salto (laser off) entre líneas
            if points:
                points.append((float('nan'), float('nan')))
        
        return points
    
    def scale_contours(self, points: List[Tuple[float, float]], 
                      target_width: float, target_height: float) -> List[Tuple[float, float]]:
        """Escalar contornos al tamaño objetivo"""
        if not points:
            return points
        
        # Filtrar puntos válidos (no NaN)
        valid_points = [(x, y) for x, y in points if not (np.isnan(x) or np.isnan(y))]
        
        if not valid_points:
            return points
        
        # Calcular dimensiones actuales
        min_x = min(x for x, y in valid_points)
        max_x = max(x for x, y in valid_points)
        min_y = min(y for x, y in valid_points)
        max_y = max(y for x, y in valid_points)
        
        current_width = max_x - min_x
        current_height = max_y - min_y
        
        if current_width == 0 or current_height == 0:
            return points
        
        # Calcular factor de escala
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        scale = min(scale_x, scale_y)  # Mantener proporción
        
        # Escalar puntos
        scaled_points = []
        for x, y in points:
            if np.isnan(x) or np.isnan(y):
                scaled_points.append((x, y))  # Mantener puntos de salto
            else:
                scaled_x = (x - min_x) * scale
                # Invertir coordenada Y para corregir orientación
                scaled_y = target_height - ((y - min_y) * scale)
                scaled_points.append((scaled_x, scaled_y))
        
        return scaled_points
    
    def process_image_to_contours(self, image_path: str, 
                                 target_width: float = 50.0,
                                 target_height: float = 50.0,
                                 blur_kernel: int = 3,
                                 threshold_method: str = 'otsu',
                                 min_area: int = 100,
                                 simplify_factor: float = 0.01,
                                 fill_spacing: int = 2,
                                 figure_width: float = None) -> List[Tuple[float, float]]:
        """Procesar imagen completa y convertir a contornos"""
        try:
            # Cargar imagen
            image = self.load_image(image_path)
            
            # Calcular dimensiones basándose en figure_width si se proporciona
            if figure_width is not None:
                # Obtener dimensiones originales de la imagen
                original_height, original_width = image.shape[:2]
                aspect_ratio = original_width / original_height
                
                # Calcular altura basándose en el ancho deseado y la relación de aspecto
                calculated_height = figure_width / aspect_ratio
                
                # Usar las dimensiones calculadas
                final_width = figure_width
                final_height = calculated_height
            else:
                # Usar las dimensiones proporcionadas
                final_width = target_width
                final_height = target_height
            
            # Preprocesar
            binary = self.preprocess_image(image, blur_kernel, threshold_method)
            
            # Encontrar contornos
            contours = self.find_contours(binary, min_area, simplify_factor, fill_spacing)
            
            # Convertir a puntos
            points = self.contours_to_points(contours)
            
            # Escalar al tamaño objetivo
            scaled_points = self.scale_contours(points, final_width, final_height)
            
            return scaled_points
            
        except Exception as e:
            raise ValueError(f"Error en procesamiento de imagen: {str(e)}")
    
    def save_preview(self, image_path: str, output_path: str,
                    blur_kernel: int = 3,
                    threshold_method: str = 'otsu',
                    min_area: int = 100) -> str:
        """Guardar vista previa del procesamiento"""
        try:
            # Cargar y procesar imagen
            image = self.load_image(image_path)
            binary = self.preprocess_image(image, blur_kernel, threshold_method)
            contours = self.find_contours(binary, min_area)
            
            # Crear figura con subplots
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Imagen original
            axes[0].imshow(image)
            axes[0].set_title('Imagen Original')
            axes[0].axis('off')
            
            # Imagen binaria
            axes[1].imshow(binary, cmap='gray')
            axes[1].set_title('Imagen Binaria')
            axes[1].axis('off')
            
            # Contornos detectados
            axes[2].imshow(image)
            for contour in contours:
                contour_points = contour.reshape(-1, 2)
                axes[2].plot(contour_points[:, 0], contour_points[:, 1], 'r-', linewidth=2)
            axes[2].set_title(f'Contornos Detectados ({len(contours)})')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)  # Cerrar figura específica
            plt.clf()  # Limpiar figura actual
            plt.cla()  # Limpiar ejes actuales
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error al guardar vista previa: {str(e)}")
    
    def get_image_info(self, image_path: str) -> dict:
        """Obtener información de la imagen"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
                # Calcular tamaño del archivo
                file_size = os.path.getsize(image_path)
                
                return {
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'file_size': file_size,
                    'aspect_ratio': width / height if height > 0 else 1.0
                }
                
        except Exception as e:
            raise ValueError(f"Error al obtener información de imagen: {str(e)}")
