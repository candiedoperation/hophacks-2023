import SatelliteAlt from '@mui/icons-material/SatelliteAlt';
import { Button, Divider, Paper, TextField, Typography } from '@mui/material';
import { Box } from '@mui/system';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';

const RegionAnalysisRequest = () => {
    const navigate = useNavigate();
    const [latText, setLatText] = React.useState("");
    const [lngText, setLngText] = React.useState("");

    return (
        <Box sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            width: '100%'
        }}>
            <Paper elevation={8} sx={{
                height: '500px',
                width: { xs: '90%', md: '60%', lg: '50%' }
            }}>
                <Box sx={{ margin: '10px' , display: 'flex', alignItems: 'center', width: '100%' }}>
                    <SatelliteAlt sx={{ marginRight: '10px' }} />
                    <Typography sx={{ fontWeight: '500' }} variant='h5'>Analyze a Location</Typography>
                </Box>
                <Divider />
                <Box sx={{ width: '100%', height: '85%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <TextField value={latText} onChange={(e) => { setLatText(e.target.value); }} placeholder='Latitude' sx={{ width: '80%', padding: '5px' }} />
                    <TextField value={lngText} onChange={(e) => { setLngText(e.target.value); }} placeholder='Longitude' sx={{ width: '80%', padding: '5px' }} />
                    <Button
                        variant="contained"
                        onClick={() => { navigate(`/region/${latText},${lngText}`) }}
                        sx={{ width: '50%', marginTop: '10px' }}
                    >
                        Analyze Region
                    </Button>
                </Box>
            </Paper>
        </Box>
    );
}

export default RegionAnalysisRequest;