import * as React from 'react';
import { Box, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginPage = () => {
    const navigate = useNavigate();
    const [capturedImage, setCapturedImage] = React.useState(null);

    React.useEffect(() => {
        initCapture();
    }, []);

    const uploadFace = () => {
        axios
            .post('http://10.195.150.165:8000/im_size', { image: capturedImage })
            .then((res) => {
                if (res.data.status == true) {
                    sessionStorage.setItem("auth", "true");
                } else {
                    let username = window.prompt("Enter Username to Sign Up...");
                    axios
                        .post('http://10.195.150.165:8000/signup', { image: capturedImage, username })
                        .then((res) => {
                            if (res.data.status == true) {
                                sessionStorage.setItem("auth", "true");
                                navigate("/");
                            } else {
                                /* Notify Error */
                                alert("Face enrollment Failed...")
                            }
                        })
                }
            })
    };

    const captureFace = () => {
        const video = document.getElementById("facestream");
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Capture a frame from the video stream and draw it on the canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert the canvas content to a data URL (image) and set it in the state
        const imageDataURL = canvas.toDataURL('image/jpeg');
        setCapturedImage(imageDataURL);

        // Run Face Detect
        uploadFace();
    }

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
                

                // Run Face Detect
                uploadFace();
            };*/
        } catch (error) {
            console.error('Error capturing image:', error);
        }
    };

    return (
        <>
            <Box sx={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Paper elevation={3} sx={{ display: 'flex', flexDirection: 'column', width: '40%', height: '70%', alignItems: 'center', justifyContent: 'center' }}>
                    <Box sx={{ border: '3px solid green', boxShadow: 5, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '300px', height: "300px", objectFit: 'cover', borderRadius: '50%' }}>
                        <video style={{ transform: 'scaleX(-1)' }} id="facestream" />
                    </Box>
                    <Button onClick={() => { captureFace(); }} variant="contained" sx={{ marginTop: '35px' }}>Login with Face Recognition</Button>
                </Paper>
            </Box>
        </>
    )
}

export default LoginPage;