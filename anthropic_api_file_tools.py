import subprocess
import anthropic
import mimetypes
import os
import pandas as pd
from tabulate import tabulate

# Function test_api: Test the Anthropic beta files API
def test_api(client, file_id=None):
    """
    Test the Anthropic API connection and file handling capabilities.

    This function sends a test message to the Anthropic API using the provided client object.
    - If no file_id is provided, it sends a simple test message to verify the API connection.
    - If a file_id is provided, it sends a message that references the uploaded file and requests a summary, testing file attachment and retrieval.

    Args:
        client (anthropic.Anthropic):
            An initialized Anthropic API client object.
        file_id (str, optional):
            The ID of a file previously uploaded to the Anthropic workspace. If provided, the function will test file referencing in the API call.

    Returns:
        None. Prints the result of the API call to stdout.

    Example usage:
        >>> client = anthropic.Anthropic(api_key="...your key...")
        >>> test_api(client)
        >>> test_api(client, file_id="file-abc123")

    Raises:
        Prints an error message if the API call fails.
    """
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

# Function upload_file_to_workspace: Uploading files to the Anthropic API Workspace
def upload_file_to_workspace(client, file_path) -> str:
    """
    Upload a file to the Anthropic API Workspace.

    This function uploads a file to the Anthropic API Workspace using the provided client object.
    It checks for file existence, determines the MIME type, and ensures compatibility with the API's supported file types.
    If the file type is not natively supported but can be converted to plain text (e.g., markdown or JSON), it is converted accordingly.

    Args:
        client (anthropic.Anthropic):
            An initialized Anthropic API client object.
        file_path (str):
            The absolute or relative path to the file to be uploaded.

    Returns:
        str or None: The file ID assigned by the Anthropic API if upload is successful, otherwise None.

    Example usage:
        >>> client = anthropic.Anthropic(api_key="...your key...")
        >>> file_id = upload_file_to_workspace(client, "./test.pdf")
        >>> print(file_id)

    Notes:
        - Only PDF and plain text files are supported for upload. Markdown and JSON files are converted to plain text.
        - Prints status messages to stdout regarding upload success or failure.

    Raises:
        Prints an error message if the file does not exist, is of an unsupported type, or if the upload fails.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return

    # Get the file name from the file path
    file_name = file_path.split("/")[-1]

    # Guess the file type based on the file extension
    file_type = mimetypes.guess_type(file_name)[0]
    # Currently Anthropic's beta files API only supports following file types: PDF (application/pdf), text (text/plain), images (image/jpeg, image/png, image/gif, image/webp) and various for datasets (https://docs.anthropic.com/en/docs/build-with-claude/files). To overcome this limitation, we convert some other file types to text/plain. This makes them generally usable and understandable for Claude (tested), but possibly results in limited functionality than native support (not tested).
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

# Function delete_file_from_workspace: Delete a single file from the Anthropic API Workspace
def delete_file_from_workspace(client, file_id):
    """
    Delete a single file from the Anthropic API Workspace.

    This function deletes a file from the Anthropic API Workspace using the provided client object and file ID.
    It attempts to remove the file and prints a status message indicating success or failure.

    Args:
        client (anthropic.Anthropic):
            An initialized Anthropic API client object.
        file_id (str):
            The ID of the file to be deleted from the workspace.

    Returns:
        None. Prints the result of the deletion to stdout.

    Example usage:
        >>> client = anthropic.Anthropic(api_key="...your key...")
        >>> delete_file_from_workspace(client, "file-abc123")

    Raises:
        Prints an error message if the deletion fails.
    """
    try:
        client.beta.files.delete(file_id=file_id)
        print(f"File with ID {file_id} deleted successfully.")
    except Exception as e:
        print(f"Failed to delete file: {e}")

# Function delete_all_files_from_workspace: Delete all files from the Anthropic API Workspace
def delete_all_files_from_workspace(client):
    """
    Delete all files from the Anthropic API Workspace.

    This function deletes every file currently stored in the Anthropic API Workspace using the provided client object.
    It iterates through all files and attempts to remove each one, printing a status message for each deletion and a summary upon completion.

    Args:
        client (anthropic.Anthropic):
            An initialized Anthropic API client object.

    Returns:
        None. Prints the result of each deletion and a summary to stdout.

    Example usage:
        >>> client = anthropic.Anthropic(api_key="...your key...")
        >>> delete_all_files_from_workspace(client)

    Raises:
        Prints an error message if any deletion fails.
    """
    try:
        page = client.beta.files.list()
        for file in page:
            client.beta.files.delete(file_id=file.id)
            print(f"Deleted file with ID {file.id}")
    except Exception as e:
        print(f"Failed to delete files: {e}")
    print(f"All files deleted successfully.")
