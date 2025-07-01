document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    // Get references to all the HTML elements we'll need to interact with.
    const video = document.getElementById('webcam');
    const webcamStatus = document.getElementById('webcam-status');
    const statusElement = document.getElementById('status');
    const yawElement = document.getElementById('yaw');
    const pitchElement = document.getElementById('pitch');
    const rollElement = document.getElementById('roll');

    // --- Configuration ---
    // The URL for the WebSocket server. This should match your backend configuration.
    // Make sure to use 'ws://' for non-secure and 'wss://' for secure connections.
    const WEBSOCKET_URL = 'ws://localhost:8000/api/v1/ws';
    const FRAME_RATE = 10; // Send 10 frames per second for analysis.

    let socket;
    let intervalId;

    /**
     * Initializes and starts the user's webcam.
     */
    async function startWebcam() {
        try {
            // Request access to the user's camera.
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            });
            // If access is granted, set the video element's source to the stream.
            video.srcObject = stream;
            webcamStatus.textContent = 'Webcam connected successfully.';
            webcamStatus.style.color = '#2dd4bf'; // Teal color for success
            
            // Once the video starts playing, connect to the WebSocket.
            video.onloadedmetadata = () => {
                connectWebSocket();
            };

        } catch (error) {
            // If there's an error (e.g., user denies access), display a message.
            console.error('Error accessing webcam:', error);
            webcamStatus.textContent = 'Could not access webcam. Please grant permission.';
            webcamStatus.style.color = '#f87171'; // Red color for error
        }
    }

    /**
     * Establishes a connection to the WebSocket server.
     */
    function connectWebSocket() {
        console.log('Attempting to connect to WebSocket...');
        socket = new WebSocket(WEBSOCKET_URL);

        // --- WebSocket Event Handlers ---

        // Called when the connection is successfully opened.
        socket.onopen = () => {
            console.log('WebSocket connection opened.');
            statusElement.textContent = 'Connected';
            updateStatusClass('status-default');
            
            // Start sending frames to the backend at the specified frame rate.
            intervalId = setInterval(sendFrame, 1000 / FRAME_RATE);
        };

        // Called when a message is received from the server.
        socket.onmessage = (event) => {
            // Parse the JSON data received from the backend.
            const data = JSON.parse(event.data);
            
            // Update the UI elements with the new data.
            statusElement.textContent = data.status;
            yawElement.textContent = data.yaw;
            pitchElement.textContent = data.pitch;
            rollElement.textContent = data.roll;
            
            // Update the color of the status text based on the focus state.
            if (data.status.includes('Distracted') || data.status.includes('Looking')) {
                updateStatusClass('status-distracted');
            } else if (data.status === 'Focused') {
                updateStatusClass('status-focused');
            } else {
                updateStatusClass('status-default');
            }
        };

        // Called when the connection is closed.
        socket.onclose = () => {
            console.log('WebSocket connection closed.');
            statusElement.textContent = 'Disconnected';
            updateStatusClass('status-default');
            // Stop sending frames when the connection is closed.
            clearInterval(intervalId);
            // Optional: Try to reconnect after a delay.
            setTimeout(connectWebSocket, 5000); 
        };

        // Called when an error occurs.
        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            statusElement.textContent = 'Connection Error';
            updateStatusClass('status-default');
            clearInterval(intervalId);
        };
    }

    /**
     * Captures a frame from the video, converts it to base64, and sends it.
     */
    function sendFrame() {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Create a temporary canvas to draw the video frame on.
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert the canvas image to a base64 encoded JPEG data URL.
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8); // 0.8 quality for smaller size

            // Send the data URL to the WebSocket server.
            socket.send(dataUrl);
        }
    }
    
    /**
     * Updates the CSS class of the status element for visual feedback.
     * @param {string} newClass - The new CSS class to apply.
     */
    function updateStatusClass(newClass) {
        statusElement.className = 'text-5xl font-bold transition-colors duration-300'; // Reset classes
        statusElement.classList.add(newClass);
    }

    // --- Start the Application ---
    // Kick everything off by starting the webcam.
    startWebcam();
});