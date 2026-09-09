# -*- coding: utf-8 -*-
"""
Workspace Uploader Module
-------------------------
Handles API authentication, container lifecycle, and Azure Blob storage uploads.
"""

from dataclasses import dataclass
from datetime import datetime
import importlib
import io
import os
import subprocess
import sys
from typing import Any, Dict, Optional, Union

DEFAULT_BASE_URL = "https://andreanl-api-management.azure-api.net/v1"

REQUIRED_PACKAGES = {
    "requests": "requests",
    "azure.storage.blob": "azure-storage-blob",
    "pandas": "pandas",
}


def verify_dependencies(auto_install: bool = True) -> None:
    """Verifies that mandatory packages are installed in the active environment."""
    missing_packages = []

    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append(pip_name)

    if not missing_packages:
        return

    missing_str = " ".join(missing_packages)

    if auto_install:
        print(f"[myDRE SDK] Missing dependencies detected: {', '.join(missing_packages)}.")
        print("[myDRE SDK] Attempting automatic package installation...")
        try:
            # Detect uv if present, otherwise fall back to python -m pip
            if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
                cmd = ["uv", "pip", "install"] + missing_packages
            else:
                cmd = [sys.executable, "-m", "pip", "install"] + missing_packages

            subprocess.check_call(cmd)
            print("[myDRE SDK] Dependencies successfully installed.")
            return
        except Exception as err:
            print(f"[myDRE SDK] Automatic installation failed: {err}")

    instructions = (
        f"\n{'=' * 70}\n"
        f"MISSING DEPENDENCY ERROR\n"
        f"{'=' * 70}\n"
        f"The myDRE Upload SDK requires the following package(s):\n"
        f"  - " + "\n  - ".join(missing_packages) + "\n\n"
        f"Install them manually using:\n"
        f"  uv:            uv pip install {missing_str}\n"
        f"  pip:           {sys.executable} -m pip install {missing_str}\n"
        f"  Jupyter/Colab: !pip install {missing_str}\n"
        f"{'=' * 70}\n"
    )
    raise ImportError(instructions)


# Run verification check on package import
verify_dependencies(auto_install=True)

import pandas as pd
import requests
from azure.storage.blob import ContainerClient, ContentSettings


class WorkspaceUploadError(Exception):
    """Base exception for all myDRE Upload SDK errors."""
    pass


class APIError(WorkspaceUploadError):
    """Raised when REST API requests fail."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class BlobStorageError(WorkspaceUploadError):
    """Raised when Azure Blob Storage file transfers fail."""
    pass


@dataclass
class WorkspaceConfig:
    """Dataclass holding workspace authentication settings."""
    workspace_name: str
    workspace_key: str
    subscription_key: str
    base_url: str = DEFAULT_BASE_URL

    @classmethod
    from_dict(cls, config_dict: Dict[str, Any]) -> "WorkspaceConfig":
        """Constructs a WorkspaceConfig instance from a dictionary."""
        try:
            return cls(
                workspace_name=config_dict["workspace_name"],
                workspace_key=config_dict["workspace_key"],
                subscription_key=config_dict["subscription_key"],
                base_url=config_dict.get("base_url", DEFAULT_BASE_URL)
            )
        except KeyError as missing_key:
            raise ValueError(f"Missing required configuration parameter: {missing_key}") from missing_key


class WorkspaceUploader:
    """Client for managing upload containers and data transfers in myDRE Workspaces."""

    def __init__(self, workspace_config: Union[WorkspaceConfig, Dict[str, Any]], auto_install_deps: bool = True):
        verify_dependencies(auto_install=auto_install_deps)

        if isinstance(workspace_config, dict):
            self.config = WorkspaceConfig.from_dict(workspace_config)
        elif isinstance(workspace_config, WorkspaceConfig):
            self.config = workspace_config
        else:
            raise TypeError("workspace_config must be a WorkspaceConfig object or dictionary.")

        self.session = requests.Session()
        self.session.headers.update({
            'Api-Key': self.config.workspace_key,
            'Ocp-Apim-Subscription-Key': self.config.subscription_key
        })

    def _get_url(self, endpoint: str) -> str:
        return f"{self.config.base_url.rstrip('/')}{endpoint}"

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = self._get_url(endpoint)
        try:
            response = self.session.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:
            status_code = getattr(err.response, 'status_code', None)
            response_text = getattr(err.response, 'text', str(err))
            raise APIError(
                f"API Request failed: {method} {endpoint} - Status {status_code}: {response_text}",
                status_code=status_code,
                response_text=response_text
            ) from err

    def test_connection(self) -> bool:
        """Tests connectivity to the workspace API."""
        response = self._request('GET', '/api/ping')
        return response.status_code == 200

    def list_containers(self) -> Dict[str, Any]:
        """Lists active upload containers for the workspace."""
        endpoint = f"/api/workspace/{self.config.workspace_name}/files/containers"
        return self._request('GET', endpoint).json()

    def create_container(self, title: Optional[str] = None) -> str:
        """Creates a new upload container and returns its SAS Location URL."""
        timestamp = f'{datetime.now():%Y-%m-%d %H:%M:%S}'
        container_title = f"{timestamp} {title}" if title else timestamp

        endpoint = f"/api/workspace/{self.config.workspace_name}/files/containers"
        params = {'title': container_title}

        response = self._request('POST', endpoint, params=params)
        
        if 'Location' not in response.headers:
            raise APIError("API created container but did not return a 'Location' header.")
            
        return response.headers['Location']

    def commit_container(self, container_location: str) -> requests.Response:
        """Commits changes in an upload container."""
        if not container_location:
            raise ValueError("Container location cannot be empty.")

        container_identifier = container_location.rsplit('/', 1)[-1]
        endpoint = f"/api/workspace/{self.config.workspace_name}/files/containers/{container_identifier}"
        return self._request('PATCH', endpoint)

    def delete_container(self, container_location: str) -> requests.Response:
        """Deletes an upload container and its uncommitted contents."""
        if not container_location:
            raise ValueError("Container location cannot be empty.")

        container_identifier = container_location.rsplit('/', 1)[-1]
        endpoint = f"/api/workspace/{self.config.workspace_name}/files/containers/{container_identifier}"
        return self._request('DELETE', endpoint)

    def upload_text(self, container_url: str, text_data: str, filename: str = 'my_text.txt') -> None:
        """Uploads plain text content directly to the target Azure container."""
        try:
            container_client = ContainerClient.from_container_url(container_url)
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(
                text_data.encode('utf-8'),
                content_settings=ContentSettings(content_type='text/plain'),
                overwrite=True
            )
        except Exception as err:
            raise BlobStorageError(f"Failed to upload text file '{filename}': {err}") from err

    def upload_dataframe(self, container_url: str, df: pd.DataFrame, filename: str = 'data.csv') -> None:
        """Uploads a pandas DataFrame as a CSV file to the target Azure container."""
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')

            container_client = ContainerClient.from_container_url(container_url)
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(csv_data, overwrite=True)
        except Exception as err:
            raise BlobStorageError(f"Failed to upload DataFrame as '{filename}': {err}") from err

    def upload_file(self, container_url: str, local_file_path: str, filename: Optional[str] = None) -> None:
        """Uploads a local file to the target Azure container."""
        if not os.path.isfile(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        target_name = filename or os.path.basename(local_file_path)

        try:
            container_client = ContainerClient.from_container_url(container_url)
            with open(local_file_path, "rb") as file_to_upload:
                container_client.upload_blob(target_name, file_to_upload, overwrite=True)
        except Exception as err:
            raise BlobStorageError(f"Failed to upload file '{local_file_path}': {err}") from err
