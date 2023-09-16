import { Alert } from '@mui/material';
import * as React from 'react';
import { useLocation, useParams } from "react-router-dom";

const RegionAnalysisDashboard = (props) => {
    const params = useParams();
    const [intrestLat, setInterestLat] = React.useState(0);
    const [intrestLong, setInterestLong] = React.useState(0);
    
    React.useEffect(() => {
        let latlong = params.loc.split(",");
        setInterestLat(latlong[0]);
        setInterestLong(latlong[1]);
    }, []);

    return(
        <Alert severity='info'>Viewing Information for <strong>{`${intrestLat}°, ${intrestLong}°`}</strong> Latitudes and Longitudes</Alert>
        
    );
}

export default RegionAnalysisDashboard;