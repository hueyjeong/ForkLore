import { MapLayer, MapObject, ObjectType } from '@/types/maps.types';
import { JsonValue } from '@/types/common';
import { Circle, Marker, Polygon, Polyline, Popup, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { Fragment } from 'react';

interface MapLayersProps {
  layers: MapLayer[];
  onObjectClick?: (object: MapObject) => void;
}

interface MapStyle extends L.PathOptions {
  iconUrl?: string;
  iconSize?: [number, number];
  iconAnchor?: [number, number];
}

const getLatLng = (coords: JsonValue): L.LatLngExpression | null => {
  if (Array.isArray(coords) && coords.length === 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
    return coords as L.LatLngTuple;
  }
  if (typeof coords === 'object' && coords !== null && !Array.isArray(coords)) {
    const c = coords as { lat?: number; lng?: number };
    if (typeof c.lat === 'number' && typeof c.lng === 'number') {
      return [c.lat, c.lng];
    }
  }
  return null;
};

const getLatLngs = (coords: JsonValue): L.LatLngExpression[] | L.LatLngExpression[][] | null => {
  if (Array.isArray(coords)) {
    return coords as L.LatLngExpression[];
  }
  return null;
};

const getCircleOptions = (
  coords: JsonValue
): { center: L.LatLngExpression; radius: number } | null => {
  const c = coords as { center?: JsonValue; radius?: number };
  const center = getLatLng(c?.center || c);
  const radius = c?.radius;
  if (center && typeof radius === 'number') {
    return { center, radius };
  }
  return null;
};

export function MapLayers({ layers, onObjectClick }: MapLayersProps) {
  const sortedLayers = [...layers].sort((a, b) => a.zIndex - b.zIndex);

  return (
    <>
      {sortedLayers.map((layer) => {
        if (!layer.isVisible) return null;

        return (
          <Fragment key={layer.id}>
            {layer.objects.map((obj) => (
              <RenderMapObject key={obj.id} object={obj} onObjectClick={onObjectClick} />
            ))}
          </Fragment>
        );
      })}
    </>
  );
}

function RenderMapObject({ object, onObjectClick }: { object: MapObject; onObjectClick?: (o: MapObject) => void }) {
  const { objectType, coordinates, styleJson, label, description } = object;
  const eventHandlers = {
    click: () => onObjectClick?.(object),
  };
  
  const pathOptions: L.PathOptions = (styleJson as MapStyle) || {};

  switch (objectType) {
    case ObjectType.POINT:
    case ObjectType.ICON: {
      const position = getLatLng(coordinates);
      if (!position) return null;
      
      let icon = undefined;
      const style = styleJson as MapStyle | null;
      if (objectType === ObjectType.ICON && style?.iconUrl) {
          icon = L.icon({
              iconUrl: style.iconUrl,
              iconSize: style.iconSize || [25, 41],
              iconAnchor: style.iconAnchor || [12, 41],
          });
      }

      return (
        <Marker position={position} icon={icon} eventHandlers={eventHandlers}>
          {label && <Tooltip>{label}</Tooltip>}
          {description && <Popup>{description}</Popup>}
        </Marker>
      );
    }

    case ObjectType.LINE: {
      const positions = getLatLngs(coordinates);
      if (!positions) return null;
      return (
        <Polyline positions={positions as L.LatLngExpression[]} pathOptions={pathOptions} eventHandlers={eventHandlers}>
           {label && <Tooltip sticky>{label}</Tooltip>}
           {description && <Popup>{description}</Popup>}
        </Polyline>
      );
    }

    case ObjectType.POLYGON: {
      const positions = getLatLngs(coordinates);
      if (!positions) return null;
      return (
        <Polygon positions={positions as L.LatLngExpression[]} pathOptions={pathOptions} eventHandlers={eventHandlers}>
           {label && <Tooltip sticky>{label}</Tooltip>}
           {description && <Popup>{description}</Popup>}
        </Polygon>
      );
    }

    case ObjectType.CIRCLE: {
      const options = getCircleOptions(coordinates);
      if (!options) return null;
      return (
        <Circle center={options.center} radius={options.radius} pathOptions={pathOptions} eventHandlers={eventHandlers}>
           {label && <Tooltip sticky>{label}</Tooltip>}
           {description && <Popup>{description}</Popup>}
        </Circle>
      );
    }

    default:
      return null;
  }
}
