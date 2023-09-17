import * as React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import GraphCardRegion from './GraphCardRegion';

const MapCardRegion = (props) => {
    return (
        <GraphCardRegion pb={true} mt={true} title="Aerial View">
            <MapContainer style={{ height: '100%' }} center={[props.lat, props.lng]} zoom={16} scrollWheelZoom={true}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                />
            </MapContainer>
        </GraphCardRegion>
    );
}

export default MapCardRegion;