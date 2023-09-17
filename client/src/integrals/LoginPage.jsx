import * as React from 'react';
import * as faceapi from 'face-api.js';
import { Box } from '@mui/material';

const LoginPage = () => {
    const MODEL_URL = '/auth/models' //model directory
    const [capturedImage, setCapturedImage] = React.useState(null);

    React.useEffect(() => {
        
    }, []);

    const faceDetection = async () => {
        await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
        await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
        await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);

        let faceDescriptions = await faceapi.detectAllFaces(capturedImage).withFaceLandmarks().withFaceDescriptors().withFaceExpressions()
        const canvas = document.getElementById("reflay");
        faceapi.matchDimensions(canvas, capturedImage);

        faceDescriptions = faceapi.resizeResults(faceDescriptions, capturedImage);
        faceapi.draw.drawDetections(canvas, faceDescriptions);
        faceapi.draw.drawFaceLandmarks(canvas, faceDescriptions);
        faceapi.draw.drawFaceExpressions(canvas, faceDescriptions);
    };

    const handleCapture = async () => {
        try {
            // Access the user's camera
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });

            // Create a video element to display the camera stream
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Wait for the video to be ready
            video.onloadedmetadata = async () => {
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
                faceDetection();
            };
        } catch (error) {
            console.error('Error capturing image:', error);
        }
    };

    return (
        <Box sx={{ width: '100%', height: '100%' }}>
            <div>
                <button onClick={handleCapture}>Capture Face</button>
                {capturedImage && <img src={capturedImage} alt="Captured Face" />}
                {/* Your React component rendering code */}
                <canvas id="reflay" />
            </div>
        </Box>
    )
}

export default LoginPage;