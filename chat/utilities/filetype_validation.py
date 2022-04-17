import filetype
from filetype.types import image

def is_image(path, image_types=None):
    return __is_file_type("image", path, image_types)

def is_video(path, video_types=None):
    return __is_file_type("video", path, video_types)

def __is_file_type(mime_type, path, file_types=None):

    kind = filetype.guess(path)

    if not kind:
        return False

    mime_parts = kind.mime.split("/")

    if mime_parts[0] != mime_type:
        return False

    if file_types and mime_parts[1] not in file_types:
        return False

    return True
