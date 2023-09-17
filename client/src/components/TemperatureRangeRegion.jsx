import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import GraphCardRegion from './GraphCardRegion';

const TemperatureRangeRegion = (props) => {
    return (
        (props.data) ?
            <GraphCardRegion title="Temperatures">
                <Bar
                    style={{ maxWidth: '100%' }}
                    data={{
                        labels: ["Maximum", "Mean", "Minimum"],
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: [props.data[0], props.data[1], props.data[2]],
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)', // Maximum temperature color
                                'rgba(54, 162, 235, 0.6)', // Minimum temperature color
                                'rgba(255, 205, 86, 0.6)'  // Mean temperature color
                            ],
                            borderWidth: 1,
                        }]
                    }}
                    options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: 'Temperatures'
                        }
                    }}
                />
            </GraphCardRegion> : <></>
    );
}

export default TemperatureRangeRegion;