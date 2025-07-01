import cv2
import numpy as np
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Import the necessary classes from other parts of the application
from app.vision.head_pose import HeadPoseEstimator
from app.services.focus_analyzer import FocusAnalyzer
from app.core.config import settings

# Create an API router for this endpoint
router = APIRouter()

# Initialize the core components
# These will be shared across all WebSocket connections
pose_estimator = HeadPoseEstimator()
focus_analyzer = FocusAnalyzer(
    yaw_threshold=settings.YAW_THRESHOLD,
    pitch_threshold_pos=settings.PITCH_THRESHOLD_POS,
    pitch_threshold_neg=settings.PITCH_THRESHOLD_NEG
)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    The main WebSocket endpoint for real-time focus tracking.

    This function establishes a WebSocket connection, receives video frames from
    the client, processes them to determine focus state, and sends the
    results back to the client.

    Args:
        websocket (WebSocket): The WebSocket connection instance managed by FastAPI.
    """
    await websocket.accept()
    print("WebSocket connection established.")

    try:
        while True:
            # Receive data from the client (frontend)
            # The frontend will send the image frame as a base64 encoded string
            base64_data = await websocket.receive_text()

            # --- Image Decoding ---
            # The received data is a data URL (e.g., "data:image/jpeg;base64,...")
            # We need to strip the header to get the pure base64 string
            try:
                header, encoded = base64_data.split(",", 1)
                image_data = base64.b64decode(encoded)
                
                # Convert the binary image data to a NumPy array
                np_arr = np.frombuffer(image_data, np.uint8)
                
                # Decode the NumPy array into an OpenCV image
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    print("Warning: Received empty frame.")
                    continue

            except (ValueError, TypeError) as e:
                print(f"Error decoding image: {e}")
                continue

            # --- Pose Estimation and Focus Analysis ---
            # Use the HeadPoseEstimator to get the angles
            # We pass a copy of the frame to avoid modifying the original
            _, angles = pose_estimator.estimate_pose(frame.copy())

            # Use the FocusAnalyzer to get the focus state
            focus_state = focus_analyzer.analyze_focus(angles)

            # --- Prepare and Send Response ---
            response_data = {
                "status": focus_state,
                "yaw": f"{angles[0]:.2f}" if angles else "N/A",
                "pitch": f"{angles[1]:.2f}" if angles else "N/A",
                "roll": f"{angles[2]:.2f}" if angles else "N/A"
            }

            # Send the JSON data back to the client
            await websocket.send_json(response_data)

    except WebSocketDisconnect:
        print("WebSocket connection closed by client.")
    except Exception as e:
        print(f"An error occurred in the WebSocket endpoint: {e}")
    finally:
        # Although FastAPI handles closing, this is a good place for any
        # additional cleanup if needed.
        print("Cleaning up WebSocket resources.")
