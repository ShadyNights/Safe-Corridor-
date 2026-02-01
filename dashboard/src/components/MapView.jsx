import React from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapView = ({ path, currentPos, startPos, endPos }) => {
    const center = currentPos || startPos || [21.1458, 79.0882];

    return (
        <div className="h-full w-full rounded-lg overflow-hidden border border-slate-700">
            <MapContainer center={center} zoom={14} scrollWheelZoom={true} className="h-full w-full">
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {startPos && <Marker position={startPos}><Popup>Start</Popup></Marker>}
                {endPos && <Marker position={endPos}><Popup>End</Popup></Marker>}

                {path && path.length > 0 && (
                    <Polyline positions={path} color="blue" />
                )}

                {currentPos && (
                    <CircleMarker center={currentPos} radius={8} color="red" fillOpacity={0.8}>
                        <Popup>Current Location</Popup>
                    </CircleMarker>
                )}
            </MapContainer>
        </div>
    );
};

export default MapView;
