import pyautogui

from config import (
    FRAME_MARGIN_X,
    FRAME_MARGIN_Y,
    SMOOTHING,
)


class CursorController:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

        self.previous_x = self.screen_width // 2
        self.previous_y = self.screen_height // 2

    def move(
        self,
        index_point,
        frame_width,
        frame_height,
    ):
        active_width = frame_width - (2 * FRAME_MARGIN_X)
        active_height = frame_height - (2 * FRAME_MARGIN_Y)

        normalized_x = (
            index_point[0] - FRAME_MARGIN_X
        ) / active_width

        normalized_y = (
            index_point[1] - FRAME_MARGIN_Y
        ) / active_height

        normalized_x = max(
            0.0,
            min(normalized_x, 1.0),
        )

        normalized_y = max(
            0.0,
            min(normalized_y, 1.0),
        )

        target_x = int(
            normalized_x * (self.screen_width - 1)
        )

        target_y = int(
            normalized_y * (self.screen_height - 1)
        )

        smooth_x = int(
            self.previous_x
            + SMOOTHING * (target_x - self.previous_x)
        )

        smooth_y = int(
            self.previous_y
            + SMOOTHING * (target_y - self.previous_y)
        )

        pyautogui.moveTo(
            smooth_x,
            smooth_y,
        )

        self.previous_x = smooth_x
        self.previous_y = smooth_y

    def sync_with_current_position(self):
        self.previous_x, self.previous_y = pyautogui.position()