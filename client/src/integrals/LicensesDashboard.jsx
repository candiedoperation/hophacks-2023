import { Avatar, Box, Divider, List, ListItem, ListItemAvatar, ListItemButton, ListItemText, Typography } from '@mui/material';
import * as React from 'react';

const LicensesDashboard = () => {
    const license = `
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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.`;

    /* OSS Lic List */
    const [licenses, setLicenses] = React.useState([]);
    React.useEffect(() => {
        setLicenses((lic) => [
            { primary: 'ReactJS', secondary: 'react, react-dom, create-react-app', link: "https://react.dev/" },
            { primary: 'MaterialUI', secondary: 'material-ui material-icons', link: "https://mui.com/" },
            { primary: 'Axios HTTP Client', secondary: 'axios', link: "https://axios-http.com/" },
            { primary: 'React Router', secondary: 'react-router', link: "https://reactrouter.com" },
            { primary: 'OpenMeteo API', secondary: 'Weather and Geodecoding APIs', link: "https://open-meteo.com" },
            { primary: 'Leaflet React', secondary: 'Leaflet, World Map API', link: "https://leafletjs.com/" },
            { primary: 'Google Maps and Earth Engine', secondary: 'Satellite Imagery, Regional Data', link: "https://earth.google.com/" },
        ]);
    }, []);

    return (
        <Box sx={{ display: 'flex', width: '100%', height: '100%' }}>
            <Box sx={{ marginRight: '30px' }}><pre>{license}</pre></Box>
            <Divider orientation='vertical' />
            <Box sx={{ margin: '10px', width: '100%' }}>
                <Typography variant='h4'>Dependencies</Typography>
                <List>
                    {
                        licenses.map((license, key) => (
                            <ListItemButton onClick={() => { window.open(license.link) }}>
                                <ListItemAvatar sx={{ minWidth: '45px' }}><Avatar sx={{ bgcolor: 'text.primary', height: '32px', width: '32px' }}>{key + 1}</Avatar></ListItemAvatar>
                                <ListItemText primary={license.primary} secondary={license.secondary} />
                            </ListItemButton>
                        ))
                    }
                </List>
            </Box>
        </Box>
    );
}

export default LicensesDashboard;