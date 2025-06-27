import os
import math
import cv2
import struct
import numpy as np
import zstandard as zstd
import subprocess

FRAME_SIZE = (256, 256) 


def compress_file(input_file, compressed_path):
    with open(input_file, "rb") as f_in, open(compressed_path, "wb") as f_out:
        compressor = zstd.ZstdCompressor()
        f_out.write(compressor.compress(f_in.read()))


def file_to_png_frames(input_path, frame_dir):
    with open(input_path, "rb") as f:
        data = f.read()

    original_size = len(data)
    header = struct.pack(">Q", original_size) + b"\x00" * 4
    data = header + data
    data += b"\x00" * ((3 - len(data) % 3) % 3)

    pixels = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3)
    total_pixels = FRAME_SIZE[0] * FRAME_SIZE[1]
    num_frames = math.ceil(len(pixels) / total_pixels)

    os.makedirs(frame_dir, exist_ok=True)

    for i in range(num_frames):
        chunk = pixels[i * total_pixels : (i + 1) * total_pixels]
        padded = np.zeros((total_pixels, 3), dtype=np.uint8)
        padded[: len(chunk)] = chunk
        frame = padded.reshape((FRAME_SIZE[1], FRAME_SIZE[0], 3))
        cv2.imwrite(os.path.join(frame_dir, f"frame_{i:04d}.png"), frame)

    return num_frames


def encode_frames_to_video(frame_dir, output_video):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            "30",
            "-i",
            os.path.join(frame_dir, "frame_%04d.png"),
            "-c:v",
            "libx264rgb",
            "-crf",
            "0",
            "-preset",
            "slow",
            output_video,
        ]
        # [
        #     "ffmpeg",
        #     "-y",
        #     "-framerate",
        #     "1",
        #     "-i",
        #     os.path.join(frame_dir, "frame_%04d.png"),
        #     "-c:v",
        #     "libx264rgb",
        #     "-crf",
        #     "0",
        #     "-preset",
        #     "ultrafast",
        #     output_video,
        # ]
    )


def zip_to_video(input_file, output_video, tmp_dir="tmp"):
    compressed_path = os.path.join(tmp_dir, "compressed.zst")
    frame_dir = os.path.join(tmp_dir, "frames")

    os.makedirs(tmp_dir, exist_ok=True)

    compress_file(input_file, compressed_path)

    file_to_png_frames(compressed_path, frame_dir)

    encode_frames_to_video(frame_dir, output_video)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert a file to a video.")
    parser.add_argument("input_file", help="Path to the input file to encode.")
    parser.add_argument("output_video", help="Path to the output video file.")
    parser.add_argument("--tmp_dir", default="tmp", help="Temporary directory for processing.")

    args = parser.parse_args()

    zip_to_video(args.input_file, args.output_video, args.tmp_dir)
    print(f"Video created at: {args.output_video}")
