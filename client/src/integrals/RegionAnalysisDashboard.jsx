import { Alert, Box, Card, Divider, Typography } from '@mui/material';
import * as React from 'react';
import { useLocation, useParams } from "react-router-dom";
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import AirMoleculesRegion from '../components/AirMoleculesRegion';
import axios from 'axios';

const RegionAnalysisDashboard = (props) => {
    const params = useParams();
    const [aiResponse, setAiResponse] = React.useState("");
    const [intrestLat, setInterestLat] = React.useState(null);
    const [intrestLong, setInterestLong] = React.useState(null);

    React.useEffect(() => {
        let latlong = params.loc.split(",");
        setInterestLat(latlong[0]);
        setInterestLong(latlong[1]);
    }, []);

    React.useEffect(() => {
        if (intrestLat != null && intrestLong != null) {
            axios
                .get(`http://10.195.144.63:5000/req?lat=${intrestLat}&long=${intrestLong}`)
                .then((res) => {
                    setAiResponse(res.data);
                });
        }
    }, [intrestLat, intrestLong]);

    var jsonData = {
        "air_quality": {
            "NO2_column_number_density": 0.0001508656407695222,
            "O3_column_number_density": 0.12677404381645405,
            "SO2_column_number_density": 4.043943617535412e-05,
            "CO_column_number_density": 0.04222102570043519
        }
    };

    return (
        <Box sx={{ height: "100%" }}>
            <Alert sx={{ margin: '10px' }} severity='info'>Viewing Information for <strong>{`${intrestLat}°, ${intrestLong}°`}</strong> Latitudes and Longitudes</Alert>
            <Box sx={{ display: 'flex', flexDirection: 'row', height: '100%' }}>
                <Box sx={{ margin: '10px', display: 'flex', flexWrap: 'wrap', flexGrow: 1, height: '100%' }}>
                    <AirMoleculesRegion data={jsonData} />
                    <AirMoleculesRegion data={jsonData} />
                    <AirMoleculesRegion data={jsonData} />
                </Box>
                <Divider flexItem orientation='vertical' />
                <Box sx={{ width: '450px', height: '100%' }}>
                    <Box sx={{ padding: '0px 10px 0px 10px', display: 'flex', alignItems: 'center', width: '100%' }}>
                        <TipsAndUpdatesIcon sx={{ height: '56px', marginRight: '10px' }} />
                        <Typography sx={{ fontWeight: '500' }} variant='h5'>AI Recommendations</Typography>
                    </Box>
                    <Divider />
                    <Typography variant='p'>{aiResponse}</Typography>
                </Box>
            </Box>
        </Box>
    );
}

export default RegionAnalysisDashboard;