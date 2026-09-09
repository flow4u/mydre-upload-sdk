import json
import os
import pandas as pd
from mydre_upload_sdk import WorkspaceUploader, WorkspaceUploadError

CONFIG_PATH = "../upload.json"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(
        f"Missing configuration file at '{CONFIG_PATH}'. "
        "Copy 'upload.json.template' to 'upload.json' and fill in your keys."
    )

with open(CONFIG_PATH, "r") as f:
    raw_config = json.load(f)

# Handle single-workspace or multi-workspace JSON structures
workspaces = {"DEFAULT": raw_config} if "workspace_name" in raw_config else raw_config

for alias, config in workspaces.items():
    print(f"\n--- Processing Workspace Alias: {alias} ---")
    
    if not config.get("subscription_key") or not config.get("workspace_key"):
        print(f"Skipping '{alias}': Missing API keys.")
        continue

    uploader = WorkspaceUploader(config)

    try:
        if uploader.test_connection():
            print("API connection active.")

        container_url = uploader.create_container(title=f"Batch Run ({alias})")
        print(f"Container created: {container_url}")

        uploader.upload_text(
            container_url=container_url,
            text_data="Dataset upload log entry.",
            filename="LOG.txt"
        )

        df = pd.DataFrame({
            "Record_ID": [101, 102, 103],
            "Status": ["Valid", "Valid", "Pending"]
        })
        uploader.upload_dataframe(
            container_url=container_url,
            df=df,
            filename="records.csv"
        )

        uploader.commit_container(container_url)
        print(f"Successfully committed data to {config['workspace_name']}.")

    except WorkspaceUploadError as err:
        print(f"Error processing workspace '{alias}': {err}")
