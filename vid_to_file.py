import struct
import cv2
import os


def video_to_zip(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    all_bytes = bytearray()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        flat = frame.reshape(-1, 3)
        all_bytes.extend(flat.flatten())

    cap.release()

    # Extract header (first 12 bytes: 8-byte size + 4-byte padding)
    header = all_bytes[:12]
    original_size = struct.unpack(">Q", header[:8])[0]
    print(f"Decoded original size: {original_size} bytes")

    file_bytes = all_bytes[12 : 12 + original_size]

    with open(output_path, "wb") as f:
        f.write(file_bytes)
    print(f"Decoded video into ZIP file: {output_path}")


def png_frames_to_file(frames_dir, output_path):
    import glob

    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    all_bytes = bytearray()

    for filename in frame_files:
        frame = cv2.imread(filename)
        flat = frame.reshape(-1, 3)
        all_bytes.extend(flat.flatten())

    header = all_bytes[:12]
    original_size = struct.unpack(">Q", header[:8])[0]
    print(f"Original size decoded from header: {original_size} bytes")

    file_bytes = all_bytes[12 : 12 + original_size]

    with open(output_path, "wb") as f:
        f.write(file_bytes)

    print(f"Restored file to: {output_path}")


png_frames_to_file("frames/", "decoded_software.zip")
# video_to_zip("zip_encoded_video.mp4v", "decoded_software.zip")
