import cv2
import glob
import struct
import numpy as np
import zstandard as zstd
import os


def extract_frames_from_video(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    i = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(os.path.join(output_dir, f"frame_{i:04d}.png"), frame)
        i += 1

    cap.release()
    return i


def png_frames_to_file(frame_dir, out_path):
    frames = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
    all_bytes = bytearray()

    for f in frames:
        frame = cv2.imread(f)
        flat = frame.reshape(-1, 3)
        all_bytes.extend(flat.flatten())

    header = all_bytes[:12]
    original_size = struct.unpack(">Q", header[:8])[0]
    file_bytes = all_bytes[12 : 12 + original_size]

    with open(out_path, "wb") as f_out:
        f_out.write(file_bytes)


def decompress_file(input_path, output_file):
    with open(input_path, "rb") as f_in, open(output_file, "wb") as f_out:
        dctx = zstd.ZstdDecompressor()
        f_out.write(dctx.decompress(f_in.read()))


def video_to_zip(video_path, restored_file, tmp_dir="tmp"):
    frame_dir = os.path.join(tmp_dir, "decoded_frames")
    compressed_path = os.path.join(tmp_dir, "restored.zst")

    print("Extracting frames...")
    extract_frames_from_video(video_path, frame_dir)

    print("Rebuilding compressed file...")
    png_frames_to_file(frame_dir, compressed_path)

    print("Decompressing to original...")
    decompress_file(compressed_path, restored_file)

    print(f"Done! Restored file: {restored_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert video to file.")
    parser.add_argument("video_path", type=str, help="Path to the input video file.")
    parser.add_argument(
        "restored_file", type=str, help="Path to save the restored file."
    )
    parser.add_argument(
        "--tmp_dir", type=str, default="tmp", help="Temporary directory for processing."
    )

    args = parser.parse_args()

    video_to_zip(args.video_path, args.restored_file)
