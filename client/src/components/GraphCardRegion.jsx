import * as React from 'react';
import { Card, CardContent, CardHeader, Divider } from "@mui/material";

const GraphCardRegion = (props) => {
    return(
        <Card sx={{ flexGrow: 1, margin: '5px', height: '300px', minWidth: '300px' }}>
            <CardHeader title={props.title} />
            <Divider />
            <CardContent sx={{ marginTop: props.mt ? '0px' : '10px', paddingBottom: props.pb ? '0px !important' : '24px', padding: '0px', height: 'calc(100% - 64px)' }}>
                {props.children}
            </CardContent>
        </Card>
    );
}

export default GraphCardRegion;