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
    config = json.load(f)

# Initialize client
uploader = WorkspaceUploader(config)

try:
    # 1. Test ping endpoint
    if uploader.test_connection():
        print("Successfully pinged workspace API.")

    # 2. List current workspace containers
    containers = uploader.list_containers()
    print("Active containers:", containers)

    # 3. Create a new temporary upload container
    container_url = uploader.create_container(title="Automated Data Run")
    print(f"Created container URL: {container_url}")

    # 4. Upload string content
    uploader.upload_text(
        container_url=container_url,
        text_data="Pipeline completed successfully on 2026-09-09.",
        filename="LOG.txt"
    )

    # 5. Upload pandas DataFrame
    df = pd.DataFrame({
        "User_ID": [10, 20, 30],
        "Access_Level": ["Admin", "User", "User"]
    })
    uploader.upload_dataframe(
        container_url=container_url,
        df=df,
        filename="users_summary.csv"
    )

    # 6. Upload a local file
    temp_file = "sample_local_doc.txt"
    with open(temp_file, "w") as f:
        f.write("Local sample document content.")

    uploader.upload_file(
        container_url=container_url,
        local_file_path=temp_file,
        filename="sample_doc_uploaded.txt"
    )
    os.remove(temp_file)

    # 7. Commit changes to workspace
    uploader.commit_container(container_url)
    print("Container successfully committed!")

except WorkspaceUploadError as error:
    print(f"myDRE SDK Operation failed: {error}")
