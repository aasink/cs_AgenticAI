import cv2
import ollama
import base64
from datetime import timedelta

PROMPT = (
    "Is there a person visible in this image? "
    "Reply with only 'yes' or 'no'."
)

def extract_frames(video_path: str) -> list:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * 2)

    frames = []
    frame_num = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num % interval == 0:
            frames.append(frame)
        frame_num += 1

    cap.release()

    for i, frame in enumerate(frames):
        cv2.imwrite(f"frames/frame_{i:04d}.jpg", frame)

    return [f"frames/frame_{i:04d}.jpg" for i in range(len(frames))]

def call_llava(frame_path: str) -> bool:
    
    response = ollama.chat(
        model="llava",
        messages=[{
            "role": "user",
            "content": PROMPT,
            "images": [frame_path],
        }]
    )

    answer = response["message"]["content"].strip().lower()
    return answer.startswith("yes")

def format_time(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))[2:]    # format as mm:ss


def main():
    vpath = input("Enter the path to the video file: ").strip()
    frame_paths = extract_frames(vpath)

    print(f"Extracted {len(frame_paths)} frames\n")
    print("Analysing frames...\n")

    person_present = False
    entry_time = None

    for i, frame_path in enumerate(frame_paths):
        timestamp = i * 2  # each frame is 2 seconds apart
        detected = call_llava(frame_path)
        status = "person detected" if detected else "empty"
        print(f"  [{format_time(timestamp)}] {status}")

        # Person just entered
        if detected and not person_present:
            person_present = True
            entry_time = timestamp
            print(f"  --> Person ENTERED at {format_time(timestamp)}")

        # Person just exited
        elif not detected and person_present:
            person_present = False
            print(f"  --> Person EXITED at {format_time(timestamp)}")
            entry_time = None

    # Still present at end of video
    if person_present:
        print(f"  --> Person still present at end of video (entered at {format_time(entry_time)})")

    print("\nDone.")

if __name__ == "__main__":
    main()
