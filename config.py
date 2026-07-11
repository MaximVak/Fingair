# Hand landmark indexes
THUMB_TIP = 4

INDEX_MCP = 5
INDEX_PIP = 6
INDEX_TIP = 8

MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_TIP = 12

RING_PIP = 14
RING_TIP = 16

PINKY_PIP = 18
PINKY_TIP = 20

# Camera control area
FRAME_MARGIN_X = 120
FRAME_MARGIN_Y = 80

# Higher values are more responsive.
# Lower values are smoother.
SMOOTHING = 0.45

# Left-click and drag settings
PINCH_START_THRESHOLD = 30
PINCH_RELEASE_THRESHOLD = 50
DRAG_HOLD_TIME = 0.3

# Right-click settings
RIGHT_CLICK_START_THRESHOLD = 30
RIGHT_CLICK_RELEASE_THRESHOLD = 50
RIGHT_CLICK_INDEX_SEPARATION = 55

# Scrolling settings
SCROLL_DIRECTION_THRESHOLD = 12
SCROLL_SENSITIVITY = 75
SCROLL_COOLDOWN = 0.04
SCROLL_THUMB_DISTANCE_THRESHOLD = 100

# Pause/resume open-hand gesture settings
PAUSE_HOLD_TIME = 0.6
OPEN_HAND_FINGER_MARGIN = 8
OPEN_HAND_THUMB_DISTANCE = 55

# MediaPipe settings
MODEL_PATH = "hand_landmarker.task"
MAX_HANDS = 1

MIN_HAND_DETECTION_CONFIDENCE = 0.7
MIN_HAND_PRESENCE_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    (0, 17),
]