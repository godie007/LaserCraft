#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de G-code para láser - Versión Backend
Migrado desde la versión CLI original
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
from scipy import ndimage
from typing import List, Tuple, Optional
import tempfile

class LaserGCodeGenerator:
    """Generador profesional de G-code para láser"""
    
    # Rango de potencia del controlador láser (0-1000 es común en GRBL y controladores modernos)
    LASER_POWER_MAX_VALUE = 1000  # Valor máximo del comando M3 S (100% = 1000)
    
    def __init__(self, table_width: float = 50.0, table_height: float = 50.0, 
                 font_size: float = 8.0, line_height: float = 0.7, 
                 feed_rate: float = 60.0, font_name: str = "Arial", 
                 laser_power_max: float = 100.0, num_layers: int = 30, 
                 focus_height: float = 0.0):
        """
        Inicializar generador de G-code
        
        Args:
            table_width: Ancho de la tabla en mm
            table_height: Alto de la tabla en mm
            font_size: Tamaño de fuente en mm
            line_height: Altura de línea en mm
            feed_rate: Velocidad de alimentación en mm/min
            font_name: Nombre de la fuente
            laser_power_max: Potencia máxima del láser (%)
            num_layers: Número de capas/pasadas
            focus_height: Altura de enfoque en mm
        """
        self.table_width = table_width
        self.table_height = table_height
        self.font_size = font_size
        self.line_height = line_height
        self.feed_rate = feed_rate
        self.font_name = font_name
        self.laser_power_max = laser_power_max
        self.num_layers = num_layers
        self.focus_height = focus_height
    
    def _convert_power_percent_to_value(self, power_percent: float) -> int:
        """
        Convertir porcentaje de potencia (0-100) al valor del comando M3 S (0-1000)
        
        Args:
            power_percent: Potencia en porcentaje (0-100)
            
        Returns:
            Valor para el comando M3 S (0-1000)
        """
        # Asegurar que el porcentaje esté en el rango 0-100
        power_percent = max(0.0, min(100.0, power_percent))
        
        # Convertir a valor del controlador (100% = 1000)
        power_value = int((power_percent / 100.0) * self.LASER_POWER_MAX_VALUE)
        
        return power_value
    
    def _get_text_contours_pil(self, text: str) -> List[np.ndarray]:
        """
        Extraer contornos del texto usando PIL y OpenCV (método mejorado)
        
        Args:
            text: Texto a procesar
            
        Returns:
            Lista de contornos
        """
        # Crear imagen temporal más grande para mejor resolución
        img_size = (1600, 400)  # Imagen más grande
        img = Image.new('L', img_size, 0)  # Imagen en escala de grises
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar fuente del sistema con tamaño más grande
        font_size = 200  # Fuente más grande
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        
        # Dibujar texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Centrar texto
        x = (img_size[0] - text_width) // 2
        y = (img_size[1] - text_height) // 2
        
        draw.text((x, y), text, font=font, fill=255)
        
        # Convertir a array numpy
        img_array = np.array(img)
        
        # Encontrar contornos - incluir tanto externos como internos
        contours, hierarchy = cv2.findContours(img_array, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos muy pequeños - reducir el área mínima
        min_area = 50  # Área mínima más pequeña para capturar más detalles
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        return valid_contours
    
    def _get_text_contours_alternative(self, text: str) -> List[np.ndarray]:
        """
        Método alternativo para extraer contornos usando matplotlib
        
        Args:
            text: Texto a procesar
            
        Returns:
            Lista de contornos
        """
        # Crear figura temporal
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 3)
        ax.axis('off')
        
        # Renderizar texto con fuente grande
        text_obj = ax.text(1, 1.5, text, fontsize=120, fontfamily='sans-serif',
                          ha='left', va='center', transform=ax.transData)
        
        # Guardar como imagen temporal
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        # Cargar imagen y procesar
        img = cv2.imread(temp_file.name, cv2.IMREAD_GRAYSCALE)
        os.unlink(temp_file.name)  # Eliminar archivo temporal
        
        if img is None:
            return []
        
        # Invertir imagen (texto blanco sobre fondo negro)
        img = 255 - img
        
        # Encontrar contornos
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos
        min_area = 100
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        return valid_contours
    
    def _simplify_contours(self, contours: List[np.ndarray], epsilon: float = 0.5) -> List[np.ndarray]:
        """
        Simplificar contornos para reducir puntos
        
        Args:
            contours: Lista de contornos
            epsilon: Factor de simplificación
            
        Returns:
            Lista de contornos simplificados
        """
        simplified = []
        for contour in contours:
            if len(contour) > 2:
                simplified_contour = cv2.approxPolyDP(contour, epsilon, True)
                simplified.append(simplified_contour)
        return simplified
    
    def _scale_contours(self, contours: List[np.ndarray], target_size: float) -> List[np.ndarray]:
        """
        Escala los contornos al tamaño objetivo
        
        Args:
            contours: Lista de contornos
            target_size: Tamaño objetivo en mm
            
        Returns:
            Lista de contornos escalados
        """
        if not contours:
            return []
        
        # Encontrar bounding box de todos los contornos
        all_points = np.vstack([c.reshape(-1, 2) for c in contours])
        min_x, min_y = np.min(all_points, axis=0)
        max_x, max_y = np.max(all_points, axis=0)
        
        current_width = max_x - min_x
        current_height = max_y - min_y
        
        # Calcular factor de escala basado en la altura objetivo
        scale_factor = target_size / current_height
        
        # Escalar contornos y normalizar para que comiencen en (0,0)
        scaled_contours = []
        for contour in contours:
            scaled_contour = contour.astype(np.float64)
            # Escalar y normalizar X (empezar desde 0)
            scaled_contour[:, :, 0] = (scaled_contour[:, :, 0] - min_x) * scale_factor
            # Escalar y normalizar Y (invertir para que quede correcto y comience en 0)
            scaled_contour[:, :, 1] = (max_y - scaled_contour[:, :, 1]) * scale_factor
            scaled_contours.append(scaled_contour)
        
        return scaled_contours
    
    def _optimize_contour_order(self, contours: List[np.ndarray]) -> List[np.ndarray]:
        """
        Optimizar orden de contornos para minimizar movimientos
        
        Args:
            contours: Lista de contornos
            
        Returns:
            Lista de contornos reordenados
        """
        if len(contours) <= 1:
            return contours
        
        # Calcular el punto más a la izquierda de cada contorno
        contour_left_points = []
        for contour in contours:
            left_x = np.min(contour[:, :, 0])
            left_y = np.mean(contour[:, :, 1])
            contour_left_points.append((left_x, left_y))
        
        # Ordenar contornos por posición X (de izquierda a derecha)
        contour_with_left_x = list(zip(contours, contour_left_points))
        contour_with_left_x.sort(key=lambda x: x[1][0])
        ordered_contours = [contour for contour, _ in contour_with_left_x]
        
        return ordered_contours
    
    def _contours_to_gcode(self, contours: List[np.ndarray], start_x: float, start_y: float) -> List[str]:
        """
        Convierte contornos a G-code con sistema de capas y potencia incremental para láser
        
        Args:
            contours: Lista de contornos
            start_x: Posición X inicial
            start_y: Posición Y inicial
            
        Returns:
            Lista de líneas de G-code
        """
        gcode_lines = []
        
        # Usar el orden optimizado de contornos (ya ordenados de izquierda a derecha)
        contours_with_area = []
        for contour in contours:
            try:
                area = cv2.contourArea(contour)
                if area > 0:  # Solo incluir contornos válidos
                    contours_with_area.append((contour, area))
            except:
                # Si hay error con el área, usar longitud del contorno
                contours_with_area.append((contour, len(contour)))
        
        # NO reordenar - usar el orden optimizado que ya viene de la función generate_gcode
        
        # Procesar cada capa
        for layer in range(self.num_layers):
            # Convertir porcentaje a valor del controlador (100% = 1000)
            power_value = self._convert_power_percent_to_value(self.laser_power_max)
            
            # Variable para rastrear la posición actual del láser
            current_x = None
            current_y = None
            
            for i, (contour, area) in enumerate(contours_with_area):
                if len(contour) < 2:
                    continue
                
                # Obtener el punto más a la izquierda del contorno
                leftmost_idx = np.argmin(contour[:, :, 0])
                leftmost_point = contour[leftmost_idx][0]
                target_x = start_x + leftmost_point[0]
                target_y = start_y + leftmost_point[1]
                
                # Solo mover si no estamos ya en la posición correcta
                # Para el primer contorno, asumir que ya estamos en la posición correcta (home)
                if current_x is None:
                    # Primer contorno - asumir que ya estamos en la posición correcta
                    current_x = target_x
                    current_y = target_y
                elif abs(current_x - target_x) > 0.001 or abs(current_y - target_y) > 0.001:
                    # Solo mover si no estamos ya en la posición correcta
                    gcode_lines.append(f"G0 X{target_x:.3f} Y{target_y:.3f}")
                    current_x = target_x
                    current_y = target_y
                
                # Configurar potencia del láser para esta capa
                gcode_lines.append(f"M3 S{power_value}")
                
                # Dibujar contorno
                for j, point in enumerate(contour):
                    x, y = point[0]
                    gcode_lines.append(f"G1 X{start_x + x:.3f} Y{start_y + y:.3f} F{self.feed_rate}")
                    current_x = start_x + x
                    current_y = start_y + y
                
                # Cerrar contorno si es necesario
                if len(contour) > 2:
                    first_point = contour[0][0]
                    gcode_lines.append(f"G1 X{start_x + first_point[0]:.3f} Y{start_y + first_point[1]:.3f}")
                    current_x = start_x + first_point[0]
                    current_y = start_y + first_point[1]
                
                # Apagar láser
                gcode_lines.append("M5")
            
            # Pausa entre capas (opcional)
            if layer < self.num_layers - 1:
                gcode_lines.append("G4 P1")
        
        return gcode_lines
    
    def generate_gcode(self, text: str, center_text: bool = True) -> List[str]:
        """
        Genera G-code completo para imprimir texto con fuentes profesionales
        
        Args:
            text: Texto a imprimir
            center_text: Si centrar el texto en la tabla
            
        Returns:
            Lista de líneas de G-code
        """
        gcode_lines = []
        
        # Encabezado del G-code - Solo comandos válidos
        gcode_lines.extend([
            "G21",
            "G90",
            "M5"
        ])
        
        # Extraer contornos del texto
        print("Extrayendo contornos del texto...")
        contours = self._get_text_contours_pil(text)
        
        # Si no se encontraron contornos, intentar método alternativo
        if not contours:
            print("Intentando método alternativo...")
            contours = self._get_text_contours_alternative(text)
        
        if not contours:
            print("No se pudieron extraer contornos del texto")
            return gcode_lines
        
        # Simplificar contornos - usar menos simplificación para mantener detalles
        print("Simplificando contornos...")
        contours = self._simplify_contours(contours, epsilon=0.5)
        
        # Escalar contornos
        print("Escalando contornos...")
        contours = self._scale_contours(contours, self.font_size)
        
        # Verificar y ajustar para que comience en (0,0)
        if contours:
            all_points = np.vstack([c.reshape(-1, 2) for c in contours])
            min_x, min_y = np.min(all_points, axis=0)
            
            # SIEMPRE ajustar para que comience en (0,0)
            print(f"Ajustando contornos para comenzar en (0,0) - Offset actual: ({min_x:.3f}, {min_y:.3f})")
            for contour in contours:
                contour[:, :, 0] -= min_x
                contour[:, :, 1] -= min_y
            
            # Verificar que el ajuste funcionó
            all_points = np.vstack([c.reshape(-1, 2) for c in contours])
            new_min_x, new_min_y = np.min(all_points, axis=0)
            print(f"Después del ajuste: min=({new_min_x:.3f}, {new_min_y:.3f})")
        
        # Optimizar orden de contornos para minimizar movimientos
        print("Optimizando orden de contornos...")
        contours = self._optimize_contour_order(contours)
        
        # Calcular posición inicial respetando el origen GRBL y configuración de centrado
        all_points = np.vstack([c.reshape(-1, 2) for c in contours])
        text_width = np.max(all_points[:, 0]) - np.min(all_points[:, 0])
        text_height = np.max(all_points[:, 1]) - np.min(all_points[:, 1])
        
        if center_text:
            # Centrar el texto en la tabla
            if text_width > self.table_width - 2:  # Margen de 2mm
                print(f"Advertencia: El texto es muy ancho ({text_width:.1f}mm) para la tabla ({self.table_width}mm)")
                start_x = 1.0  # Forzar margen mínimo
            else:
                start_x = (self.table_width - text_width) / 2
                
            if text_height > self.table_height - 2:  # Margen de 2mm
                print(f"Advertencia: El texto es muy alto ({text_height:.1f}mm) para la tabla ({self.table_height}mm)")
                start_y = 1.0  # Forzar margen mínimo
            else:
                start_y = (self.table_height - text_height) / 2
        else:
            # Comenzar exactamente desde el origen GRBL (0,0) - sin margen
            start_x = 0.0  # Exactamente en el origen
            start_y = 0.0  # Exactamente en el origen
        
        print(f"Texto comenzará en posición ({start_x:.1f}, {start_y:.1f}) - Dimensiones: {text_width:.1f}mm x {text_height:.1f}mm")
        
        # Convertir contornos a G-code
        print("Generando G-code...")
        contour_gcode = self._contours_to_gcode(contours, start_x, start_y)
        gcode_lines.extend(contour_gcode)
        
        # Finalizar - Regresar al inicio
        gcode_lines.extend([
            "G0 X0 Y0",
            "M30"
        ])
        
        return gcode_lines
    
    def generate_gcode_from_contours(self, contours: List[Tuple[float, float]]) -> str:
        """
        Generar G-code desde contornos de imagen
        
        Args:
            contours: Lista de puntos (x, y) de contornos
            
        Returns:
            G-code como string
        """
        gcode_lines = []
        
        # Encabezado
        gcode_lines.extend([
            "; G-code generado desde imagen",
            f"; Dimensiones de tabla: {self.table_width}x{self.table_height}mm",
            f"; Potencia máxima: {self.laser_power_max}%",
            f"; Velocidad: {self.feed_rate}mm/min",
            f"; Número de capas: {self.num_layers}",
            "",
            "G0 X0 Y0 ; Ir al HOME (origen)"
        ])
        
        # Procesar contornos
        current_layer = 1
        laser_on = False
        first_point = True
        
        for i, (x, y) in enumerate(contours):
            # Verificar si es un punto de salto (NaN)
            if np.isnan(x) or np.isnan(y):
                if laser_on:
                    gcode_lines.append("M5 ; Apagar láser")
                    laser_on = False
                continue
            
            # Verificar si necesitamos cambiar de capa
            if current_layer <= self.num_layers:
                if i == 0 or (i > 0 and (np.isnan(contours[i-1][0]) or np.isnan(contours[i-1][1]))):
                    # Inicio de nuevo contorno
                    if first_point:
                        # Para el primer punto: posicionar, encender láser, empezar a dibujar
                        gcode_lines.append(f"G0 X{x:.3f} Y{y:.3f} ; Posicionar en primer punto")
                        # Convertir porcentaje a valor del controlador
                        power_value = self._convert_power_percent_to_value(self.laser_power_max)
                        gcode_lines.append(f"M3 S{power_value} ; Encender láser - Capa {current_layer}")
                        gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{self.feed_rate} ; Iniciar grabado")
                        laser_on = True
                        first_point = False
                    else:
                        # Para contornos siguientes: posicionar, encender láser, empezar a dibujar
                        gcode_lines.append(f"G0 X{x:.3f} Y{y:.3f} ; Posicionar")
                        if not laser_on:
                            # Convertir porcentaje a valor del controlador
                            power_value = self._convert_power_percent_to_value(self.laser_power_max)
                            gcode_lines.append(f"M3 S{power_value} ; Encender láser - Capa {current_layer}")
                            laser_on = True
                        gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{self.feed_rate} ; Iniciar grabado")
                else:
                    # Continuar contorno
                    gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{self.feed_rate}")
            else:
                # Apagar láser si hemos terminado todas las capas
                if laser_on:
                    gcode_lines.append("M5 ; Apagar láser")
                    laser_on = False
                break
        
        # Asegurar que el láser esté apagado al final
        if laser_on:
            gcode_lines.append("M5 ; Apagar láser")
        
        # Finalizar - regresar al HOME
        gcode_lines.extend([
            "G0 X0 Y0 ; Regresar al HOME",
            "M30 ; Fin del programa"
        ])
        
        return '\n'.join(gcode_lines)
    
    def generate_cut_gcode(self, cut_distance: float, cut_depth: float, cut_angle: float, 
                          start_x: float = 0.0, start_y: float = 0.0, 
                          cut_power: float = None, cut_speed: float = None) -> List[str]:
        """
        Genera G-code para corte láser
        
        Args:
            cut_distance: Distancia del corte en mm
            cut_depth: Profundidad del corte en mm (número de pasadas)
            cut_angle: Ángulo del corte en grados (0° = horizontal, 90° = vertical)
            start_x: Posición X inicial en mm
            start_y: Posición Y inicial en mm
            cut_power: Potencia del láser para corte (si no se especifica, usa laser_power_max)
            cut_speed: Velocidad de corte (si no se especifica, usa feed_rate)
            
        Returns:
            Lista de líneas de G-code para el corte
        """
        gcode_lines = []
        
        # Usar valores por defecto si no se especifican
        if cut_power is None:
            cut_power = self.laser_power_max
        if cut_speed is None:
            cut_speed = self.feed_rate
        
        # Convertir ángulo a radianes
        angle_rad = np.radians(cut_angle)
        
        # Calcular punto final del corte
        end_x = start_x + cut_distance * np.cos(angle_rad)
        end_y = start_y + cut_distance * np.sin(angle_rad)
        
        # Encabezado del G-code
        gcode_lines.extend([
            "; G-code para corte láser",
            f"; Distancia: {cut_distance}mm",
            f"; Profundidad: {cut_depth}mm ({int(cut_depth)} pasadas)",
            f"; Ángulo: {cut_angle}°",
            f"; Potencia: {cut_power}%",
            f"; Velocidad: {cut_speed}mm/min",
            "",
            "G21 ; Unidades en milímetros",
            "G90 ; Posicionamiento absoluto",
            "M5 ; Asegurar que el láser esté apagado"
        ])
        
        # Realizar múltiples pasadas para la profundidad
        for pass_num in range(int(cut_depth)):
            gcode_lines.extend([
                f"; Pasada {pass_num + 1} de {int(cut_depth)}",
                f"G0 X{start_x:.3f} Y{start_y:.3f} ; Posicionar en inicio",
                f"M3 S{self._convert_power_percent_to_value(cut_power)} ; Encender láser - Potencia {cut_power}%",
                f"G1 X{end_x:.3f} Y{end_y:.3f} F{cut_speed} ; Realizar corte",
                "M5 ; Apagar láser"
            ])
            
            # Pausa entre pasadas (excepto en la última)
            if pass_num < int(cut_depth) - 1:
                gcode_lines.append("G4 P0.5 ; Pausa entre pasadas")
        
        # Finalizar
        gcode_lines.extend([
            "G0 X0 Y0 ; Regresar al origen",
            "M30 ; Fin del programa"
        ])
        
        return gcode_lines
    
    def generate_multiple_cuts_gcode(self, cuts: List[dict], 
                                   cut_power: float = None, cut_speed: float = None) -> List[str]:
        """
        Genera G-code para múltiples cortes láser
        
        Args:
            cuts: Lista de diccionarios con parámetros de cada corte
                  Cada diccionario debe contener: distance, depth, angle, start_x, start_y
            cut_power: Potencia del láser para todos los cortes
            cut_speed: Velocidad para todos los cortes
            
        Returns:
            Lista de líneas de G-code para todos los cortes
        """
        gcode_lines = []
        
        # Usar valores por defecto si no se especifican
        if cut_power is None:
            cut_power = self.laser_power_max
        if cut_speed is None:
            cut_speed = self.feed_rate
        
        # Encabezado general
        gcode_lines.extend([
            "; G-code para múltiples cortes láser",
            f"; Número de cortes: {len(cuts)}",
            f"; Potencia: {cut_power}%",
            f"; Velocidad: {cut_speed}mm/min",
            "",
            "G21 ; Unidades en milímetros",
            "G90 ; Posicionamiento absoluto",
            "M5 ; Asegurar que el láser esté apagado"
        ])
        
        # Procesar cada corte
        for i, cut in enumerate(cuts):
            gcode_lines.extend([
                f"; Corte {i + 1} de {len(cuts)}",
                f"; Distancia: {cut['distance']}mm, Profundidad: {cut['depth']}mm, Ángulo: {cut['angle']}°"
            ])
            
            # Generar G-code para este corte
            cut_gcode = self.generate_cut_gcode(
                cut_distance=cut['distance'],
                cut_depth=cut['depth'],
                cut_angle=cut['angle'],
                start_x=cut.get('start_x', 0.0),
                start_y=cut.get('start_y', 0.0),
                cut_power=cut_power,
                cut_speed=cut_speed
            )
            
            # Agregar solo las líneas de movimiento (sin encabezados duplicados)
            for line in cut_gcode:
                if not line.startswith(';') and not line.startswith('G21') and not line.startswith('G90') and not line.startswith('M5'):
                    gcode_lines.append(line)
            
            # Pausa entre cortes (excepto en el último)
            if i < len(cuts) - 1:
                gcode_lines.append("G4 P1 ; Pausa entre cortes")
        
        # Finalizar
        gcode_lines.extend([
            "G0 X0 Y0 ; Regresar al origen",
            "M30 ; Fin del programa"
        ])
        
        return gcode_lines
    
    def generate_gcode_from_svg_layers(self, layers: List[Dict], 
                                      table_width: float = None, 
                                      table_height: float = None,
                                      scale_factor: float = 1.0,
                                      offset_x: float = 0.0,
                                      offset_y: float = 0.0) -> str:
        """
        Generar G-code desde elementos SVG organizados por capas
        
        Args:
            layers: Lista de diccionarios, cada uno representa una capa con:
                   - 'layer_name': Nombre de la capa
                   - 'speed': Velocidad de desplazamiento (mm/min)
                   - 'power': Potencia del láser (%)
                   - 'elements': Lista de elementos SVG, cada uno con:
                     - 'id': ID del elemento
                     - 'points': Lista de puntos [(x, y), ...]
            table_width: Ancho de la tabla (opcional, usa self.table_width si no se especifica)
            table_height: Alto de la tabla (opcional, usa self.table_height si no se especifica)
            scale_factor: Factor de escala para los puntos SVG
            offset_x: Offset X para posicionar el diseño
            offset_y: Offset Y para posicionar el diseño
            
        Returns:
            G-code como string
        """
        gcode_lines = []
        
        # Usar dimensiones proporcionadas o las del generador
        tw = table_width if table_width is not None else self.table_width
        th = table_height if table_height is not None else self.table_height
        
        # Encabezado
        gcode_lines.extend([
            "; G-code generado desde SVG con capas configurables",
            f"; Dimensiones de tabla: {tw}x{th}mm",
            f"; Número de capas: {len(layers)}",
            "",
            "G21 ; Unidades en milímetros",
            "G90 ; Posicionamiento absoluto",
            "M5 ; Asegurar que el láser esté apagado",
            "G0 X0 Y0 ; Ir al HOME (origen)"
        ])
        
        # Calcular bounding box de todos los elementos para normalizar coordenadas
        all_points_for_bbox = []
        for layer in layers:
            for element in layer.get('elements', []):
                points = element.get('points', [])
                if points:
                    for point in points:
                        all_points_for_bbox.append((point[0] * scale_factor, point[1] * scale_factor))
        
        # Normalizar coordenadas: encontrar mínimo y ajustar para que empiece en (0,0)
        if all_points_for_bbox:
            min_x = min(p[0] for p in all_points_for_bbox)
            min_y = min(p[1] for p in all_points_for_bbox)
        else:
            min_x = 0
            min_y = 0
        
        # Aplicar offset adicional para margen desde el origen
        margin_x = offset_x
        margin_y = offset_y
        
        # Procesar cada capa
        for layer_idx, layer in enumerate(layers):
            layer_name = layer.get('layer_name', f'Layer_{layer_idx + 1}')
            speed = float(layer.get('speed', self.feed_rate))
            power = float(layer.get('power', self.laser_power_max))
            num_passes = int(layer.get('num_passes', 1))  # Número de pasadas
            elements = layer.get('elements', [])
            
            if not elements:
                continue
            
            # Comentario de inicio de capa
            gcode_lines.append(f"; === Capa: {layer_name} ===")
            gcode_lines.append(f"; Velocidad: {speed}mm/min, Potencia: {power}%, Pasadas: {num_passes}")
            
            # Procesar cada elemento de la capa
            for elem_idx, element in enumerate(elements):
                points = element.get('points', [])
                elem_id = element.get('id', f'elem_{elem_idx}')
                
                if not points:
                    continue
                
                # Comentario del elemento
                gcode_lines.append(f"; Elemento: {elem_id}")
                
                # Repetir el corte según el número de pasadas
                for pass_num in range(num_passes):
                    if num_passes > 1:
                        gcode_lines.append(f"; Pasada {pass_num + 1} de {num_passes}")
                    
                    # Asegurar que el láser esté apagado antes del movimiento rápido
                    gcode_lines.append("M5 ; Asegurar láser apagado para desplazamiento")
                    
                    # Normalizar coordenadas: restar mínimo y agregar margen
                    # Esto asegura que el diseño empiece desde la esquina inferior izquierda (0,0)
                    first_point = points[0]
                    x = (first_point[0] * scale_factor) - min_x + margin_x
                    y = (first_point[1] * scale_factor) - min_y + margin_y
                    gcode_lines.append(f"G0 X{x:.3f} Y{y:.3f} ; Desplazamiento rápido (láser apagado)")
                    
                    # Encender láser SOLO cuando vamos a cortar (G1)
                    # Convertir porcentaje a valor del controlador (100% = 1000)
                    power_value = self._convert_power_percent_to_value(power)
                    gcode_lines.append(f"M3 S{power_value} ; Encender láser - {layer_name} ({power}% = {power_value})")
                    
                    # Dibujar el path (normalizando coordenadas) - SOLO aquí el láser está encendido
                    for point in points[1:]:
                        x = (point[0] * scale_factor) - min_x + margin_x
                        y = (point[1] * scale_factor) - min_y + margin_y
                        gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{speed} ; Corte con láser encendido")
                    
                    # Cerrar path si el primer y último punto son diferentes
                    if len(points) > 1 and points[0] != points[-1]:
                        first_x = (points[0][0] * scale_factor) - min_x + margin_x
                        first_y = (points[0][1] * scale_factor) - min_y + margin_y
                        gcode_lines.append(f"G1 X{first_x:.3f} Y{first_y:.3f} F{speed} ; Cerrar path")
                    
                    # Apagar láser inmediatamente después del corte
                    gcode_lines.append("M5 ; Apagar láser después del corte")
                    
                    # Pausa entre pasadas (excepto en la última)
                    if pass_num < num_passes - 1:
                        gcode_lines.append("G4 P0.5 ; Pausa entre pasadas")
            
            # Pausa entre capas (excepto en la última)
            if layer_idx < len(layers) - 1:
                gcode_lines.append("G4 P0.5 ; Pausa entre capas")
        
        # Finalizar - regresar al HOME
        gcode_lines.extend([
            "",
            "G0 X0 Y0 ; Regresar al HOME",
            "M30 ; Fin del programa"
        ])
        
        return '\n'.join(gcode_lines)
    
    def save_gcode(self, gcode_lines: List[str], filename: str) -> None:
        """
        Guardar G-code en archivo
        
        Args:
            gcode_lines: Lista de líneas de G-code
            filename: Nombre del archivo
        """
        with open(filename, 'w', encoding='utf-8') as f:
            for line in gcode_lines:
                f.write(line + '\n')
