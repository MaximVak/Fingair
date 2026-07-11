import math
import time

import pyautogui

from config import (
    DRAG_HOLD_TIME,
    INDEX_MCP,
    INDEX_PIP,
    INDEX_TIP,
    MIDDLE_MCP,
    MIDDLE_PIP,
    MIDDLE_TIP,
    OPEN_HAND_FINGER_MARGIN,
    OPEN_HAND_THUMB_DISTANCE,
    PAUSE_HOLD_TIME,
    PINCH_RELEASE_THRESHOLD,
    PINCH_START_THRESHOLD,
    PINKY_PIP,
    PINKY_TIP,
    RIGHT_CLICK_INDEX_SEPARATION,
    RIGHT_CLICK_RELEASE_THRESHOLD,
    RIGHT_CLICK_START_THRESHOLD,
    RING_PIP,
    RING_TIP,
    SCROLL_COOLDOWN,
    SCROLL_DIRECTION_THRESHOLD,
    SCROLL_SENSITIVITY,
    SCROLL_THUMB_DISTANCE_THRESHOLD,
    THUMB_TIP,
)


class GestureController:
    def __init__(self):
        # Left-click and drag state
        self.is_pinching = False
        self.is_dragging = False
        self.pinch_start_time = 0.0

        # Right-click state
        self.is_right_pinching = False

        # Scroll state
        self.is_scrolling = False
        self.last_scroll_time = 0.0

        # Pause state
        self.is_paused = False
        self.pause_gesture_start_time = None
        self.pause_toggle_ready = True

    @staticmethod
    def calculate_distance(point_a, point_b):
        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        )

    @staticmethod
    def finger_is_extended(
        points,
        tip_index,
        pip_index,
    ):
        return (
            points[tip_index][1]
            < points[pip_index][1] - OPEN_HAND_FINGER_MARGIN
        )

    def open_hand_is_active(self, points):
        index_extended = self.finger_is_extended(
            points,
            INDEX_TIP,
            INDEX_PIP,
        )

        middle_extended = self.finger_is_extended(
            points,
            MIDDLE_TIP,
            MIDDLE_PIP,
        )

        ring_extended = self.finger_is_extended(
            points,
            RING_TIP,
            RING_PIP,
        )

        pinky_extended = self.finger_is_extended(
            points,
            PINKY_TIP,
            PINKY_PIP,
        )

        thumb_distance = self.calculate_distance(
            points[THUMB_TIP],
            points[INDEX_MCP],
        )

        thumb_extended = (
            thumb_distance > OPEN_HAND_THUMB_DISTANCE
        )

        return (
            index_extended
            and middle_extended
            and ring_extended
            and pinky_extended
            and thumb_extended
        )

    def release_active_controls(self):
        if self.is_dragging:
            pyautogui.mouseUp()

        self.is_dragging = False
        self.is_pinching = False
        self.is_right_pinching = False
        self.is_scrolling = False

    def handle_pause_gesture(
        self,
        points,
        cursor_controller,
        current_time,
    ):
        open_hand = self.open_hand_is_active(points)

        if open_hand:
            if self.pause_gesture_start_time is None:
                self.pause_gesture_start_time = current_time

            gesture_duration = (
                current_time - self.pause_gesture_start_time
            )

            if (
                gesture_duration >= PAUSE_HOLD_TIME
                and self.pause_toggle_ready
            ):
                self.release_active_controls()

                self.is_paused = not self.is_paused
                self.pause_toggle_ready = False

                cursor_controller.sync_with_current_position()

                return True
        else:
            self.pause_gesture_start_time = None
            self.pause_toggle_ready = True

        return False

    def get_scroll_direction(self, points):
        thumb_point = points[THUMB_TIP]

        index_tip = points[INDEX_TIP]
        index_mcp = points[INDEX_MCP]

        middle_tip = points[MIDDLE_TIP]
        middle_mcp = points[MIDDLE_MCP]

        thumb_index_distance = self.calculate_distance(
            thumb_point,
            index_tip,
        )

        if (
            thumb_index_distance
            <= SCROLL_THUMB_DISTANCE_THRESHOLD
        ):
            return 0

        index_vertical_change = (
            index_tip[1] - index_mcp[1]
        )

        middle_vertical_change = (
            middle_tip[1] - middle_mcp[1]
        )

        fingers_point_up = (
            index_vertical_change
            < -SCROLL_DIRECTION_THRESHOLD
            and middle_vertical_change
            < -SCROLL_DIRECTION_THRESHOLD
        )

        fingers_point_down = (
            index_vertical_change
            > SCROLL_DIRECTION_THRESHOLD
            and middle_vertical_change
            > SCROLL_DIRECTION_THRESHOLD
        )

        if fingers_point_up:
            return 1

        if fingers_point_down:
            return -1

        return 0

    def handle_continuous_scroll(
        self,
        direction,
        cursor_controller,
        current_time,
    ):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.last_scroll_time = current_time
            cursor_controller.sync_with_current_position()

        if (
            current_time - self.last_scroll_time
            >= SCROLL_COOLDOWN
        ):
            scroll_amount = int(
                direction * SCROLL_SENSITIVITY
            )

            if scroll_amount != 0:
                pyautogui.scroll(scroll_amount)

            self.last_scroll_time = current_time

    def exit_scroll_mode(self, cursor_controller):
        if self.is_scrolling:
            self.is_scrolling = False
            cursor_controller.sync_with_current_position()

    @staticmethod
    def make_result(
        status_text,
        status_color,
        pinch_distance,
        hold_progress,
        index_point,
        thumb_point,
    ):
        return {
            "status_text": status_text,
            "status_color": status_color,
            "pinch_distance": pinch_distance,
            "hold_progress": hold_progress,
            "index_point": index_point,
            "thumb_point": thumb_point,
        }

    def update(
        self,
        points,
        cursor_controller,
        frame_width,
        frame_height,
    ):
        index_point = points[INDEX_TIP]
        middle_point = points[MIDDLE_TIP]
        thumb_point = points[THUMB_TIP]

        index_pinch_distance = self.calculate_distance(
            thumb_point,
            index_point,
        )

        middle_pinch_distance = self.calculate_distance(
            thumb_point,
            middle_point,
        )

        current_time = time.perf_counter()

        self.handle_pause_gesture(
            points,
            cursor_controller,
            current_time,
        )

        if self.is_paused:
            return self.make_result(
                status_text="PAUSED - HOLD OPEN HAND TO RESUME",
                status_color=(0, 0, 255),
                pinch_distance=index_pinch_distance,
                hold_progress=None,
                index_point=index_point,
                thumb_point=thumb_point,
            )

        if self.open_hand_is_active(points):
            return self.make_result(
                status_text="HOLD OPEN HAND TO PAUSE",
                status_color=(0, 255, 255),
                pinch_distance=index_pinch_distance,
                hold_progress=None,
                index_point=index_point,
                thumb_point=thumb_point,
            )

        status_text = "MOVE"
        status_color = (255, 255, 255)
        hold_progress = None

        # Start right-click pinch.
        if (
            not self.is_right_pinching
            and not self.is_pinching
            and not self.is_dragging
            and middle_pinch_distance
            < RIGHT_CLICK_START_THRESHOLD
            and index_pinch_distance
            > RIGHT_CLICK_INDEX_SEPARATION
        ):
            self.exit_scroll_mode(cursor_controller)
            self.is_right_pinching = True

        # Handle right-click pinch.
        if self.is_right_pinching:
            if (
                middle_pinch_distance
                > RIGHT_CLICK_RELEASE_THRESHOLD
            ):
                pyautogui.rightClick()
                self.is_right_pinching = False

                cursor_controller.sync_with_current_position()

                status_text = "RIGHT CLICK"
                status_color = (255, 0, 255)
            else:
                status_text = "RIGHT-CLICK PINCH"
                status_color = (255, 0, 255)

            return self.make_result(
                status_text,
                status_color,
                index_pinch_distance,
                None,
                index_point,
                thumb_point,
            )

        # Handle scrolling.
        scroll_direction = self.get_scroll_direction(points)

        if (
            scroll_direction != 0
            and not self.is_pinching
            and not self.is_dragging
        ):
            self.handle_continuous_scroll(
                scroll_direction,
                cursor_controller,
                current_time,
            )

            if scroll_direction > 0:
                status_text = "SCROLL UP"
            else:
                status_text = "SCROLL DOWN"

            status_color = (255, 255, 0)

            return self.make_result(
                status_text,
                status_color,
                index_pinch_distance,
                None,
                index_point,
                thumb_point,
            )

        self.exit_scroll_mode(cursor_controller)

        # Start left-click or drag pinch.
        if (
            not self.is_pinching
            and index_pinch_distance
            < PINCH_START_THRESHOLD
        ):
            self.is_pinching = True
            self.pinch_start_time = current_time

        if self.is_pinching:
            pinch_duration = (
                current_time - self.pinch_start_time
            )

            if (
                index_pinch_distance
                > PINCH_RELEASE_THRESHOLD
            ):
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False

                    status_text = "DRAG RELEASED"
                    status_color = (0, 255, 0)
                else:
                    pyautogui.click()

                    status_text = "LEFT CLICK"
                    status_color = (0, 255, 0)

                self.is_pinching = False
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

        return self.make_result(
            status_text,
            status_color,
            index_pinch_distance,
            hold_progress,
            index_point,
            thumb_point,
        )

    def handle_missing_hand(self):
        self.release_active_controls()

        self.pause_gesture_start_time = None
        self.pause_toggle_ready = True

    def cleanup(self):
        self.release_active_controls()