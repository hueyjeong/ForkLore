'use client';

import { Map as MapData, MapObject } from '@/types/maps.types';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import type L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Dynamically import React Leaflet components to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);
const ImageOverlay = dynamic(
  () => import('react-leaflet').then((mod) => mod.ImageOverlay),
  { ssr: false }
);

// MapLayers also needs dynamic import as it depends on Leaflet
const MapLayers = dynamic(
  () => import('./map-layers').then((mod) => mod.MapLayers),
  { ssr: false }
);

interface MapViewerProps {
  mapData: MapData;
  onObjectSelect?: (object: MapObject | null) => void;
}

export function MapViewer({ mapData, onObjectSelect }: MapViewerProps) {
  const [leafletLib, setLeafletLib] = useState<typeof L | null>(null);

  useEffect(() => {
    // Import Leaflet on client side only
    import('leaflet').then((leaflet) => {
      // Fix for default marker icons in Next.js
      // We are using a simple fix here. In a real prod app, might want to serve these from public/
      const DefaultIcon = leaflet.Icon.Default;
      
      // Accessing private property to reset icon paths for Next.js compatibility
      delete (DefaultIcon.prototype as { _getIconUrl?: unknown })._getIconUrl;

      DefaultIcon.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      setLeafletLib(leaflet);
    });
  }, []);

  if (!leafletLib) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-muted/20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const snapshot = mapData.snapshot || mapData.snapshots?.[0];

  if (!snapshot) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-muted/20 text-muted-foreground">
        No map snapshot available
      </div>
    );
  }

  // Calculate bounds: [[0,0], [height, width]]
  // For CRS.Simple, we map the image 1:1 to map units.
  const bounds: [[number, number], [number, number]] = [
    [0, 0],
    [mapData.height, mapData.width],
  ];

  return (
    <div className="relative h-full w-full overflow-hidden rounded-md border shadow-sm">
      <MapContainer
        crs={leafletLib.CRS.Simple}
        bounds={bounds}
        center={[mapData.height / 2, mapData.width / 2]}
        zoom={-1}
        minZoom={-3}
        maxZoom={2}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', background: '#1a1a1a' }}
        attributionControl={false}
      >
        <ImageOverlay url={snapshot.baseImageUrl} bounds={bounds} />
        <MapLayers 
          layers={snapshot.layers} 
          onObjectClick={onObjectSelect} 
        />
      </MapContainer>
    </div>
  );
}
