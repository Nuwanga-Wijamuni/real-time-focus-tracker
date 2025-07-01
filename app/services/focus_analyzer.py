class FocusAnalyzer:
    """
    Analyzes head pose angles to determine the user's focus state.

    This class uses a rule-based system to classify attention based on yaw, pitch,
    and roll values. The thresholds for these rules can be easily tuned.
    """

    def __init__(self, yaw_threshold=20, pitch_threshold_pos=20, pitch_threshold_neg=-15):
        """
        Initializes the FocusAnalyzer with customizable thresholds.

        Args:
            yaw_threshold (int): The angle (in degrees) for left/right head turns
                                 to be considered a distraction.
            pitch_threshold_pos (int): The angle (in degrees) for looking up to be
                                       considered a distraction.
            pitch_threshold_neg (int): The angle (in degrees) for looking down to be
                                       considered a distraction.
        """
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold_pos = pitch_threshold_pos
        self.pitch_threshold_neg = pitch_threshold_neg

    def analyze_focus(self, angles):
        """
        Classifies the focus state based on the provided head pose angles.

        Args:
            angles (tuple): A tuple containing (yaw, pitch, roll) in degrees.

        Returns:
            str: A string describing the user's focus state (e.g., "Focused",
                 "Distracted - Looking Left", "Looking Down"). Returns
                 "No Face Detected" if the input angles are None.
        """
        if angles is None:
            return "No Face Detected"

        yaw, pitch, _ = angles  # Roll is not used for focus state in this version

        # Check for left or right distractions based on the yaw angle
        if yaw > self.yaw_threshold:
            return "Distracted - Looking Right"
        elif yaw < -self.yaw_threshold:
            return "Distracted - Looking Left"
        
        # Check for up or down distractions based on the pitch angle
        elif pitch > self.pitch_threshold_pos:
            return "Distracted - Looking Up"
        elif pitch < self.pitch_threshold_neg:
            return "Looking Down"
        
        # If none of the distraction conditions are met, the user is focused
        else:
            return "Focused"

# Example usage (for testing this module directly)
if __name__ == '__main__':
    # Initialize the analyzer with default thresholds
    analyzer = FocusAnalyzer()

    # --- Test Cases ---

    # 1. Focused state
    focused_angles = (5, -5, 0)
    focus_state = analyzer.analyze_focus(focused_angles)
    print(f"Angles: {focused_angles} -> State: {focus_state}") # Expected: Focused

    # 2. Distracted - Looking Left
    distracted_left_angles = (-30, 0, 5)
    focus_state = analyzer.analyze_focus(distracted_left_angles)
    print(f"Angles: {distracted_left_angles} -> State: {focus_state}") # Expected: Distracted - Looking Left

    # 3. Distracted - Looking Right
    distracted_right_angles = (25, 5, -5)
    focus_state = analyzer.analyze_focus(distracted_right_angles)
    print(f"Angles: {distracted_right_angles} -> State: {focus_state}") # Expected: Distracted - Looking Right

    # 4. Looking Down
    looking_down_angles = (0, -25, 0)
    focus_state = analyzer.analyze_focus(looking_down_angles)
    print(f"Angles: {looking_down_angles} -> State: {focus_state}") # Expected: Looking Down
    
    # 5. Distracted - Looking Up
    looking_up_angles = (0, 25, 0)
    focus_state = analyzer.analyze_focus(looking_up_angles)
    print(f"Angles: {looking_up_angles} -> State: {focus_state}") # Expected: Distracted - Looking Up

    # 6. No face detected
    no_face = None
    focus_state = analyzer.analyze_focus(no_face)
    print(f"Angles: {no_face} -> State: {focus_state}") # Expected: No Face Detected
