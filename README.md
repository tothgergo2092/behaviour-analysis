# Video Processing and Distribution Script

## Description
This script processes video files by splitting them into smaller parts based on predefined grid dimensions. It then distributes these parts among different workers for tasks such as annotation. This can be particularly useful in workflows where parallel processing of video data is required.

## Modules and Libraries
The script uses the following Python modules:
- `os` and `shutil` for handling file and directory operations.
- `cv2` (OpenCV) for video processing.
- `random` for shuffling parts before distribution.
- `multiprocessing` and `concurrent.futures` for parallel processing.

## Functions

### process_video_part
Processes a specific part of a video and saves it to a temporary folder.

**Parameters:**
- `video_path` (str): Path to the original video file.
- `temp_folder` (str): Path to the folder where the video part will be saved.
- `part_name` (str): Name of the video part.
- `frame_indices` (Tuple[int, int]): Starting indices (x, y) to crop the video part.
- `frame_size` (Tuple[int, int]): Size of the cropped frame (width, height).
- `total_frames` (int): Total number of frames to process.
- `fps` (int): Frames per second of the original video.

**Returns:**
- `str`: Path to the processed video part.

### distribute_videos_to_workers
Distributes processed video parts to workers' annotation folders.

**Parameters:**
- `videos_folder` (str): Folder containing the original videos to be split.
- `workers` (List[str]): List of worker directories to distribute processed video parts.
- `n_parts` (int): Number of vertical parts to split the video into.
- `m_parts` (int): Number of horizontal parts to split the video into.

**Raises:**
- `ValueError`: If the provided video folder does not exist.

## Setup and Execution
To run this script, ensure all dependencies are installed and modify the parameters in the script as necessary to fit the video files and desired grid configuration. Use high-performance hardware for processing large video files to optimize execution time.

