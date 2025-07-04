class FocusAnalyzer:
    """
    Analyzes head pose angles to determine the user's focus state.

    This class uses a rule-based system to classify attention based on yaw, pitch,
    and roll values. The thresholds for these rules can be easily tuned.
    """

    # THIS IS THE FIX:
    # The STATE_MAPPING dictionary is now part of the class, making it
    # accessible to other files that import and use this class.
    STATE_MAPPING = {
        "No Face Detected": 0,
        "Focused": 1,
        "Distracted - Looking Left": 2,
        "Distracted - Looking Right": 3,
        "Looking Down": 4,
        "Distracted - Looking Up": 5
    }

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
            str: A string describing the user's focus state.
        """
        if angles is None:
            return "No Face Detected"

        yaw, pitch, _ = angles

        if yaw > self.yaw_threshold:
            return "Distracted - Looking Right"
        elif yaw < -self.yaw_threshold:
            return "Distracted - Looking Left"
        elif pitch > self.pitch_threshold_pos:
            return "Distracted - Looking Up"
        elif pitch < self.pitch_threshold_neg:
            return "Looking Down"
        else:
            return "Focused"
