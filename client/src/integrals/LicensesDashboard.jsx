import { Avatar, Box, Divider, List, ListItem, ListItemAvatar, ListItemText, Typography } from '@mui/material';
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
            { primary: 'ReactJS', secondary: 'react, react-dom, create-react-app' }
        ]);
    }, []);

    return (
        <Box sx={{ display: 'flex', width: '100%', height: '100%' }}>
            <Box sx={{ marginRight: '30px' }}><pre>{license}</pre></Box>
            <Divider orientation='vertical' />
            <Box sx={{ margin: '10px' }}>
                <Typography variant='h4'>Open Source Licenses</Typography>
                <List>
                    {
                        licenses.map((license, key) => (
                            <ListItem>
                                <ListItemAvatar sx={{ minWidth: '45px' }}><Avatar sx={{ bgcolor: 'text.primary', height: '32px', width: '32px' }}>{key + 1}</Avatar></ListItemAvatar>
                                <ListItemText primary={license.primary} secondary={license.secondary} />
                            </ListItem>
                        ))
                    }
                </List>
            </Box>
        </Box>
    );
}

export default LicensesDashboard;