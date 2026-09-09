# myDRE Upload SDK - Python Client

Python implementation for interacting with myDRE Workspace Upload APIs and Blob Storage.

## Installation

### Direct Installation from GitHub
```bash
pip install git+[https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python](https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python)
```

### Local Editable Installation
```bash
git clone [https://github.com/flow4u/mydre-upload-sdk.git](https://github.com/flow4u/mydre-upload-sdk.git)
cd mydre-upload-sdk/python
pip install -e .
```

## Configuration Setup
Create an upload.json file in your project using single or multi-workspace configurations:

### Multi-Workspace Configuration
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

## API Reference
### Initializing Client & Executing Uploads
```Python
import json
import pandas as pd
from mydre_upload_sdk import WorkspaceUploader

with open("upload.json", "r") as f:
    config = json.load(f)["DEMO_WORKSPACE"]

uploader = WorkspaceUploader(config)

# Workflow Execution
container_url = uploader.create_container(title="Sync Run")
uploader.upload_text(container_url, "Upload metadata", filename="meta.txt")

df = pd.DataFrame({"col1": [1, 2]})
uploader.upload_dataframe(container_url, df, filename="data.csv")

uploader.upload_file(container_url, "./local_file.pdf")
uploader.commit_container(container_url)
```

### Error Handling
```Python
from mydre_upload_sdk import WorkspaceUploadError, APIError, BlobStorageError

try:
    uploader.commit_container(container_url)
except APIError as e:
    print(f"API Error ({e.status_code}): {e}")
except BlobStorageError as e:
    print(f"Storage Error: {e}")
except WorkspaceUploadError as e:
    print(f"SDK Error: {e}")
```
