/*
    Satellite Imagery Based Community Assistance (HopHacks 2023)
    Copyright (C) 2023  SIBCA Contributors

    SIBCA Contributors:
        Kushal Kapoor (kushalk@umd.edu)
        Atheesh Thirumalairajan (atheesh@umd.edu)
        Tanay Shah (tanay11@umd.edu)
        Krish Bhatt (kbhatt20@umd.edu)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

import * as React from 'react';
import { Alert, Autocomplete, Box, Button, Divider, Grid, ListItem, ListItemButton, ListItemIcon, ListItemText, TextField, Typography } from '@mui/material';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { getCurrentTheme } from '../middleware/AppThemeController';
import axios from 'axios';
import ExploreIcon from '@mui/icons-material/Explore';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import SatelliteAltIcon from '@mui/icons-material/SatelliteAlt';
import { useNavigate } from 'react-router-dom';

const WorldMapDashboard = (props) => {
    const navigate = useNavigate();
    const mapRef = React.useRef();
    const [regions, setRegions] = React.useState([]);
    const [selectedLL, setSelectedLL] = React.useState([-33.8688, 151.2093]);
    const [regionText, setRegionText] = React.useState("");

    const updateLoc = (regionSearch) => {
        axios
            .get(`https://geocoding-api.open-meteo.com/v1/search?name=${regionSearch}&count=8&language=en&format=json`)
            .then((res) => {
                if (res.data.results) setRegions((regions) => res.data.results);
                else setRegions([]);
            });
    }

    React.useEffect(() => {
        if (mapRef.current) {
            mapRef.current.on('click', (e) => {
                /* Refine Location */
                setSelectedLL((ll) => [e.latlng.lat.toFixed(6), e.latlng.lng.toFixed(6)]);
            });
        }
    }, [mapRef.current]);
    
    React.useEffect(() => {
        if (mapRef.current) {
            mapRef.current.setView(selectedLL, mapRef.current.getZoom());
        }
    }, [selectedLL]);

    const analyzeRegion = () => {
        navigate(`/region/${selectedLL[0]},${selectedLL[1]}`)
    }

    return (
        <Box sx={{ height: '100%', display: 'flex' }}>
            <Box sx={{ height: '100%', flexGrow: 1, filter: (getCurrentTheme() == "light") ? "" : "invert(1) hue-rotate(210deg)" }}>
                <MapContainer ref={mapRef} style={{ height: '100%' }} center={selectedLL} zoom={13} scrollWheelZoom={true}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    <Marker position={selectedLL}></Marker>
                </MapContainer>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', width: '300px', boxShadow: 8, zIndex: 1000 }}>
                <Box sx={{ padding: '0px 10px 0px 10px', display: 'flex', alignItems: 'center', width: '100%' }}>
                    <ExploreIcon sx={{ height: '56px', marginRight: '10px' }} />
                    <Typography sx={{ fontWeight: '500' }} variant='h5'>Navigator</Typography>
                </Box>
                <Divider />
                <Alert sx={{ margin: '10px' }} severity='info'>Select a Region, you can refine your location by pinning a point on the map.</Alert>
                <Autocomplete
                    sx={{ width: "100%", padding: '10px' }}
                    options={regions}
                    getOptionLabel={(option) => typeof option === 'string' ? option : `${option.name}, ${option.country}`}
                    filterOptions={(x) => x}
                    noOptionsText="No Regions"
                    filterSelectedOptions
                    autoComplete
                    includeInputInList
                    value={regionText}
                    onInputChange={(e, v) => { setRegionText(v); updateLoc(v); }}
                    onChange={(e, v) => { setRegionText(v); }}
                    renderInput={(params) => (<TextField {...params} label="Select Region" fullWidth />)}
                    renderOption={(props, option) => {
                        return (
                            <li {...props}>
                                <ListItem onClick={() => { setSelectedLL((ll) => [option.latitude, option.longitude]) }}>
                                    <ListItemIcon><LocationOnIcon sx={{ color: 'text.secondary' }} /></ListItemIcon>
                                    <ListItemText primary={`${option.name}, ${option.country}`} secondary={`${option.latitude}°, ${option.longitude}°`} />
                                </ListItem>
                            </li>
                        );
                    }}
                />
                <Box sx={{ padding: '0px 10px 0px 10px', display: 'flex', alignItems: 'center', width: '100%' }}>
                    <SatelliteAltIcon sx={{ height: '56px', marginRight: '10px' }} />
                    <Typography sx={{ fontWeight: '500' }} variant='h5'>Regional Analysis</Typography>
                </Box>
                <Divider />
                <Alert sx={{ margin: '10px' }} severity='info'>
                    {`Selected Latitudes, Longitudes are ${selectedLL[0]}° and ${selectedLL[1]}°`}
                </Alert>
                <Button onClick={() => { analyzeRegion(); }} sx={{ margin: '0px 10px 10px 10px' }} variant='contained'>Analyze Region</Button>
            </Box>
        </Box>
    );
}

export default WorldMapDashboard;