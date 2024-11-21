import os
from tqdm.notebook import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading
from PIL import Image

def save_frame_shared(img, i, output_folder, lock):
    """
    Save a single frame from a shared TIFF image object as a JPEG file.

    Args:
        img (PIL.Image.Image): The shared TIFF image object.
        i (int): Frame index.
        output_folder (str): Folder to save the JPEG file.
        lock (threading.Lock): Lock to ensure thread-safe access to the image object.
    """
    jpeg_filename = os.path.join(output_folder, f"{i:05d}.jpg")
    with lock:
        img.seek(i)  # Move to the i-th frame safely
        frame = img.convert("RGB")
    frame.save(jpeg_filename, "JPEG")

def tiff2jpeg(tiff_path, output_folder):
    """
    Convert a multipage TIFF to a series of JPEG files with a shared image object and progress bar.

    Args:
        tiff_path (str): Path to the input multipage TIFF file.
        output_folder (str): Path to the folder where JPEG files will be saved.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Open the TIFF image once
    with Image.open(tiff_path) as img:
        total_frames = img.n_frames

        # Create a lock for thread-safe operations
        lock = threading.Lock()

        # Process frames in parallel
        with tqdm(total=total_frames, desc="Converting TIFF to JPEG", unit="frame", leave=True, dynamic_ncols=True) as pbar:
            with ThreadPoolExecutor() as executor:
                # Submit tasks for each frame
                futures = [executor.submit(save_frame_shared, img, i, output_folder, lock) for i in range(total_frames)]
                
                # Wait for tasks to complete and update the progress bar
                for _ in futures:
                    pbar.update(1)
