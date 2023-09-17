import { Alert, Box, Card, CircularProgress, Divider, Typography } from '@mui/material';
import * as React from 'react';
import { useLocation, useParams } from "react-router-dom";
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import AirMoleculesRegion from '../components/AirMoleculesRegion';
import axios from 'axios';
import GraphCardSkeleton from '../components/GraphCardSkeleton';
import TemperatureRangeRegion from '../components/TemperatureRangeRegion';
import DataCardRegion from '../components/DataCardRegion';
import MapCardRegion from '../components/MapCardRegion';

const RegionAnalysisDashboard = (props) => {
    const params = useParams();
    const [graphData, setGraphData] = React.useState("");
    const [aiResponse, setAiResponse] = React.useState("");
    const [isLoadingG, setIsLoadingG] = React.useState(true);
    const [isLoadingR, setIsLoadingR] = React.useState(true);
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
                    setIsLoadingR(false);
                    setAiResponse(res.data);
                });

            axios
                .get(`http://10.195.150.165:8000?lat=-33.8688&long=151.2093`)
                .then((res) => {
                    setTimeout(() => {
                        setIsLoadingG(false);
                        setGraphData(res.data);
                    }, 1000);
                })
        }
    }, [intrestLat, intrestLong]);

    return (
        <Box sx={{ height: "calc(100% - 125px)" }}>
            <Alert sx={{ margin: '10px' }} severity='info'>Viewing Information for <strong>{`${intrestLat}°, ${intrestLong}°`}</strong> Latitudes and Longitudes</Alert>
            <Box sx={{ display: 'flex', flexDirection: 'row', height: '100%', width: '100%' }}>
                <Box sx={{ margin: '10px', display: 'flex', flexWrap: 'wrap', width: '60%', height: '100%', overflowY: 'auto' }}>
                    {
                        (isLoadingG) ? <GraphCardSkeleton /> :
                            <>
                                <MapCardRegion lat={intrestLat} lng={intrestLong} />
                                <AirMoleculesRegion data={graphData.air_quality} />
                                <TemperatureRangeRegion data={[(graphData.maximum_2m_air_temperature - 273), (graphData.mean_2m_air_temperature - 273), (graphData.minimum_2m_air_temperature - 273)]} />
                                <DataCardRegion primary={graphData.elevation.toFixed(2)} secondary="Meters" title="Elevation" />
                                <DataCardRegion primary={graphData.SoilMoi0_10cm_inst.toFixed(2)} secondary="Wf/v" title="Soil Moisture" />
                                <DataCardRegion primary={graphData.precipitation.toFixed(2)*100} secondary="mm" title="Precipitation" />
                            </>
                    }
                </Box>
                <Divider flexItem orientation='vertical' />
                <Box sx={{ height: '100%', width: '40%' }}>
                    <Box sx={{ padding: '0px 10px 0px 10px', display: 'flex', alignItems: 'center', width: '100%' }}>
                        <TipsAndUpdatesIcon sx={{ height: '56px', marginRight: '10px' }} />
                        <Typography sx={{ fontWeight: '500' }} variant='h5'>Recommendations</Typography>
                    </Box>
                    <Divider />
                    <Box sx={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {
                            (isLoadingR) ? <CircularProgress /> : <Typography component="div" sx={{ padding: '25px', textAlign: 'justify', maxHeight: '100%', overflowY: 'auto' }} whiteSpace="pre-line" variant='p'>{aiResponse}</Typography>
                        }
                    </Box>
                </Box>
            </Box>
        </Box>
    );
}

export default RegionAnalysisDashboard;