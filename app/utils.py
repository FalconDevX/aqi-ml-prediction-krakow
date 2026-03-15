from pathlib import Path

def save_file_to_local_dir(caller_file, filename):
    """
    Returns file local file path from the script location
    """
    curr_dir = Path(caller_file).parent

    file_path = curr_dir / str(filename)

    return file_path 