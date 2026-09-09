# myDRE Upload SDK - Python Client

Python implementation for interacting with myDRE Workspace Upload APIs and Blob Storage.

## Installation

### Using `uv` (Recommended)

```bash
# Add to a uv-managed project
uv add "mydre-upload-sdk @ git+[https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python](https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python)"

# Or install directly into active virtualenv
uv pip install git+[https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python](https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python)

# Local editable install
git clone [https://github.com/flow4u/mydre-upload-sdk.git](https://github.com/flow4u/mydre-upload-sdk.git)
cd mydre-upload-sdk/python
uv pip install -e .
```

### Using `pip`


```bash
# Direct Installation from GitHub
pip install git+[https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python](https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python)

# Local Editable Installation
git clone [https://github.com/flow4u/mydre-upload-sdk.git](https://github.com/flow4u/mydre-upload-sdk.git)
cd mydre-upload-sdk/python
pip install -e .
```

## Configuration Setup
Create an `upload.json` file in your project. The library automatically supplies the default `base_url` (`https://andreanl-api-management.azure-api.net/v1`), so you only need to provide your workspace credentials.

### Option 1: Multi-Workspace Configuration (Recommended)
```json
{
  "DEMO_WORKSPACE": {
    "workspace_name": "dws-0001-DEMO",
    "workspace_key": "00000000-0000-0000-0000-000000000000",
    "subscription_key": "11111111222233334444555566667777"
  },
  "PROD_WORKSPACE": {
    "workspace_name": "dws-0002-PROD",
    "workspace_key": "88888888-8888-8888-8888-888888888888",
    "subscription_key": "99999999888877776666555544443333"
  }
}
```

### Option 2: Single-Workspace Configuration
```json
{
  "workspace_name": "dws-0001-DEMO",
  "workspace_key": "00000000-0000-0000-0000-000000000000",
  "subscription_key": "11111111222233334444555566667777"
}
```



## Quick Start Guide
Using the with `uploader.container()` context manager guarantees that temporary containers are allocated on block entry and finalized upon exit—preventing orphaned or uncommitted containers.

```Python
import json
import pandas as pd
from mydre_upload_sdk import WorkspaceUploader

# Load configuration
with open("upload.json", "r") as f:
    config = json.load(f)["DEMO_WORKSPACE"]

uploader = WorkspaceUploader(config)

# Context manager creates the container and commits it when exiting
with uploader.container(title="Monthly Report Sync") as container:
    # 1. Upload string content
    container.upload_text("Pipeline run complete.", filename="LOG.txt")

    # 2. Upload a pandas DataFrame directly as CSV
    df = pd.DataFrame({"Metric": ["SignIns", "VMs"], "Count": [142, 12]})
    container.upload_dataframe(df, filename="metrics.csv")

    # 3. Upload a local file from disk
    container.upload_file("./summary_report.pdf")

# Container is automatically committed here!
```

## API Reference
`WorkspaceUploader`

Main client interface for executing workspace operations.
```Python
uploader = WorkspaceUploader(workspace_config, auto_install_deps=True)
```
### Client Methods
* **`test_connection() -> bool`**<br />
Pings the workspace health endpoint `(GET /api/ping)`. Returns `True` if operational.
* **`list_containers() -> dict`**<br />
Retrieves metadata for active upload containers associated with the workspace.
* **`container(title: Optional[str] = None, commit_on_error: bool = True)`**<br />
  Context manager yielding a `ContainerSession` object. Handles creation, upload routing, and automated completion.

### `ContainerSession` (Context Manager Session)
Provided inside the `with uploader.container() as container:` block.
* **`container.upload_text(text_data: str, filename: str = 'my_text.txt') -> None`**<br />
  Uploads plain text content directly to Azure Blob Storage.
* **`container.upload_dataframe(df: pandas.DataFrame, filename: str = 'data.csv') -> None`**<br />
  Converts a pandas DataFrame into CSV format in memory and streams it directly to storage.
* **`container.upload_file(local_file_path: str, filename: Optional[str] = None) -> None`**<br />
  Uploads a file from local disk. Uses the local file name if `filename` is omitted.
* **`container.commit() -> requests.Response`**<br />
  Manually triggers container finalization prior to exiting the context block.
* **`container.delete() -> requests.Response`**<br />
  Cancels and deletes the current container and its uncommitted blobs prior to exiting the context block.

### Error Handling
All SDK operations raise exceptions derived from `WorkspaceUploadError`. When using the context manager, any exception raised inside the `with` block triggers automatic container cleanup before re-raising the original exception.

### Catching SDK Exceptions
```Python
from mydre_upload_sdk import (
    WorkspaceUploader,
    WorkspaceUploadError,
    APIError,
    BlobStorageError,
)

uploader = WorkspaceUploader(config)

try:
    with uploader.container(title="Sync Run") as container:
        container.upload_text("Processing...", filename="status.txt")
        container.upload_file("./non_existent_file.csv")  # Triggers FileNotFoundError

except APIError as err:
    # Handles API Management HTTP failures
    print(f"API Error (HTTP {err.status_code}): {err}")

except BlobStorageError as err:
    # Handles Azure Blob transfer failures
    print(f"Azure Storage Error: {err}")

except WorkspaceUploadError as err:
    # Catch-all for SDK base errors
    print(f"SDK Operation Failure: {err}")

except Exception as err:
    # Standard Python execution errors
    print(f"Execution Error: {err}")
```
### Exception Class Hierarchy
|Class | Base Class | Description|
|-----| --------|-------------|
`WorkspaceUploadError` | `Exception` | Base exception for all errors raised by this SDK. |
`APIError` | `WorkspaceUploadError` | Raised when REST API HTTP requests fail. Exposes `status_code` and `response_text`. |
`BlobStorageError` | `WorkspaceUploadError` | Raised when streaming data or files to Azure Blob Storage fails.| 

### Context Manager Error Behaviors
You can configure how partial uploads are handled when an error occurs during execution inside a `with` block:
1. **Save Partial Uploads (Default: `commit_on_error=True`)** <br />
   Commits all files successfully uploaded before the error occurred so data is not lost, then re-raises the exception.
   ```Python
   with uploader.container(title="Partial Save Run", commit_on_error=True) as container:
    container.upload_text("Saved log", filename="log.txt")
    raise RuntimeError("Unexpected failure")
    # 'log.txt' remains committed to the workspace
   ```
2. **Rollback / Discard Uploads (`commit_on_error=False`)** <br />
   Deletes the temporary container entirely on failure, ensuring incomplete data batches are discarded.
   ```Python
   with uploader.container(title="Transactional Run", commit_on_error=False) as container:
    container.upload_text("Temporary log", filename="log.txt")
    raise RuntimeError("Unexpected failure")
    # Container is deleted; 'log.txt' is discarded
   ```

