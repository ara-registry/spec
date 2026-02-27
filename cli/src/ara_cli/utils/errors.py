"""Custom exception hierarchy for ARA CLI."""


class ARAError(Exception):
    """Base exception for all ARA CLI errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ARAValidationError(ARAError):
    """Raised when manifest validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        self.errors = errors or []
        super().__init__(message)


class ARARegistryError(ARAError):
    """Raised when a registry API call fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class ARAAuthError(ARAError):
    """Raised when authentication fails or is missing."""


class ARANotFoundError(ARAError):
    """Raised when a package or version is not found."""


class ARAConflictError(ARAError):
    """Raised when a version already exists."""


class ARACyclicDependencyError(ARAError):
    """Raised when a cyclic dependency is detected."""

    def __init__(self, message: str, cycle: list[str] | None = None):
        self.cycle = cycle or []
        super().__init__(message)


class ARAChecksumError(ARAError):
    """Raised when a checksum verification fails."""

    def __init__(self, message: str, expected: str = "", actual: str = ""):
        self.expected = expected
        self.actual = actual
        super().__init__(message)
