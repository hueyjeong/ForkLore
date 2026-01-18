import { MapLayer, MapObject, ObjectType } from '@/types/maps.types';
import { Circle, Marker, Polygon, Polyline, Popup, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { Fragment } from 'react';

interface MapLayersProps {
  layers: MapLayer[];
  onObjectClick?: (object: MapObject) => void;
}

// Helper to parse coordinates
// Assuming coordinates are stored as { lat: number, lng: number } or { latlngs: ... } or similar
// This might need adjustment based on actual data structure
const getLatLng = (coords: unknown): L.LatLngExpression | null => {
  if (Array.isArray(coords) && coords.length === 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
    return coords as L.LatLngTuple;
  }
  if (typeof coords === 'object' && coords !== null) {
    const c = coords as { lat?: unknown; lng?: unknown };
    if (typeof c.lat === 'number' && typeof c.lng === 'number') {
      return [c.lat, c.lng];
    }
  }
  return null;
};

const getLatLngs = (coords: unknown): L.LatLngExpression[] | L.LatLngExpression[][] | null => {
  if (Array.isArray(coords)) {
    // Check if it's simple array of points or array of arrays
    return coords as L.LatLngExpression[];
  }
  return null;
};

const getCircleOptions = (
  coords: unknown
): { center: L.LatLngExpression; radius: number } | null => {
  const c = coords as { center?: unknown; radius?: unknown };
  const center = getLatLng(c?.center || c);
  const radius = c?.radius;
  if (center && typeof radius === 'number') {
    return { center, radius };
  }
  return null;
};

export function MapLayers({ layers, onObjectClick }: MapLayersProps) {
  // Sort layers by z_index
  const sortedLayers = [...layers].sort((a, b) => a.z_index - b.z_index);

  return (
    <>
      {sortedLayers.map((layer) => {
        if (!layer.is_visible) return null;

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
  const { object_type, coordinates, style_json, label, description } = object;
  const eventHandlers = {
    click: () => onObjectClick?.(object),
  };
  
  // Default path options from style_json
  const pathOptions: L.PathOptions = style_json as L.PathOptions || {};

  switch (object_type) {
    case ObjectType.POINT:
    case ObjectType.ICON: {
      const position = getLatLng(coordinates);
      if (!position) return null;
      
      // For now using default icon. Custom icons would need more logic based on style_json or object props.
      // If it's an ICON type, we might want to look for an iconUrl in style_json
      let icon = undefined;
      if (object_type === ObjectType.ICON && style_json?.iconUrl) {
          icon = L.icon({
              iconUrl: style_json.iconUrl as string,
              iconSize: (style_json.iconSize as L.PointTuple) || [25, 41],
              iconAnchor: (style_json.iconAnchor as L.PointTuple) || [12, 41],
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
