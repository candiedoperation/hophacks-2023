import * as React from 'react';
import { Box, Paper } from '@mui/material';
import axios from 'axios';

const LoginPage = () => {
    const [capturedImage, setCapturedImage] = React.useState(null);

    React.useEffect(() => {
        initCapture();
    }, []);

    const uploadFace = () => {
        axios
            .post('http://10.195.150.165:8000/im_size', { image: capturedImage })
            .then((res) => {
                console.log(res.data);
            })
    };

    const initCapture = async () => {
        try {
            // Access the user's camera
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });

            // Create a video element to display the camera stream
            const video = document.getElementById("facestream");
            video.srcObject = stream;
            video.play();

            // Wait for the video to be ready
            /*video.onloadedmetadata = async () => {
                // Create a canvas element to capture the image
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Capture a frame from the video stream and draw it on the canvas
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Convert the canvas content to a data URL (image) and set it in the state
                const imageDataURL = canvas.toDataURL('image/jpeg');
                setCapturedImage(imageDataURL);

                // Stop the camera stream
                stream.getTracks().forEach((track) => track.stop());

                // Remove the video and canvas elements
                video.remove();
                canvas.remove();

                // Run Face Detect
                uploadFace();
            };*/
        } catch (error) {
            console.error('Error capturing image:', error);
        }
    };

    return (
        <>
            <Box sx={{ bgcolor: 'green', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Paper elevation={3} sx={{ display: 'flex', flexDirection: 'column', width: '40%', height: '70%' }}>
                    <Box sx={{ overflow: 'hidden' }}>
                        <video id="facestream" />
                    </Box>
                </Paper>
            </Box>
            <div>
                <button onClick={initCapture}>Capture Face</button>
                {capturedImage && <img src={capturedImage} alt="Captured Face" />}
            </div>
        </>
    )
}

export default LoginPage;