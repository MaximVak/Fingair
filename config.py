# Hand landmark indexes
THUMB_TIP = 4
INDEX_TIP = 8

# Camera control area
FRAME_MARGIN_X = 120
FRAME_MARGIN_Y = 80

# Higher values are more responsive.
# Lower values are smoother.
SMOOTHING = 0.45

# Pinch gesture settings
PINCH_START_THRESHOLD = 30
PINCH_RELEASE_THRESHOLD = 50

# How long a pinch must be held before dragging starts
DRAG_HOLD_TIME = 0.3

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