import { Box, Skeleton } from '@mui/material';
import * as React from 'react';

const GraphCardSkeletonIn = () => {
    return (
        <Box sx={{ flexGrow: 1, margin: '5px' }}>
            <Skeleton height="40px" variant='linear' sx={{ marginBottom: '10px', borderRadius: '10px' }}></Skeleton>
            <Skeleton height="250px" width="100%" variant='rectangular' sx={{ borderRadius: '5px' }}></Skeleton>
        </Box>
    );
}

const GraphCardSkeleton = (props) => {
    return (
        <>
            <GraphCardSkeletonIn />
            <GraphCardSkeletonIn />
        </>
    )
}

export default GraphCardSkeleton;