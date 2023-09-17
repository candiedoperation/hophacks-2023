import * as React from 'react';
import { Card, CardContent, CardHeader } from "@mui/material";

const GraphCardRegion = (props) => {
    React.useEffect(() => { console.log(props); });
    return(
        <Card sx={{ flexGrow: 1, margin: '5px', height: '300px' }}>
            <CardHeader title={props.title} />
            <CardContent sx={{ padding: '0px', height: 'calc(100% - 64px)' }}>
                {props.children}
            </CardContent>
        </Card>
    );
}

export default GraphCardRegion;