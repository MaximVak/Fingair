import math
import time

import pyautogui

from config import (
    DRAG_HOLD_TIME,
    INDEX_TIP,
    PINCH_RELEASE_THRESHOLD,
    PINCH_START_THRESHOLD,
    THUMB_TIP,
)


class GestureController:
    def __init__(self):
        self.is_pinching = False
        self.is_dragging = False
        self.pinch_start_time = 0.0

    @staticmethod
    def calculate_distance(point_a, point_b):
        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        )

    def update(
        self,
        points,
        cursor_controller,
        frame_width,
        frame_height,
    ):
        index_point = points[INDEX_TIP]
        thumb_point = points[THUMB_TIP]

        pinch_distance = self.calculate_distance(
            thumb_point,
            index_point,
        )

        current_time = time.perf_counter()

        status_text = "MOVE"
        status_color = (255, 255, 255)
        hold_progress = None

        if (
            not self.is_pinching
            and pinch_distance < PINCH_START_THRESHOLD
        ):
            self.is_pinching = True
            self.pinch_start_time = current_time

        if self.is_pinching:
            pinch_duration = (
                current_time - self.pinch_start_time
            )

            # Check for release before moving the cursor.
            if pinch_distance > PINCH_RELEASE_THRESHOLD:
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False

                    status_text = "DRAG RELEASED"
                    status_color = (0, 255, 0)
                else:
                    pyautogui.click()

                    status_text = "CLICK"
                    status_color = (0, 255, 0)

                self.is_pinching = False

                # Prevent the cursor from jumping on release.
                cursor_controller.sync_with_current_position()

            else:
                if (
                    not self.is_dragging
                    and pinch_duration >= DRAG_HOLD_TIME
                ):
                    pyautogui.mouseDown()
                    self.is_dragging = True

                if self.is_dragging:
                    cursor_controller.move(
                        index_point,
                        frame_width,
                        frame_height,
                    )

                    status_text = "DRAGGING"
                    status_color = (0, 165, 255)
                else:
                    # Lock the cursor while deciding whether this
                    # will be a click or drag.
                    status_text = "PINCH - HOLD TO DRAG"
                    status_color = (0, 255, 255)

                    hold_progress = min(
                        pinch_duration / DRAG_HOLD_TIME,
                        1.0,
                    )

        else:
            cursor_controller.move(
                index_point,
                frame_width,
                frame_height,
            )

        return {
            "status_text": status_text,
            "status_color": status_color,
            "pinch_distance": pinch_distance,
            "hold_progress": hold_progress,
            "index_point": index_point,
            "thumb_point": thumb_point,
        }

    def handle_missing_hand(self):
        if self.is_dragging:
            pyautogui.mouseUp()

        self.is_dragging = False
        self.is_pinching = False

    def cleanup(self):
        if self.is_dragging:
            pyautogui.mouseUp()

        self.is_dragging = False
        self.is_pinching = False