import os
import shutil
import cv2
import random
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple

def process_video_part(video_path: str, temp_folder: str, part_name: str, frame_indices: Tuple[int, int], frame_size: Tuple[int, int], total_frames: int, fps: int) -> str:
    """
    Process a specific part of a video and save it to a temporary folder.

    Args:
        video_path (str): Path to the original video file.
        temp_folder (str): Path to the folder where the video part will be saved.
        part_name (str): Name of the video part.
        frame_indices (Tuple[int, int]): Starting indices (x, y) to crop the video part.
        frame_size (Tuple[int, int]): Size of the cropped frame (width, height).
        total_frames (int): Total number of frames to process.
        fps (int): Frames per second of the original video.

    Returns:
        str: Path to the processed video part.
    """
    grid_width, grid_height = frame_size
    x_start, y_start = frame_indices
    part_output_path = os.path.join(temp_folder, f"{part_name}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(part_output_path, fourcc, fps, (grid_width, grid_height))

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    for frame_num in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        cropped_frame = frame[y_start:y_start + grid_height, x_start:x_start + grid_width]
        out.write(cropped_frame)

    out.release()
    cap.release()
    return part_output_path

def distribute_videos_to_workers(videos_folder: str, workers: List[str], n_parts: int, m_parts: int) -> None:
    """
    Distribute processed video parts to workers' annotation folders.

    Args:
        videos_folder (str): Folder containing the original videos to be split.
        workers (List[str]): List of worker directories to distribute processed video parts.
        n_parts (int): Number of vertical parts to split the video into.
        m_parts (int): Number of horizontal parts to split the video into.

    Raises:
        ValueError: If the provided video folder does not exist.
    """
    annotation_root = "annotation"
    os.makedirs(annotation_root, exist_ok=True)
    for worker in workers:
        worker_dir = os.path.join(annotation_root, worker)
        os.makedirs(worker_dir, exist_ok=True)
        # Clear existing contents to avoid duplication
        for item in os.listdir(worker_dir):
            shutil.rmtree(os.path.join(worker_dir, item), ignore_errors=True)

    if not os.path.exists(videos_folder):
        raise ValueError(f"Provided videos folder does not exist: {videos_folder}")
    
    video_files = [f for f in os.listdir(videos_folder) if f.lower().endswith(('.mp4', '.avi', '.mkv'))]

    for video_file in video_files:
        video_path = os.path.join(videos_folder, video_file)
        video_name, _ = os.path.splitext(video_file)
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        grid_width = width // m_parts
        grid_height = height // n_parts
        temp_folder = "temp"
        os.makedirs(temp_folder, exist_ok=True)
        part_videos = []

        num_cores = multiprocessing.cpu_count()
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            future_to_part = {
                executor.submit(
                    process_video_part, video_path, temp_folder, f"{video_name}_part_{i+1}_{j+1}",
                    (j * grid_width, i * grid_height), (grid_width, grid_height), total_frames, fps
                ): f"{video_name}_part_{i+1}_{j+1}"
                for i in range(n_parts) for j in range(m_parts)
            }
            for future in as_completed(future_to_part):
                part_videos.append((future_to_part[future], future.result()))

        # Shuffle and distribute video parts fairly among workers
        worker_distribution = {worker: [] for worker in workers}
        random.shuffle(part_videos)
        while part_videos:
            for worker in workers:
                if part_videos:
                    part_name, part_path = part_videos.pop()
                    worker_distribution[worker].append((part_name, part_path))

        # Copy video parts to respective worker annotation folders
        for worker, videos in worker_distribution.items():
            for part_name, part_path in videos:
                worker_folder = os.path.join(annotation_root, worker, part_name)
                os.makedirs(worker_folder, exist_ok=True)
                shutil.copy(part_path, os.path.join(worker_folder, os.path.basename(part_path)))

        # Clean up temporary processing folder
        shutil.rmtree(temp_folder, ignore_errors=True)

    print("Video processing and distribution completed.")
