import cv2
import mediapipe as mp
import numpy as np

class HeadPoseEstimator:
    """
    A class to estimate head pose from an image using MediaPipe and OpenCV.

    This class encapsulates the logic for detecting facial landmarks and calculating
    the 3D head orientation (yaw, pitch, roll).
    """

    def __init__(self):
        """
        Initializes the HeadPoseEstimator.

        Sets up the MediaPipe Face Mesh model and defines the 3D model points
        of a canonical face required for pose estimation.
        """
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        # The 'with' statement is recommended for resource management
        # We will use it in the main processing loop instead of here
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # 3D model points of a generic human face.
        # These points are chosen because they are stable and easy to detect.
        # The origin (0, 0, 0) is the approximate center of the head.
        self.face_3d_model_points = np.array([
            [0.0, 0.0, 0.0],         # Nose tip
            [0.0, -330.0, -65.0],    # Chin
            [-225.0, 170.0, -135.0], # Left eye left corner
            [225.0, 170.0, -135.0],  # Right eye right corner
            [-150.0, -150.0, -125.0],# Left Mouth corner
            [150.0, -150.0, -125.0]  # Right mouth corner
        ])


    def estimate_pose(self, image):
        """
        Estimates the head pose from a single image frame.

        Args:
            image: A BGR image frame from OpenCV.

        Returns:
            A tuple containing:
            - The annotated image with the 3D pose axes drawn on it.
            - A tuple of (yaw, pitch, roll) angles in degrees. Returns None if no face is detected.
        """
        # Get the height and width of the image
        img_h, img_w, _ = image.shape
        focal_length = img_w
        cam_center = (img_w / 2, img_h / 2)

        # Camera matrix setup for the solvePnP algorithm
        camera_matrix = np.array([
            [focal_length, 0, cam_center[0]],
            [0, focal_length, cam_center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        # Assuming no lens distortion
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image to find face landmarks
        results = self.face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 2D image points corresponding to the 3D model points
                face_2d_image_points = np.array([
                    [face_landmarks.landmark[1].x * img_w, face_landmarks.landmark[1].y * img_h],      # Nose tip
                    [face_landmarks.landmark[152].x * img_w, face_landmarks.landmark[152].y * img_h],   # Chin
                    [face_landmarks.landmark[263].x * img_w, face_landmarks.landmark[263].y * img_h],   # Left eye left corner
                    [face_landmarks.landmark[33].x * img_w, face_landmarks.landmark[33].y * img_h],     # Right eye right corner
                    [face_landmarks.landmark[287].x * img_w, face_landmarks.landmark[287].y * img_h],   # Left Mouth corner
                    [face_landmarks.landmark[57].x * img_w, face_landmarks.landmark[57].y * img_h]      # Right mouth corner
                ], dtype=np.float64)

                # Solve for the pose (rotation and translation vectors)
                success, rotation_vector, translation_vector = cv2.solvePnP(
                    self.face_3d_model_points,
                    face_2d_image_points,
                    camera_matrix,
                    dist_coeffs
                )

                if success:
                    # Project 3D points to image plane for drawing the axes
                    axis_points_3d = np.array([
                        [50, 0, 0],
                        [0, 50, 0],
                        [0, 0, 50]
                    ], dtype=np.float64)

                    axis_points_2d, _ = cv2.projectPoints(
                        axis_points_3d,
                        rotation_vector,
                        translation_vector,
                        camera_matrix,
                        dist_coeffs
                    )

                    # Convert rotation vector to rotation matrix
                    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

                    # Decompose rotation matrix to get Euler angles
                    # This gives us yaw, pitch, and roll
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
                    
                    # Angles are in degrees. Adjust them for intuitive understanding.
                    # Yaw: Rotation around the Y-axis
                    # Pitch: Rotation around the X-axis
                    # Roll: Rotation around the Z-axis
                    yaw = angles[1]
                    pitch = angles[0]
                    roll = angles[2]

                    # Draw the 3D pose axes on the image
                    nose_tip_2d = (int(face_2d_image_points[0][0]), int(face_2d_image_points[0][1]))
                    
                    # Draw X-axis (Pitch) in Blue
                    cv2.line(image, nose_tip_2d, tuple(np.int32(axis_points_2d[0].ravel())), (255, 0, 0), 3)
                    # Draw Y-axis (Yaw) in Green
                    cv2.line(image, nose_tip_2d, tuple(np.int32(axis_points_2d[1].ravel())), (0, 255, 0), 3)
                    # Draw Z-axis (Roll) in Red
                    cv2.line(image, nose_tip_2d, tuple(np.int32(axis_points_2d[2].ravel())), (0, 0, 255), 3)
                    
                    return image, (yaw, pitch, roll)

        # If no face is detected, return the original image and None
        return image, None

    def close(self):
        """
        Releases the MediaPipe Face Mesh resources.
        """
        self.face_mesh.close()

# Example usage (for testing this module directly)
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    pose_estimator = HeadPoseEstimator()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Estimate the pose
        annotated_frame, angles = pose_estimator.estimate_pose(frame)

        if angles:
            yaw, pitch, roll = angles
            # Display the angles on the frame
            cv2.putText(annotated_frame, f"Yaw: {yaw:.2f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Pitch: {pitch:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Roll: {roll:.2f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Head Pose Estimation', annotated_frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # When everything done, release the capture and resources
    cap.release()
    cv2.destroyAllWindows()
    pose_estimator.close()