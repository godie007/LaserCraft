#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de SVG para Vectorización
Extrae paths y elementos de archivos SVG para generación de G-code
"""

import xml.etree.ElementTree as ET
from svgpathtools import parse_path, Path, Line, CubicBezier, QuadraticBezier, Arc
import numpy as np
from typing import List, Dict, Tuple, Optional
import re
import os


class SVGProcessor:
    """Procesador de archivos SVG para extracción de elementos vectoriales"""
    
    def __init__(self):
        self.supported_formats = {'.svg'}
        self.namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
    
    def parse_svg(self, svg_path: str) -> Dict:
        """
        Parsear archivo SVG y extraer información básica
        
        Args:
            svg_path: Ruta al archivo SVG
            
        Returns:
            Diccionario con información del SVG
        """
        try:
            # Intentar parsear con manejo de namespaces
            try:
                tree = ET.parse(svg_path)
            except ET.ParseError as e:
                raise ValueError(f"Error al parsear XML del SVG: {str(e)}")
            
            root = tree.getroot()
            
            # Remover namespace si existe
            if root.tag.startswith('{'):
                # Extraer namespace
                namespace = root.tag.split('}')[0][1:]
                # Registrar namespace
                ET.register_namespace('', namespace)
                # Actualizar nombrespaces
                self.namespaces['svg'] = namespace
            
            # Obtener dimensiones del viewBox o width/height
            viewbox = root.get('viewBox', '') or root.get('{http://www.w3.org/2000/svg}viewBox', '')
            width = root.get('width', '') or root.get('{http://www.w3.org/2000/svg}width', '')
            height = root.get('height', '') or root.get('{http://www.w3.org/2000/svg}height', '')
            
            # Función auxiliar para extraer número de string con unidades
            def extract_number(value: str, default: float = 100.0) -> float:
                if not value:
                    return default
                # Remover unidades comunes
                value = value.strip().replace('px', '').replace('mm', '').replace('cm', '').replace('in', '').replace('pt', '')
                try:
                    return float(value)
                except:
                    return default
            
            # Parsear viewBox
            if viewbox:
                parts = viewbox.strip().split()
                if len(parts) >= 4:
                    try:
                        x, y, w, h = map(float, parts[:4])
                        svg_width = w
                        svg_height = h
                    except:
                        svg_width = extract_number(width)
                        svg_height = extract_number(height)
                else:
                    svg_width = extract_number(width)
                    svg_height = extract_number(height)
            else:
                svg_width = extract_number(width)
                svg_height = extract_number(height)
            
            return {
                'root': root,
                'width': svg_width,
                'height': svg_height,
                'viewbox': viewbox,
                'tree': tree
            }
        except Exception as e:
            raise ValueError(f"Error al parsear SVG: {str(e)}")
    
    def extract_elements(self, svg_path: str) -> List[Dict]:
        """
        Extraer todos los elementos (paths, rect, circle, etc.) del SVG
        
        Args:
            svg_path: Ruta al archivo SVG
            
        Returns:
            Lista de diccionarios con información de cada elemento
        """
        try:
            svg_info = self.parse_svg(svg_path)
            root = svg_info['root']
            elements = []
            element_id = 0
            used_names = set()  # Rastrear nombres usados para evitar duplicados
            
            # Función auxiliar para detectar si un nombre es técnico
            def is_technical_name(name):
                if not name:
                    return True
                technical_patterns = ['__', '_w', 'Part__', 'Sprocket_', 'Python']
                return any(pattern in name for pattern in technical_patterns)
            
            # Función auxiliar para extraer nombre/ID del elemento - buscar en múltiples lugares
            def get_element_name(elem, default_prefix='element', parent_name=None):
                # 0. PRIMERO: Buscar elemento <title> dentro del elemento (FreeCAD usa esto para nombres naturales)
                for title_elem in elem.findall('.//{http://www.w3.org/2000/svg}title'):
                    title_text = title_elem.text
                    if title_text:
                        # Limpiar formato b'nombre' que FreeCAD a veces usa
                        title_text = title_text.strip()
                        # Remover prefijo b' y sufijo ' si existe
                        if title_text.startswith("b'") and title_text.endswith("'"):
                            title_text = title_text[2:-1]
                        elif title_text.startswith('b"') and title_text.endswith('"'):
                            title_text = title_text[2:-1]
                        # Solo usar el título si no es técnico
                        if title_text and not is_technical_name(title_text):
                            return title_text
                
                # También buscar en el elemento mismo (no solo hijos)
                title_elem = elem.find('{http://www.w3.org/2000/svg}title')
                if title_elem is not None and title_elem.text:
                    title_text = title_elem.text.strip()
                    if title_text.startswith("b'") and title_text.endswith("'"):
                        title_text = title_text[2:-1]
                    elif title_text.startswith('b"') and title_text.endswith('"'):
                        title_text = title_text[2:-1]
                    # Solo usar el título si no es técnico
                    if title_text and not is_technical_name(title_text):
                        return title_text
                
                # 1. Intentar obtener 'id' estándar
                elem_id = elem.get('id', '')
                if elem_id:
                    # Si el ID es técnico y hay un nombre de grupo padre natural, preferir el padre
                    if is_technical_name(elem_id) and parent_name and not is_technical_name(parent_name):
                        return parent_name
                    # Si el ID no es técnico, usarlo
                    if not is_technical_name(elem_id):
                        return elem_id
                    # Si el ID es técnico pero no hay padre natural, devolver None para generar nombre descriptivo
                    return None
                
                # 2. Intentar obtener 'inkscape:label' (común en FreeCAD/Inkscape)
                # Buscar con namespace completo
                inkscape_label = elem.get('{http://www.inkscape.org/namespaces/inkscape}label', '')
                if inkscape_label:
                    return inkscape_label
                
                # 3. Intentar obtener 'sodipodi:label'
                sodipodi_label = elem.get('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}label', '')
                if sodipodi_label:
                    return sodipodi_label
                
                # 4. Intentar obtener atributo 'name'
                name = elem.get('name', '')
                if name:
                    return name
                
                # 5. Si está en un grupo con nombre natural (no técnico), usar el nombre del grupo
                if parent_name and not is_technical_name(parent_name):
                    return parent_name
                
                # 6. NO devolver nombre técnico del padre
                return None
            
            # Función recursiva para extraer elementos
            def extract_recursive(element, parent_transform=None, depth=0, parent_name=None):
                nonlocal element_id
                
                # Obtener transformación del elemento
                transform = element.get('transform', '')
                if transform:
                    # Parsear transformación básica (translate, scale, rotate)
                    # Por simplicidad, almacenamos la cadena completa
                    current_transform = transform
                else:
                    current_transform = parent_transform
                
                # Manejar namespaces correctamente
                if '}' in element.tag:
                    tag = element.tag.split('}')[-1]
                else:
                    tag = element.tag
                
                # Ignorar el elemento raíz <svg> - solo procesar sus hijos
                if tag == 'svg':
                    for child in element:
                        extract_recursive(child, current_transform, depth + 1, parent_name)
                    return
                
                # Si es un grupo (<g>), extraer su nombre y procesar hijos
                if tag == 'g':
                    # Para grupos, obtener el nombre del grupo (puede venir del título o del ID)
                    group_name = get_element_name(element, 'group', parent_name)
                    # Si el grupo tiene un título natural, ese es el nombre preferido para los hijos
                    group_title = None
                    title_elem = element.find('{http://www.w3.org/2000/svg}title')
                    if title_elem is not None and title_elem.text:
                        title_text = title_elem.text.strip()
                        if title_text.startswith("b'") and title_text.endswith("'"):
                            title_text = title_text[2:-1]
                        elif title_text.startswith('b"') and title_text.endswith('"'):
                            title_text = title_text[2:-1]
                        # Solo usar título si no es técnico
                        if title_text and not is_technical_name(title_text):
                            group_title = title_text
                    
                    # Usar el título natural del grupo como nombre preferido para hijos
                    # Si no hay título natural, NO usar el nombre del grupo si es técnico
                    # Esto asegura que los hijos generen sus propios nombres descriptivos
                    if group_title:
                        final_group_name = group_title
                    elif group_name and not is_technical_name(group_name):
                        final_group_name = group_name
                    else:
                        # Si el grupo es técnico, NO pasar su nombre a los hijos
                        # Los hijos generarán sus propios nombres descriptivos
                        final_group_name = None
                    
                    # Procesar hijos con el nombre del grupo como contexto
                    # IMPORTANTE: Si final_group_name es None (grupo técnico), los hijos generarán sus propios nombres
                    # NO pasar parent_name para evitar que hereden nombres de grupos anteriores
                    for child in element:
                        extract_recursive(child, current_transform, depth + 1, final_group_name)
                    return
                
                # Obtener el nombre/ID del elemento (con fallback)
                elem_name = get_element_name(element, tag, parent_name)
                
                # Si el elemento tiene un ID técnico y hay un nombre de grupo padre natural,
                # preferir el nombre del grupo padre (que viene del título natural)
                # PERO solo si el padre no es técnico
                if elem_name and parent_name:
                    if is_technical_name(elem_name) and not is_technical_name(parent_name):
                        # Usar el nombre del padre natural
                        elem_name = parent_name
                    elif is_technical_name(elem_name) and is_technical_name(parent_name):
                        # Si ambos son técnicos, descartar y generar nombre descriptivo
                        elem_name = None
                elif not elem_name and parent_name and is_technical_name(parent_name):
                    # Si no hay nombre y el padre es técnico, NO usar el padre
                    elem_name = None
                
                # Si todavía no tenemos un nombre o es técnico, generar uno descriptivo basado en el tipo
                if not elem_name or is_technical_name(elem_name):
                    # Generar nombre descriptivo basado en el tipo de elemento
                    type_names = {
                        'circle': 'circunferencia',
                        'ellipse': 'elipse',
                        'rect': 'rectangulo',
                        'path': 'trayectoria',
                        'line': 'linea',
                        'polyline': 'polilinea',
                        'polygon': 'poligono'
                    }
                    descriptive_name = type_names.get(tag, tag)
                    
                    # IMPORTANTE: Solo usar el padre como prefijo si es natural (no técnico)
                    # Si el padre es técnico o None, usar solo el nombre descriptivo
                    if parent_name and not is_technical_name(parent_name):
                        # Hay un padre natural, usarlo como prefijo
                        base_name = f"{parent_name}_{descriptive_name}"
                    else:
                        # No hay padre natural o es técnico, usar solo el nombre descriptivo
                        base_name = descriptive_name
                    
                    # Asegurar nombres únicos: si ya existe un elemento con este nombre, agregar sufijo
                    elem_name = base_name
                    counter = 1
                    original_base = base_name
                    while elem_name in used_names:
                        elem_name = f"{original_base}_{counter}"
                        counter += 1
                    used_names.add(elem_name)
                
                # Ignorar otros elementos que no son formas (como <defs>, etc.)
                # pero procesar sus hijos
                if tag not in ['path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon']:
                    # Procesar hijos pero no agregar este elemento
                    for child in element:
                        extract_recursive(child, current_transform, depth + 1, elem_name or parent_name)
                    return
                
                # Extraer diferentes tipos de elementos
                # IMPORTANTE: Después de agregar un elemento, NO procesar sus hijos
                # porque los elementos SVG (path, circle, etc.) no tienen hijos que sean formas
                if tag == 'path':
                    d = element.get('d', '')
                    if d:
                        elements.append({
                            'id': elem_name,
                            'type': 'path',
                            'd': d,
                            'transform': current_transform,
                            'fill': element.get('fill', 'black'),
                            'stroke': element.get('stroke', 'none'),
                            'stroke_width': element.get('stroke-width', '1'),
                            'element': element,
                            'depth': depth
                        })
                        return  # NO procesar hijos de path
                
                elif tag == 'rect':
                    x = float(element.get('x', 0))
                    y = float(element.get('y', 0))
                    width = float(element.get('width', 0))
                    height = float(element.get('height', 0))
                    rx = float(element.get('rx', 0))
                    ry = float(element.get('ry', 0))
                    
                    # Convertir rect a path
                    if rx == 0 and ry == 0:
                        d = f"M {x} {y} L {x+width} {y} L {x+width} {y+height} L {x} {y+height} Z"
                    else:
                        d = f"M {x+rx} {y} L {x+width-rx} {y} A {rx} {ry} 0 0 1 {x+width} {y+ry} L {x+width} {y+height-ry} A {rx} {ry} 0 0 1 {x+width-rx} {y+height} L {x+rx} {y+height} A {rx} {ry} 0 0 1 {x} {y+height-ry} L {x} {y+ry} A {rx} {ry} 0 0 1 {x+rx} {y} Z"
                    
                    elements.append({
                        'id': elem_name,
                        'type': 'rect',
                        'd': d,
                        'transform': current_transform,
                        'fill': element.get('fill', 'black'),
                        'stroke': element.get('stroke', 'none'),
                        'stroke_width': element.get('stroke-width', '1'),
                        'element': element,
                        'depth': depth,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    })
                    return  # NO procesar hijos de rect
                
                elif tag == 'circle':
                    cx = float(element.get('cx', 0))
                    cy = float(element.get('cy', 0))
                    r = float(element.get('r', 0))
                    
                    # Convertir circle a path
                    d = f"M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy} A {r} {r} 0 0 1 {cx-r} {cy} Z"
                    
                    elements.append({
                        'id': elem_name,
                        'type': 'circle',
                        'd': d,
                        'transform': current_transform,
                        'fill': element.get('fill', 'black'),
                        'stroke': element.get('stroke', 'none'),
                        'stroke_width': element.get('stroke-width', '1'),
                        'element': element,
                        'depth': depth,
                        'cx': cx,
                        'cy': cy,
                        'r': r
                    })
                    return  # NO procesar hijos de circle
                
                elif tag == 'ellipse':
                    cx = float(element.get('cx', 0))
                    cy = float(element.get('cy', 0))
                    rx = float(element.get('rx', 0))
                    ry = float(element.get('ry', 0))
                    
                    # Convertir ellipse a path
                    d = f"M {cx-rx} {cy} A {rx} {ry} 0 0 1 {cx+rx} {cy} A {rx} {ry} 0 0 1 {cx-rx} {cy} Z"
                    
                    elements.append({
                        'id': elem_name,
                        'type': 'ellipse',
                        'd': d,
                        'transform': current_transform,
                        'fill': element.get('fill', 'black'),
                        'stroke': element.get('stroke', 'none'),
                        'stroke_width': element.get('stroke-width', '1'),
                        'element': element,
                        'depth': depth,
                        'cx': cx,
                        'cy': cy,
                        'rx': rx,
                        'ry': ry
                    })
                    return  # NO procesar hijos de ellipse
                
                elif tag == 'line':
                    x1 = float(element.get('x1', 0))
                    y1 = float(element.get('y1', 0))
                    x2 = float(element.get('x2', 0))
                    y2 = float(element.get('y2', 0))
                    
                    # Convertir line a path
                    d = f"M {x1} {y1} L {x2} {y2}"
                    
                    elements.append({
                        'id': elem_name,
                        'type': 'line',
                        'd': d,
                        'transform': current_transform,
                        'fill': 'none',
                        'stroke': element.get('stroke', 'black'),
                        'stroke_width': element.get('stroke-width', '1'),
                        'element': element,
                        'depth': depth,
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2
                    })
                    return  # NO procesar hijos de line
                
                elif tag == 'polyline':
                    points = element.get('points', '')
                    if points:
                        # Parsear puntos
                        point_list = re.findall(r'([\d.]+),([\d.]+)', points)
                        if point_list:
                            path_points = ' '.join([f"{x},{y}" for x, y in point_list])
                            d = f"M {path_points.replace(',', ' ').replace(' ', ' L ')}"
                            
                            elements.append({
                                'id': elem_name,
                                'type': 'polyline',
                                'd': d,
                                'transform': current_transform,
                                'fill': 'none',
                                'stroke': element.get('stroke', 'black'),
                                'stroke_width': element.get('stroke-width', '1'),
                                'element': element,
                                'depth': depth
                            })
                            return  # NO procesar hijos de polyline
                
                elif tag == 'polygon':
                    points = element.get('points', '')
                    if points:
                        # Parsear puntos
                        point_list = re.findall(r'([\d.]+),([\d.]+)', points)
                        if point_list:
                            path_points = ' '.join([f"{x},{y}" for x, y in point_list])
                            d = f"M {path_points.replace(',', ' ').replace(' ', ' L ')} Z"
                            
                            elements.append({
                                'id': elem_name,
                                'type': 'polygon',
                                'd': d,
                                'transform': current_transform,
                                'fill': element.get('fill', 'black'),
                                'stroke': element.get('stroke', 'none'),
                                'stroke_width': element.get('stroke-width', '1'),
                                'element': element,
                                'depth': depth
                            })
                            return  # NO procesar hijos de polygon
                
                # Si llegamos aquí, el elemento no es una forma reconocida
                # Procesar hijos solo si no es una forma (ya que las formas no tienen hijos que sean formas)
                # Esto solo debería ejecutarse para elementos como <defs>, <title>, etc.
                for child in element:
                    extract_recursive(child, current_transform, depth + 1, parent_name)
            
            # Extraer elementos desde la raíz
            extract_recursive(root)
            
            return elements
            
        except Exception as e:
            raise ValueError(f"Error al extraer elementos SVG: {str(e)}")
    
    def path_to_points(self, path_d: str, num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Convertir path SVG a lista de puntos
        
        Args:
            path_d: Atributo 'd' del path SVG
            num_points: Número de puntos a generar por segmento
            
        Returns:
            Lista de tuplas (x, y)
        """
        try:
            # Parsear path usando svgpathtools
            path = parse_path(path_d)
            
            points = []
            
            # Generar puntos a lo largo del path
            for i in range(num_points + 1):
                t = i / num_points
                try:
                    point = path.point(t)
                    points.append((point.real, point.imag))
                except:
                    # Si hay error, intentar con el siguiente punto
                    continue
            
            return points
            
        except Exception as e:
            # Si falla el parsing, intentar método simple
            # Extraer comandos M, L, C, etc. y convertirlos a puntos
            return self._simple_path_to_points(path_d)
    
    def _simple_path_to_points(self, path_d: str) -> List[Tuple[float, float]]:
        """
        Método simple para convertir path a puntos (fallback)
        """
        points = []
        current_x, current_y = 0, 0
        
        # Parsear comandos básicos
        commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)', path_d)
        
        for cmd, args in commands:
            args = args.strip()
            if not args:
                continue
            
            # Parsear números
            numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', args)
            numbers = [float(n) for n in numbers]
            
            if cmd.upper() == 'M':  # Move to
                if len(numbers) >= 2:
                    current_x, current_y = numbers[0], numbers[1]
                    points.append((current_x, current_y))
            
            elif cmd.upper() == 'L':  # Line to
                if len(numbers) >= 2:
                    current_x, current_y = numbers[0], numbers[1]
                    points.append((current_x, current_y))
            
            elif cmd.upper() == 'Z':  # Close path
                if points:
                    points.append(points[0])  # Cerrar al primer punto
            
            elif cmd.upper() == 'H':  # Horizontal line
                if len(numbers) >= 1:
                    current_x = numbers[0]
                    points.append((current_x, current_y))
            
            elif cmd.upper() == 'V':  # Vertical line
                if len(numbers) >= 1:
                    current_y = numbers[0]
                    points.append((current_x, current_y))
            
            # Para otros comandos (C, Q, A, etc.), usar interpolación simple
            elif cmd.upper() in ['C', 'S', 'Q', 'T', 'A']:
                if len(numbers) >= 2:
                    # Tomar el último punto como destino
                    current_x, current_y = numbers[-2], numbers[-1]
                    points.append((current_x, current_y))
        
        return points
    
    def get_svg_info(self, svg_path: str) -> Dict:
        """
        Obtener información general del SVG
        
        Args:
            svg_path: Ruta al archivo SVG
            
        Returns:
            Diccionario con información del SVG
        """
        try:
            svg_info = self.parse_svg(svg_path)
            file_size = os.path.getsize(svg_path)
            
            # Intentar extraer elementos, pero no fallar si hay problemas
            elements = []
            try:
                elements = self.extract_elements(svg_path)
            except Exception as extract_error:
                # Si falla la extracción, continuar con información básica
                print(f"Advertencia: Error al extraer elementos: {str(extract_error)}")
                elements = []
            
            return {
                'width': svg_info['width'],
                'height': svg_info['height'],
                'viewbox': svg_info['viewbox'],
                'num_elements': len(elements),
                'file_size': file_size,
                'elements': [
                    {
                        'id': elem['id'],
                        'type': elem['type']
                    }
                    for elem in elements
                ]
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error completo en get_svg_info: {error_details}")
            raise ValueError(f"Error al obtener información SVG: {str(e)}")

