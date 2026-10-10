class PhotoTooLargeException(Exception):
    def __init__(self, max_bytes: int):
        super().__init__(f"The photo is larger than the {max_bytes // (1024 * 1024)} MB limit")
