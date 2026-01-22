from pathlib import Path
import pickle
import numpy as np
import cv2
import face_recognition
from biometric.biometric_base import BiometricProvider

ENCODINGS_PATH = Path("encodings.pkl")

class FaceProvider(BiometricProvider):
    def __init__(self, tolerance: float = 0.5, camera_index: int = 0, max_seconds: int = 10):
        """
        tolerance: lower = stricter (0.45-0.55 good range)
        max_seconds: stop trying after N seconds
        """
        self.tolerance = tolerance
        self.camera_index = camera_index
        self.max_seconds = max_seconds

    def _load_db(self):
        if not ENCODINGS_PATH.exists():
            return {"teacher_ids": [], "encodings": []}
        with open(ENCODINGS_PATH, "rb") as f:
            return pickle.load(f)

    def identify(self) -> str:
        data = self._load_db()
        known_ids = data["teacher_ids"]
        known_encs = data["encodings"]

        if not known_ids:
            raise RuntimeError("No face encodings found. Enroll teachers first (python face_enroll.py).")

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Webcam not found.")

        start = cv2.getTickCount()
        freq = cv2.getTickFrequency()

        best_id = None
        best_dist = 999.0

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb, model="hog")
            face_encs = face_recognition.face_encodings(rgb, face_locations)

            for (top, right, bottom, left), enc in zip(face_locations, face_encs):
                dists = face_recognition.face_distance(known_encs, enc)
                idx = int(np.argmin(dists))
                dist = float(dists[idx])

                label = "Unknown"
                if dist <= self.tolerance:
                    label = f"{known_ids[idx]} (dist={dist:.2f})"
                    if dist < best_dist:
                        best_dist = dist
                        best_id = known_ids[idx]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, label, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.putText(frame, "Press 'q' to cancel", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            cv2.imshow("Face पहचान", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            elapsed = (cv2.getTickCount() - start) / freq
            if elapsed >= self.max_seconds:
                break

        cap.release()
        cv2.destroyAllWindows()

        if best_id is None:
            raise RuntimeError("Face not recognized. Improve lighting or re-enroll with more samples.")
        return best_id
