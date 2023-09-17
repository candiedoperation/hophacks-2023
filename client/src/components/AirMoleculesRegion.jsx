import * as React from 'react';
import { PolarArea } from 'react-chartjs-2';
import 'chart.js/auto';
import GraphCardRegion from './GraphCardRegion';

const AirMoleculesRegion = (props) => {
    React.useEffect(() => {console.warn(props)}, []);
    return (
        (props.data) ?
        <GraphCardRegion title="Air Pollutant Distribution">
            <PolarArea
                style={{ maxWidth: '100%' }}
                data={{
                    labels: Object.keys(props.data).map((x) => x.split("_")[0]),
                    datasets: [{
                        data: Object.values(props.data),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)', // Red for NO2
                            'rgba(54, 162, 235, 0.5)', // Blue for O3
                            'rgba(255, 206, 86, 0.5)', // Yellow for SO2
                            'rgba(75, 192, 192, 0.5)' // Green for CO
                        ],
                    }]
                }}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Air Molecule Data'
                    }
                }}
            />
        </GraphCardRegion> : <></>
    );
}

export default AirMoleculesRegion;