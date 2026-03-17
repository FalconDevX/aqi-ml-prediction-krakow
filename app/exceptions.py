class ExternalAPIError(Exception):
    def __init__(self, message: str, status_code: int, url: str):
        self.message = message
        self.status_code = status_code
        self.url = url
        super().__init__(message)