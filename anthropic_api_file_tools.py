import subprocess
import anthropic
import mimetypes
import os
import pandas as pd
from tabulate import tabulate

# Test the API
def test_api(client, file_id=None):

    # Send a test message to the Anthropic API
    try:
        if not file_id:
            # If no file ID is provided, just test the API connection
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Hello! Please respond with 'API test successful' if you can read this."}
                ]
            )
            # Check if the response is successful
            print("API test successful!")
            print(f"Response by Claude: {response.content[0].text}")
        else:
            # If a file ID is provided, test the file handling
            response = client.beta.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Give a short summary of the attached file."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "file",
                                    "file_id":  f"""{file_id}"""
                                }
                            }
                        ]
                    }
                ],
                betas=["files-api-2025-04-14"],
            )
            # Check if the response is successful
            print("API test successful!")
            print(f"Response by Claude: {response.content[0].text}")

    except Exception as e:
        print(f"API test failed: {e}")

# Function for uploading files to the Anthropic API Workspace
def upload_file_to_workspace(client, file_path) -> str:

    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return

    # Get the file name from the file path
    file_name = file_path.split("/")[-1]

    # Guess the file type based on the file extension
    file_type = mimetypes.guess_type(file_name)[0]
    if file_type == "text/markdown":
        file_type = "text/plain"
    if file_type == "application/json":
        file_type = "text/plain"
    if file_type != 'application/pdf' and file_type != 'text/plain':
        print("Unsupported file type. Only PDF and text files are allowed.")
        return

    # Upload the file to the Anthropic API Workspace
    try:
        result = client.beta.files.upload(
            file=(file_name, open(file_path, "rb"), file_type))
        file_id = result.id if hasattr(result, 'id') else result["id"]
        print(f"File uploaded successfully: {file_name}")
        print(f"File ID: {file_id}")
        return file_id
    except Exception as e:
        print(f"File upload failed: {e}")
        return None

# List files in the Anthropic API Workspace
def list_files_in_workspace(client):
    try:
        page = client.beta.files.list()
        print("Files currently uploaded to the Anthropic API Workspace:")
        
        files_dict = {}
        for file in page:
            created_at = file.created_at.strftime('%Y-%m-%d %H:%M:%S')
            files_dict[file.id] = {
                "created_at": created_at,
                "filename": file.filename,
                "mime_type": file.mime_type,
                "size_bytes": file.size_bytes,
                "type": file.type,
                "downloadable": file.downloadable
            }      
        df = pd.DataFrame.from_dict(files_dict, orient='index')
        df = df.rename(columns={
            "created_at": "Created",
            "filename": "File Name",
            "mime_type": "MIME Type",
            "size_bytes": "Size (bytes)",
            "type": "Type",
            "downloadable": "Downloadable"
        })
        df = df.reset_index().rename(columns={"index": "File ID"})
        print(df.to_markdown(tablefmt="grid"))
    except Exception as e:
        print(f"Failed to list files: {e}")

# Delete a file from the Anthropic API Workspace
def delete_file_from_workspace(client, file_id):
    try:
        client.beta.files.delete(file_id=file_id)
        print(f"File with ID {file_id} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete file: {e}")

# Delete all files from the Anthropic API Workspace
def delete_all_files_from_workspace(client):
    try:
        page = client.beta.files.list()
        for file in page:
            client.beta.files.delete(file_id=file.id)
            print(f"Deleted file with ID {file.id}")
    except Exception as e:
        print(f"Failed to delete files: {e}")
