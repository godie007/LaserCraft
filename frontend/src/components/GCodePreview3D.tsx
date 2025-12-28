import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Box } from '@react-three/drei';
import * as THREE from 'three';

interface GCodeLayer {
  layer: number;
  power: number;
  paths: Array<{
    x: number;
    y: number;
    z: number;
  }>;
}

interface GCodePreview3DProps {
  gcodeData?: string;
  tableWidth: number;
  tableHeight: number;
  numLayers: number;
  lineHeight: number;
}

// Componente para renderizar el grabado final como contornos
const EngravingMesh: React.FC<{
  allPaths: { x: number; y: number }[];
  tableWidth: number;
  tableHeight: number;
  lineHeight: number;
}> = ({ allPaths, tableWidth, tableHeight, lineHeight }) => {
  if (allPaths.length === 0) return null;

  return (
    <group>
      {/* Crear líneas continuas del grabado */}
      {allPaths.map((point, pointIndex) => {
        if (pointIndex === 0) return null;
        
        const prevPoint = allPaths[pointIndex - 1];
        const distance = Math.sqrt(
          Math.pow(point.x - prevPoint.x, 2) + 
          Math.pow(point.y - prevPoint.y, 2)
        );
        
        // Conectar puntos cercanos con líneas gruesas
        if (distance < 8) {
          return (
            <group key={`line-${pointIndex}`}>
              {/* Línea principal del grabado - en alto relieve */}
              <line
                geometry={new THREE.BufferGeometry().setFromPoints([
                  new THREE.Vector3(prevPoint.x, prevPoint.y, 0.1),
                  new THREE.Vector3(point.x, point.y, 0.1)
                ])}
                material={new THREE.LineBasicMaterial({ 
                  color: '#FF4444', // Color rojo para corte láser
                  linewidth: 3,
                  transparent: true,
                  opacity: 0.9
                })}
              />
            </group>
          );
        }
        return null;
      })}
      
      {/* Puntos individuales para áreas aisladas */}
      {allPaths.map((point, pointIndex) => {
        const hasConnection = pointIndex > 0 && 
          Math.sqrt(
            Math.pow(point.x - allPaths[pointIndex - 1].x, 2) + 
            Math.pow(point.y - allPaths[pointIndex - 1].y, 2)
          ) < 5;
        
        const hasNextConnection = pointIndex < allPaths.length - 1 && 
          Math.sqrt(
            Math.pow(point.x - allPaths[pointIndex + 1].x, 2) + 
            Math.pow(point.y - allPaths[pointIndex + 1].y, 2)
          ) < 5;
        
        // Solo mostrar puntos que no están conectados
        if (!hasConnection && !hasNextConnection) {
          return (
            <group key={`isolated-${pointIndex}`}>
              {/* Punto del grabado */}
              <Box
                position={[point.x, point.y, 0.1]}
                args={[0.5, 0.5, 0.2]}
                material-color="#FF4444" // Color rojo para corte láser
                material-transparent
                material-opacity={0.9}
              />
            </group>
          );
        }
        return null;
      })}
    </group>
  );
};

// Componente para renderizar la tabla con cuadrícula
const TableMesh: React.FC<{
  width: number;
  height: number;
  engravingBounds: { minX: number; maxX: number; minY: number; maxY: number };
}> = ({ width, height, engravingBounds }) => {
  // Calcular el tamaño del plano basado en la figura + margen
  const margin = 20; // 20mm de margen alrededor de la figura
  const tableWidth = Math.max(width, (engravingBounds.maxX - engravingBounds.minX) + margin * 2);
  const tableHeight = Math.max(height, (engravingBounds.maxY - engravingBounds.minY) + margin * 2);
  
  const gridSize = 5; // Cada 5mm
  const gridLines = [];
  
  // Líneas verticales (paralelas al eje Y en CNCjs)
  for (let x = 0; x <= tableWidth; x += gridSize) {
    gridLines.push(
      <line
        key={`v-${x}`}
        geometry={new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(x, 0, 0),
          new THREE.Vector3(x, tableHeight, 0)
        ])}
        material={new THREE.LineBasicMaterial({ color: '#666666', opacity: 0.3, transparent: true, linewidth: 1 })}
      />
    );
  }
  
  // Líneas horizontales (paralelas al eje X en CNCjs)
  for (let y = 0; y <= tableHeight; y += gridSize) {
    gridLines.push(
      <line
        key={`h-${y}`}
        geometry={new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, y, 0),
          new THREE.Vector3(tableWidth, y, 0)
        ])}
        material={new THREE.LineBasicMaterial({ color: '#666666', opacity: 0.3, transparent: true, linewidth: 1 })}
      />
    );
  }
  
  return (
    <group>
      {/* Tabla base - origen en esquina inferior izquierda (0,0) */}
      <Box
        position={[tableWidth / 2, tableHeight / 2, -0.1]}
        args={[tableWidth, tableHeight, 0.2]}
        material-color="#E8E8E8" // Color gris claro para la tabla
        material-transparent
        material-opacity={0.4}
      />
      
      {/* Líneas de borde de la tabla */}
      <line
        geometry={new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(tableWidth, 0, 0),
          new THREE.Vector3(tableWidth, tableHeight, 0),
          new THREE.Vector3(0, tableHeight, 0),
          new THREE.Vector3(0, 0, 0)
        ])}
        material={new THREE.LineBasicMaterial({ color: '#333333', linewidth: 2 })}
      />
      {/* Cuadrícula */}
      {gridLines}
    </group>
  );
};

// Componente para renderizar las etiquetas de ejes y medidas
const AxisLabels: React.FC<{
  tableWidth: number;
  tableHeight: number;
  maxZ: number;
}> = ({ tableWidth, tableHeight, maxZ }) => {
  const gridSize = 5; // Cada 5mm
  const measureLabels = [];
  
  // Etiquetas de medidas en X (cada 10mm)
  for (let x = 0; x <= tableWidth; x += 10) {
    measureLabels.push(
      <Text
        key={`x-${x}`}
        position={[x, -1, 0]}
        fontSize={0.8}
        color="#888888"
        anchorX="center"
        anchorY="middle"
      >
        {x}mm
      </Text>
    );
  }
  
  // Etiquetas de medidas en Y (cada 10mm)
  for (let y = 0; y <= tableHeight; y += 10) {
    measureLabels.push(
      <Text
        key={`y-${y}`}
        position={[-1, y, 0]}
        fontSize={0.8}
        color="#888888"
        anchorX="center"
        anchorY="middle"
        rotation={[0, 0, Math.PI / 2]}
      >
        {y}mm
      </Text>
    );
  }
  
  return (
    <group>
      {/* Etiquetas de ejes principales */}
      {/* Eje X (horizontal, hacia la derecha) */}
      <Text
        position={[tableWidth / 2, -2, 0]}
        fontSize={1.5}
        color="red"
        anchorX="center"
        anchorY="middle"
      >
        X
      </Text>
      
      {/* Eje Y (hacia adelante, perpendicular a X) */}
      <Text
        position={[-2, tableHeight / 2, 0]}
        fontSize={1.5}
        color="green"
        anchorX="center"
        anchorY="middle"
        rotation={[0, 0, Math.PI / 2]}
      >
        Y
      </Text>
      
      {/* Eje Z (vertical, hacia arriba) */}
      <Text
        position={[-2, -2, maxZ / 2]}
        fontSize={1.5}
        color="blue"
        anchorX="center"
        anchorY="middle"
      >
        Z
      </Text>
      
      {/* Origen (0,0) marcado */}
      <Text
        position={[0, 0, 0.5]}
        fontSize={1.0}
        color="orange"
        anchorX="center"
        anchorY="middle"
      >
        (0,0)
      </Text>
      
      {/* Etiquetas de medidas */}
      {measureLabels}
    </group>
  );
};

// Componente principal de la vista previa 3D
const GCodePreview3D: React.FC<GCodePreview3DProps> = ({
  gcodeData,
  tableWidth,
  tableHeight,
  numLayers,
  lineHeight
}) => {
  const [layers, setLayers] = useState<GCodeLayer[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Función para parsear el G-code y extraer las capas
  const parseGCode = (gcode: string): GCodeLayer[] => {
    const lines = gcode.split('\n');
    const parsedLayers: GCodeLayer[] = [];
    let currentLayer: GCodeLayer | null = null;
    let currentPath: Array<{ x: number; y: number; z: number }> = [];
    let currentPower = 0;
    let layerIndex = 0;

    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // Detectar inicio de nueva capa (M3 S)
      if (trimmedLine.startsWith('M3 S')) {
        // Si hay una capa anterior, guardarla
        if (currentLayer && currentPath.length > 0) {
          currentLayer.paths = [...currentPath];
          parsedLayers.push(currentLayer);
        }
        
        // Extraer potencia
        const powerMatch = trimmedLine.match(/M3 S(\d+)/);
        currentPower = powerMatch ? parseInt(powerMatch[1]) : 0;
        
        // Crear nueva capa
        currentLayer = {
          layer: layerIndex,
          power: currentPower,
          paths: []
        };
        currentPath = [];
        layerIndex++;
      }
      
      // Detectar comandos G0 (movimiento rápido - láser apagado)
      else if (trimmedLine.startsWith('G0') && currentLayer) {
        const xMatch = trimmedLine.match(/X([\d.-]+)/);
        const yMatch = trimmedLine.match(/Y([\d.-]+)/);
        
        if (xMatch && yMatch) {
          const x = parseFloat(xMatch[1]);
          const y = parseFloat(yMatch[1]);
          const z = currentLayer.layer * lineHeight;
          
          // G0 es movimiento rápido, no dibuja, pero actualiza posición
          // No agregamos a currentPath, pero actualizamos la posición
        }
      }
      
      // Detectar comandos G1 (movimiento con láser encendido - dibuja)
      else if (trimmedLine.startsWith('G1') && currentLayer) {
        const xMatch = trimmedLine.match(/X([\d.-]+)/);
        const yMatch = trimmedLine.match(/Y([\d.-]+)/);
        
        if (xMatch && yMatch) {
          const x = parseFloat(xMatch[1]);
          const y = parseFloat(yMatch[1]);
          const z = currentLayer.layer * lineHeight;
          
          currentPath.push({ x, y, z });
        }
      }
      
      // Detectar fin de capa (M5 - apagar láser)
      else if (trimmedLine.startsWith('M5') && currentLayer) {
        // Guardar el path actual si tiene puntos
        if (currentPath.length > 0) {
          if (currentLayer.paths.length === 0) {
            // Si es el primer path de la capa, crear nuevo array
            currentLayer.paths = [...currentPath];
          } else {
            // Agregar al path existente
            currentLayer.paths.push(...currentPath);
          }
        }
        currentPath = [];
      }
    }
    
    // Agregar la última capa si existe
    if (currentLayer) {
      if (currentPath.length > 0) {
        if (currentLayer.paths.length === 0) {
          currentLayer.paths = [...currentPath];
        } else {
          currentLayer.paths.push(...currentPath);
        }
      }
      if (currentLayer.paths.length > 0) {
        parsedLayers.push(currentLayer);
      }
    }
    
    return parsedLayers;
  };

  // Efecto para parsear el G-code cuando cambie
  useEffect(() => {
    if (gcodeData) {
      setIsLoading(true);
      try {
        const parsedLayers = parseGCode(gcodeData);
        setLayers(parsedLayers);
      } catch (error) {
        console.error('Error parsing G-code:', error);
      } finally {
        setIsLoading(false);
      }
    }
  }, [gcodeData, lineHeight]);

  const maxZ = layers.length * lineHeight;

  // Combinar todos los puntos de todas las capas para calcular límites
  const allPaths = React.useMemo(() => {
    const paths: { x: number; y: number }[] = [];
    layers.forEach(layer => {
      layer.paths.forEach(path => {
        paths.push({ x: path.x, y: path.y });
      });
    });
    return paths;
  }, [layers]);

  // Calcular los límites del grabado para ajustar el tamaño del plano
  const engravingBounds = React.useMemo(() => {
    if (allPaths.length === 0) {
      return { minX: 0, maxX: tableWidth, minY: 0, maxY: tableHeight };
    }
    
    // Optimización: calcular límites sin crear arrays intermedios
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    
    for (const point of allPaths) {
      if (!isNaN(point.x) && !isNaN(point.y)) {
        minX = Math.min(minX, point.x);
        maxX = Math.max(maxX, point.x);
        minY = Math.min(minY, point.y);
        maxY = Math.max(maxY, point.y);
      }
    }
    
    // Si no hay puntos válidos, usar dimensiones de tabla
    if (minX === Infinity) {
      return { minX: 0, maxX: tableWidth, minY: 0, maxY: tableHeight };
    }
    
    return { minX, maxX, minY, maxY };
  }, [allPaths, tableWidth, tableHeight]);

  return (
    <div style={{ width: '100%', height: '500px', border: '1px solid #ccc', borderRadius: '8px' }}>
      {/* Información de la vista previa */}
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f5f5f5', 
        borderBottom: '1px solid #ccc',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <strong>Vista Previa del Grabado</strong>
          {layers.length > 0 && (
            <span style={{ marginLeft: '10px', color: '#666', fontSize: '14px' }}>
              {layers.reduce((sum, layer) => sum + layer.paths.length, 0)} puntos de grabado
            </span>
          )}
        </div>
        {isLoading && (
          <span style={{ color: '#1976d2', fontSize: '14px' }}>
            Cargando vista previa...
          </span>
        )}
      </div>

      {/* Canvas 3D */}
      <Canvas
        camera={{ 
          position: [
            Math.max(tableWidth, (engravingBounds.maxX - engravingBounds.minX) + 40) / 2, 
            Math.max(tableHeight, (engravingBounds.maxY - engravingBounds.minY) + 40) / 2, 
            Math.max(maxZ + 20, 50)
          ], 
          fov: 50,
          up: [0, 0, 1] // Z hacia arriba (como CNCjs)
        }}
        style={{ width: '100%', height: 'calc(100% - 50px)' }}
      >
        {/* Iluminación mejorada */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 10]} intensity={1.0} />
        <directionalLight position={[-10, -10, 5]} intensity={0.5} />
        <pointLight position={[0, 0, maxZ + 10]} intensity={0.8} />
        
        {/* Controles de órbita - centrado en el origen (esquina inferior izquierda) */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={20}
          maxDistance={200}
          target={[
            Math.max(tableWidth, (engravingBounds.maxX - engravingBounds.minX) + 40) / 2, 
            Math.max(tableHeight, (engravingBounds.maxY - engravingBounds.minY) + 40) / 2, 
            0
          ]}
          autoRotate={false}
        />
        
        {/* Tabla */}
        <TableMesh 
          width={tableWidth} 
          height={tableHeight} 
          engravingBounds={engravingBounds}
        />
        
        {/* Grabado final */}
        <EngravingMesh
          allPaths={allPaths}
          tableWidth={tableWidth}
          tableHeight={tableHeight}
          lineHeight={lineHeight}
        />
        
        {/* Etiquetas de ejes */}
        <AxisLabels 
          tableWidth={Math.max(tableWidth, (engravingBounds.maxX - engravingBounds.minX) + 40)} 
          tableHeight={Math.max(tableHeight, (engravingBounds.maxY - engravingBounds.minY) + 40)} 
          maxZ={maxZ} 
        />
      </Canvas>
      
      {/* Información de la vista previa */}
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f9f9f9', 
        borderTop: '1px solid #ccc',
        fontSize: '12px',
        color: '#666'
      }}>
        <strong>Controles:</strong> 
        {layers.length > 0 ? (
          <span>
            {' '}Arrastra para rotar • Rueda del mouse para zoom • Click derecho + arrastrar para mover
          </span>
        ) : (
          <span> Genera G-code para ver la vista previa</span>
        )}
      </div>
    </div>
  );
};

export default GCodePreview3D;
