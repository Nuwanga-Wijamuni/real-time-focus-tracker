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
HEAD_POSE_YAW = Gauge('head_pose_yaw', 'Head pose Yaw angle in degrees')
HEAD_POSE_PITCH = Gauge('head_pose_pitch', 'Head pose Pitch angle in degrees')
HEAD_POSE_ROLL = Gauge('head_pose_roll', 'Head pose Roll angle in degrees')

FOCUS_STATE = Gauge('focus_state', 'Current focus state of the user (numeric)')
FOCUS_STATE_SECONDS_TOTAL = Counter('focus_state_seconds_total', 'Total time in seconds for each focus state', ['state'])

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
                HEAD_POSE_YAW.set(0)
                HEAD_POSE_PITCH.set(0)
                HEAD_POSE_ROLL.set(0)
            
            numeric_state = focus_analyzer.STATE_MAPPING.get(focus_state_str, 0)
            FOCUS_STATE.set(numeric_state)

            FOCUS_STATE_SECONDS_TOTAL.labels(state=focus_state_str).inc(1.0 / 10)

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
