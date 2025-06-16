import cv2
import numpy as np
import math
import struct
import os

def zip_to_video(zip_path, video_path, frame_size=(256, 256), fps=1):
    with open(zip_path, 'rb') as f:
        data = f.read()

    original_size = len(data)
    print(f"Original file size: {original_size} bytes")

    # Header: Store file size in first 4 pixels (12 bytes)
    header = struct.pack(">Q", original_size)  # 8 bytes, big-endian
    header += b'\x00' * 4  # pad to 12 bytes

    data = header + data
    padding = (3 - len(data) % 3) % 3
    data += b'\x00' * padding

    pixels = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3)
    total_pixels = frame_size[0] * frame_size[1]
    num_frames = math.ceil(len(pixels) / total_pixels)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    for i in range(num_frames):
        chunk = pixels[i * total_pixels : (i + 1) * total_pixels]
        padded = np.zeros((total_pixels, 3), dtype=np.uint8)
        padded[:len(chunk)] = chunk
        frame = padded.reshape((frame_size[1], frame_size[0], 3))
        out.write(frame)

    out.release()
    print(f"Encoded ZIP into video: {video_path}")


def file_to_png_frames(input_path, output_dir, frame_size=(256, 256)):
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "rb") as f:
        data = f.read()

    original_size = len(data)
    header = struct.pack(">Q", original_size) + b"\x00" * 4  # 12 bytes
    data = header + data
    padding = (3 - len(data) % 3) % 3
    data += b"\x00" * padding

    pixels = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3)
    total_pixels = frame_size[0] * frame_size[1]
    num_frames = math.ceil(len(pixels) / total_pixels)

    for i in range(num_frames):
        chunk = pixels[i * total_pixels : (i + 1) * total_pixels]
        padded = np.zeros((total_pixels, 3), dtype=np.uint8)
        padded[: len(chunk)] = chunk
        frame = padded.reshape((frame_size[1], frame_size[0], 3))
        filename = os.path.join(output_dir, f"frame_{i:04d}.png")
        cv2.imwrite(filename, frame)

    print(f"Saved {num_frames} PNG frames to {output_dir}")


file_to_png_frames("software.zip", "frames/")
# zip_to_video("software.zip", "zip_encoded_video.mp4v")
