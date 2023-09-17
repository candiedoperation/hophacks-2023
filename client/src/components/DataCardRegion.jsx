import { Box, Typography } from '@mui/material';
import * as React from 'react';
import GraphCardRegion from './GraphCardRegion';

const DataCardRegion = (props) => {
    return (
        <GraphCardRegion title={props.title}>
            <Box sx={{ padding: '0px 20px 0px 20px' }}>
                <Typography variant='h2' sx={{ marginBottom: '0px', paddingBottom: '0px' }}>{ props.primary }</Typography>
                <Typography variant='h5'>{ props.secondary }</Typography>
            </Box>
        </GraphCardRegion>
    );
}

export default DataCardRegion;