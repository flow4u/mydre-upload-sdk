"""
myDRE Upload SDK for Python
"""

from .uploader import (
    WorkspaceUploader,
    WorkspaceConfig,
    WorkspaceUploadError,
    APIError,
    BlobStorageError,
    verify_dependencies
)

__all__ = [
    "WorkspaceUploader",
    "WorkspaceConfig",
    "WorkspaceUploadError",
    "APIError",
    "BlobStorageError",
    "verify_dependencies",
]

__version__ = "1.0.0"
