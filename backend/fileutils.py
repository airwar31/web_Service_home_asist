import os
import secrets
import tempfile

ALLOWED_EXTENSIONS = {"wav", "mp3", "ogg", "m4a", "webm"}

def allowed_file(filename: str) -> bool:

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_ext(filename: str) -> str:

    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""

def temp_filepath(suffix: str = "") -> str:

    name = secrets.token_hex(8)
    directory = tempfile.gettempdir()
    return os.path.join(directory, f"{name}{suffix}")
