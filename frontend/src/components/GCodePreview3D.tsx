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
                  new THREE.Vector3(prevPoint.x, prevPoint.y, 1.0),
                  new THREE.Vector3(point.x, point.y, 1.0)
                ])}
                material={new THREE.LineBasicMaterial({ 
                  color: '#FFD700', // Color dorado brillante
                  linewidth: 12,
                  transparent: true,
                  opacity: 1.0
                })}
              />
              
              {/* Línea de sombra para dar profundidad */}
              <line
                geometry={new THREE.BufferGeometry().setFromPoints([
                  new THREE.Vector3(prevPoint.x, prevPoint.y, 0.7),
                  new THREE.Vector3(point.x, point.y, 0.7)
                ])}
                material={new THREE.LineBasicMaterial({ 
                  color: '#B8860B', // Color dorado oscuro para sombra
                  linewidth: 14,
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
              {/* Punto principal del grabado - en alto relieve */}
              <Box
                position={[point.x, point.y, 1.0]}
                args={[1.2, 1.2, 1.0]}
                material-color="#FFD700" // Color dorado brillante
                material-transparent
                material-opacity={1.0}
              />
              
              {/* Sombra del grabado */}
              <Box
                position={[point.x, point.y, 0.7]}
                args={[1.3, 1.3, 0.5]}
                material-color="#B8860B" // Color dorado oscuro
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
  
  // Líneas verticales
  for (let x = 0; x <= tableWidth; x += gridSize) {
    gridLines.push(
      <line
        key={`v-${x}`}
        geometry={new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(x, 0, 0),
          new THREE.Vector3(x, tableHeight, 0)
        ])}
        material={new THREE.LineBasicMaterial({ color: '#888888', opacity: 0.1, transparent: true })}
      />
    );
  }
  
  // Líneas horizontales
  for (let y = 0; y <= tableHeight; y += gridSize) {
    gridLines.push(
      <line
        key={`h-${y}`}
        geometry={new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, y, 0),
          new THREE.Vector3(tableWidth, y, 0)
        ])}
        material={new THREE.LineBasicMaterial({ color: '#888888', opacity: 0.1, transparent: true })}
      />
    );
  }
  
  return (
    <group>
      {/* Tabla base con textura de madera más clara */}
      <Box
        position={[tableWidth / 2, tableHeight / 2, -0.5]}
        args={[tableWidth, tableHeight, 1]}
        material-color="#D2B48C" // Color madera más claro
        material-transparent
        material-opacity={0.1} // Muy transparente
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
      <Text
        position={[tableWidth / 2, -3, 0]}
        fontSize={1.2}
        color="red"
        anchorX="center"
        anchorY="middle"
      >
        X
      </Text>
      
      <Text
        position={[-3, tableHeight / 2, 0]}
        fontSize={1.2}
        color="green"
        anchorX="center"
        anchorY="middle"
        rotation={[0, 0, Math.PI / 2]}
      >
        Y
      </Text>
      
      <Text
        position={[-3, -3, maxZ / 2]}
        fontSize={1.2}
        color="blue"
        anchorX="center"
        anchorY="middle"
        rotation={[0, 0, Math.PI / 2]}
      >
        Z
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
      
      // Detectar comandos G1 (movimiento con láser encendido)
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
      
      // Detectar fin de capa (M5)
      else if (trimmedLine === 'M5' && currentLayer) {
        if (currentPath.length > 0) {
          currentLayer.paths = [...currentPath];
          parsedLayers.push(currentLayer);
        }
        currentPath = [];
      }
    }
    
    // Agregar la última capa si existe
    if (currentLayer && currentPath.length > 0) {
      currentLayer.paths = [...currentPath];
      parsedLayers.push(currentLayer);
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
          position: [0, 0, maxZ + 20], 
          fov: 45,
          up: [0, 1, 0]
        }}
        style={{ width: '100%', height: 'calc(100% - 50px)' }}
      >
        {/* Iluminación mejorada */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[0, 0, 5]} intensity={0.8} />
        
        {/* Controles de órbita */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={10}
          maxDistance={100}
          target={[tableWidth / 2, tableHeight / 2, 0]}
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
