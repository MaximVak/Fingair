import time

import cv2

from config import (
    FRAME_MARGIN_X,
    FRAME_MARGIN_Y,
)
from cursor_controller import CursorController
from gesture_controller import GestureController
from hand_tracker import HandTracker


def draw_gesture_feedback(frame, gesture_result):
    index_point = gesture_result["index_point"]
    thumb_point = gesture_result["thumb_point"]

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

    cv2.putText(
        frame,
        (
            "Pinch distance: "
            f"{int(gesture_result['pinch_distance'])}"
        ),
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    hold_progress = gesture_result["hold_progress"]

    if hold_progress is not None:
        cv2.putText(
            frame,
            f"Hold: {hold_progress * 100:.0f}%",
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    hand_tracker = HandTracker()
    cursor_controller = CursorController()
    gesture_controller = GestureController()

    start_time = time.perf_counter()

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Error: Could not read webcam frame.")
                break

            frame = cv2.flip(frame, 1)

            timestamp_ms = int(
                (time.perf_counter() - start_time) * 1000
            )

            landmarks = hand_tracker.detect(
                frame,
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

            if landmarks:
                points = hand_tracker.draw_hand(
                    frame,
                    landmarks,
                )

                gesture_result = gesture_controller.update(
                    points,
                    cursor_controller,
                    frame_width,
                    frame_height,
                )

                status_text = gesture_result["status_text"]
                status_color = gesture_result["status_color"]

                draw_gesture_feedback(
                    frame,
                    gesture_result,
                )

            else:
                gesture_controller.handle_missing_hand()

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
        gesture_controller.cleanup()
        hand_tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()