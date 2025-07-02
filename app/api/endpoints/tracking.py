import cv2
import numpy as np
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from prometheus_client import Gauge, Counter

# Import the necessary classes from other parts of the application
from app.vision.head_pose import HeadPoseEstimator
from app.services.focus_analyzer import FocusAnalyzer
from app.core.config import settings

# --- Prometheus Custom Metrics ---
# Create Gauge metrics to hold the current value of the head pose angles.
# A Gauge is a metric that represents a single numerical value that can arbitrarily go up and down.
HEAD_POSE_YAW = Gauge('head_pose_yaw', 'Head pose Yaw angle in degrees')
HEAD_POSE_PITCH = Gauge('head_pose_pitch', 'Head pose Pitch angle in degrees')
HEAD_POSE_ROLL = Gauge('head_pose_roll', 'Head pose Roll angle in degrees')

# Create a Gauge for the focus state. We will use a numeric mapping.
# This allows us to graph the state over time easily.
FOCUS_STATE = Gauge('focus_state', 'Current focus state of the user', ['state'])

# Create a Counter for the total time spent in each state.
# A Counter is a cumulative metric that represents a single monotonically increasing counter.
FOCUS_STATE_SECONDS_TOTAL = Counter('focus_state_seconds_total', 'Total time in seconds for each focus state', ['state'])

# Mapping from string state to a numeric value for the gauge
STATE_MAPPING = {
    "No Face Detected": 0,
    "Focused": 1,
    "Distracted - Looking Left": 2,
    "Distracted - Looking Right": 3,
    "Looking Down": 4,
    "Distracted - Looking Up": 5
}

# Create an API router for this endpoint
router = APIRouter()

# Initialize the core components
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
    """
    await websocket.accept()
    print("WebSocket connection established.")

    try:
        while True:
            base64_data = await websocket.receive_text()

            try:
                header, encoded = base64_data.split(",", 1)
                image_data = base64.b64decode(encoded)
                np_arr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue
            except (ValueError, TypeError) as e:
                print(f"Error decoding image: {e}")
                continue

            _, angles = pose_estimator.estimate_pose(frame.copy())
            focus_state_str = focus_analyzer.analyze_focus(angles)

            # --- Update Prometheus Metrics ---
            if angles:
                yaw, pitch, roll = angles
                HEAD_POSE_YAW.set(yaw)
                HEAD_POSE_PITCH.set(pitch)
                HEAD_POSE_ROLL.set(roll)
            else:
                # If no face, set angles to 0 or a default value
                HEAD_POSE_YAW.set(0)
                HEAD_POSE_PITCH.set(0)
                HEAD_POSE_ROLL.set(0)
            
            # Update the focus state gauge with the numeric value
            numeric_state = STATE_MAPPING.get(focus_state_str, 0)
            # Set the gauge for the current state to 1, and all others to 0
            for state_name, state_num in STATE_MAPPING.items():
                FOCUS_STATE.labels(state=state_name).set(1 if state_num == numeric_state else 0)

            # Increment the counter for the current state.
            # We approximate the time per frame based on the FRAME_RATE.
            # Assuming FRAME_RATE is 10, each frame is ~0.1 seconds.
            FOCUS_STATE_SECONDS_TOTAL.labels(state=focus_state_str).inc(1.0 / 10) # Assumes 10 FPS

            # --- Prepare and Send Response to Frontend ---
            response_data = {
                "status": focus_state_str,
                "yaw": f"{angles[0]:.2f}" if angles else "N/A",
                "pitch": f"{angles[1]:.2f}" if angles else "N/A",
                "roll": f"{angles[2]:.2f}" if angles else "N/A"
            }
            await websocket.send_json(response_data)

    except WebSocketDisconnect:
        print("WebSocket connection closed by client.")
    except Exception as e:
        print(f"An error occurred in the WebSocket endpoint: {e}")
    finally:
        print("Cleaning up WebSocket resources.")
