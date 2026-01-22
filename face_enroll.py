import cv2
import pickle
import numpy as np
from pathlib import Path
import face_recognition

ENCODINGS_PATH = Path("encodings.pkl")

def load_encodings():
    if ENCODINGS_PATH.exists():
        with open(ENCODINGS_PATH, "rb") as f:
            return pickle.load(f)
    return {"teacher_ids": [], "encodings": []}

def save_encodings(data):
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump(data, f)

def enroll_teacher(teacher_id: str, samples: int = 10):
    data = load_encodings()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Webcam not found.")

    collected = 0
    print("\nINSTRUCTIONS:")
    print("- Keep your face centered and well-lit.")
    print("- Press 'c' to capture a sample (need multiple).")
    print("- Press 'q' to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Convert BGR (OpenCV) to RGB (face_recognition expects RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb, model="hog")
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(frame, f"Teacher: {teacher_id}  Samples: {collected}/{samples}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("Enroll Face", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord("c"):
            if len(face_locations) != 1:
                print("Capture failed: ensure exactly ONE face is visible.")
                continue

            encs = face_recognition.face_encodings(rgb, face_locations)
            if not encs:
                print("Capture failed: no encoding generated, try again.")
                continue

            data["teacher_ids"].append(teacher_id)
            data["encodings"].append(encs[0])
            collected += 1
            print(f"Captured sample {collected}/{samples}")

            if collected >= samples:
                print("Enrollment complete.")
                break

    cap.release()
    cv2.destroyAllWindows()
    save_encodings(data)

if __name__ == "__main__":
    teacher_id = input("Enter Teacher ID to enroll: ").strip()
    enroll_teacher(teacher_id, samples=10)
