import math
import time

import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

THUMB_TIP = 4
INDEX_TIP = 8

FRAME_MARGIN_X = 120
FRAME_MARGIN_Y = 80

SMOOTHING = 0.45

PINCH_START_THRESHOLD = 30
PINCH_RELEASE_THRESHOLD = 50
DRAG_HOLD_TIME = 0.4


def landmark_to_pixel(landmark, frame_width, frame_height):
    x = int(landmark.x * frame_width)
    y = int(landmark.y * frame_height)
    return x, y


def calculate_distance(point_a, point_b):
    return math.hypot(
        point_b[0] - point_a[0],
        point_b[1] - point_a[1],
    )


def draw_hand(frame, landmarks):
    frame_height, frame_width, _ = frame.shape

    points = [
        landmark_to_pixel(
            landmark,
            frame_width,
            frame_height,
        )
        for landmark in landmarks
    ]

    for start, end in HAND_CONNECTIONS:
        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 255, 255),
            2,
        )

    for point in points:
        cv2.circle(
            frame,
            point,
            5,
            (0, 255, 0),
            -1,
        )

    return points


def move_cursor(
    index_point,
    frame_width,
    frame_height,
    screen_width,
    screen_height,
    previous_x,
    previous_y,
):
    active_width = frame_width - (2 * FRAME_MARGIN_X)
    active_height = frame_height - (2 * FRAME_MARGIN_Y)

    normalized_x = (
        index_point[0] - FRAME_MARGIN_X
    ) / active_width

    normalized_y = (
        index_point[1] - FRAME_MARGIN_Y
    ) / active_height

    normalized_x = max(0.0, min(normalized_x, 1.0))
    normalized_y = max(0.0, min(normalized_y, 1.0))

    cursor_x = int(
        normalized_x * (screen_width - 1)
    )

    cursor_y = int(
        normalized_y * (screen_height - 1)
    )

    smooth_x = int(
        previous_x
        + SMOOTHING * (cursor_x - previous_x)
    )

    smooth_y = int(
        previous_y
        + SMOOTHING * (cursor_y - previous_y)
    )

    pyautogui.moveTo(smooth_x, smooth_y)

    return smooth_x, smooth_y


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    screen_width, screen_height = pyautogui.size()

    previous_x = screen_width // 2
    previous_y = screen_height // 2

    is_pinching = False
    is_dragging = False
    pinch_start_time = 0.0

    base_options = python.BaseOptions(
        model_asset_path="hand_landmarker.task"
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7,
    )

    start_time = time.perf_counter()

    try:
        with vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                success, frame = camera.read()

                if not success:
                    print("Error: Could not read webcam frame.")
                    break

                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )

                timestamp_ms = int(
                    (time.perf_counter() - start_time) * 1000
                )

                result = detector.detect_for_video(
                    mp_image,
                    timestamp_ms,
                )

                frame_height, frame_width, _ = frame.shape

                cv2.rectangle(
                    frame,
                    (FRAME_MARGIN_X, FRAME_MARGIN_Y),
                    (
                        frame_width - FRAME_MARGIN_X,
                        frame_height - FRAME_MARGIN_Y,
                    ),
                    (255, 0, 0),
                    2,
                )

                status_text = "NO HAND"
                status_color = (0, 0, 255)

                if result.hand_landmarks:
                    hand_landmarks = result.hand_landmarks[0]
                    points = draw_hand(frame, hand_landmarks)

                    index_point = points[INDEX_TIP]
                    thumb_point = points[THUMB_TIP]

                    pinch_distance = calculate_distance(
                        thumb_point,
                        index_point,
                    )

                    cv2.circle(
                        frame,
                        index_point,
                        10,
                        (0, 0, 255),
                        -1,
                    )

                    cv2.circle(
                        frame,
                        thumb_point,
                        10,
                        (255, 0, 255),
                        -1,
                    )

                    cv2.line(
                        frame,
                        thumb_point,
                        index_point,
                        (0, 255, 255),
                        3,
                    )

                    current_time = time.perf_counter()

                    if (
                        not is_pinching
                        and pinch_distance < PINCH_START_THRESHOLD
                    ):
                        is_pinching = True
                        pinch_start_time = current_time

                    if is_pinching:
                        pinch_duration = (
                            current_time - pinch_start_time
                        )

                        # Release before moving the cursor.
                        if pinch_distance > PINCH_RELEASE_THRESHOLD:
                            if is_dragging:
                                pyautogui.mouseUp()
                                is_dragging = False
                                status_text = "DRAG RELEASED"
                                status_color = (0, 255, 0)
                            else:
                                pyautogui.click()
                                status_text = "CLICK"
                                status_color = (0, 255, 0)

                            is_pinching = False

                            # Keep the cursor locked at its current position
                            # on the release frame.
                            previous_x, previous_y = pyautogui.position()

                        else:
                            if (
                                not is_dragging
                                and pinch_duration >= DRAG_HOLD_TIME
                            ):
                                pyautogui.mouseDown()
                                is_dragging = True

                            if is_dragging:
                                previous_x, previous_y = move_cursor(
                                    index_point,
                                    frame_width,
                                    frame_height,
                                    screen_width,
                                    screen_height,
                                    previous_x,
                                    previous_y,
                                )

                                status_text = "DRAGGING"
                                status_color = (0, 165, 255)

                            else:
                                # Cursor remains locked while deciding
                                # between a click and a drag.
                                status_text = "PINCH - HOLD TO DRAG"
                                status_color = (0, 255, 255)

                    else:
                        previous_x, previous_y = move_cursor(
                            index_point,
                            frame_width,
                            frame_height,
                            screen_width,
                            screen_height,
                            previous_x,
                            previous_y,
                        )

                        status_text = "MOVE"
                        status_color = (255, 255, 255)

                    cv2.putText(
                        frame,
                        f"Pinch distance: {int(pinch_distance)}",
                        (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2,
                    )

                    if is_pinching and not is_dragging:
                        hold_progress = min(
                            (
                                current_time - pinch_start_time
                            ) / DRAG_HOLD_TIME,
                            1.0,
                        )

                        cv2.putText(
                            frame,
                            f"Hold: {hold_progress * 100:.0f}%",
                            (20, 105),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2,
                        )

                else:
                    if is_dragging:
                        pyautogui.mouseUp()

                    is_dragging = False
                    is_pinching = False

                cv2.putText(
                    frame,
                    status_text,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    status_color,
                    2,
                )

                cv2.imshow(
                    "Fingair Virtual Mouse",
                    frame,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        if is_dragging:
            pyautogui.mouseUp()

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()