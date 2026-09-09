# myDRE Upload SDK

`mydre-upload-sdk` provides multi-language client libraries for uploading metrics, dataframes, and files to myDRE workspaces via Azure API Management and Blob Storage.

## Repository Layout

```text
mydre-upload-sdk/
├── python/    # Python package implementation
└── r/         # Reserved for future R package implementation
```

## Available SDKs


## Quick Start (Python)
Install directly from GitHub into any Python project or virtual environment:

Bash
pip install git+[https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python](https://github.com/flow4u/mydre-upload-sdk.git#subdirectory=python)
For full usage instructions, code examples, and API references, see the Python SDK Documentation.


## Available Implementations

| Language | Directory | Status | Installation Command |
| :--- | :--- | :--- | :--- |
| **Python** | `./python` | Ready | `pip install "git+[https://github.com/your-org/workspace-sdk.git#subdirectory=python](https://github.com/your-org/workspace-sdk.git#subdirectory=python)"` |
| **R** | `./r` | Planned | *TBD* |

---

## Quick Start (Python)

Navigate to the Python implementation directory or install directly via `pip`:

## Installation

```bash
pip install "git+[https://github.com/your-org/workspace-sdk.git#subdirectory=python](https://github.com/your-org/workspace-sdk.git#subdirectory=python)"
```

See the [Python SDK Documentation](./python/README.md) for detailed configuration options and multi-workspace examples.

---

### R Placeholder

**`/r/.gitkeep`**
*(Empty file created to maintain the directory structure in Git)*

---

### Python Package Files

**`/python/upload.json.template`**
```json
{
  "DEMO_WORKSPACE": {
    "workspace_name": "dws-0001-DEMO",
    "workspace_key": "00000000-0000-0000-0000-000000000000",
    "subscription_key": "11111111222233334444555566667777",
    "base_url": "https://your-apim-gateway.azure-api.net/v1"
  },
  "PRODUCTION_WORKSPACE": {
    "workspace_name": "dws-0002-PROD",
    "workspace_key": "88888888-8888-8888-8888-888888888888",
    "subscription_key": "99999999888877776666555544443333",
    "base_url": "https://your-apim-gateway.azure-api.net/v1"
  }
}
