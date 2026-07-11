import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    HAND_CONNECTIONS,
    MAX_HANDS,
    MIN_HAND_DETECTION_CONFIDENCE,
    MIN_HAND_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_PATH,
)


class HandTracker:
    def __init__(self):
        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH,
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=MAX_HANDS,
            min_hand_detection_confidence=(
                MIN_HAND_DETECTION_CONFIDENCE
            ),
            min_hand_presence_confidence=(
                MIN_HAND_PRESENCE_CONFIDENCE
            ),
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        self.detector = vision.HandLandmarker.create_from_options(
            options
        )

    def detect(self, frame, timestamp_ms):
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        result = self.detector.detect_for_video(
            mp_image,
            timestamp_ms,
        )

        if not result.hand_landmarks:
            return None

        return result.hand_landmarks[0]

    @staticmethod
    def landmark_to_pixel(
        landmark,
        frame_width,
        frame_height,
    ):
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)

        return x, y

    def draw_hand(self, frame, landmarks):
        frame_height, frame_width, _ = frame.shape

        points = [
            self.landmark_to_pixel(
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

    def close(self):
        self.detector.close()