# AnthropicAPIFileTools

A simple Python helper package for working with the Anthropic API's file upload features. The Anthropic files API is still new and in beta, so these basic wrapper functions are for convenience when uploading, listing, and deleting files in your Anthropic workspace.

## Why?
The Anthropic files API is still in beta, therefore limited in functionality and documentation. The provided wrapper functions make it easier to:
- Upload PDF and text files (also accepting markdown and JSON)
- List your uploaded files in a readable table
- Delete individual files or clear your workspace
- Test your API connection and file referencing with Claude

## References
- [Anthropic API documentation](https://docs.anthropic.com/en/api/overview)
- [Anthropic API Files documentation](https://docs.anthropic.com/en/docs/build-with-claude/files)

## Third-Party Dependencies and Legal Notice
This package uses the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) to interact with the Claude API. Use of the Anthropic API is subject to [Anthropic's Terms of Service](https://www.anthropic.com/legal/terms-of-service) and [API documentation](https://docs.anthropic.com/en/api/overview). You must have your own valid API key and comply with all applicable terms. This package does not include or redistribute any Anthropic proprietary code.

## Installation
Clone this repository and install the package in editable mode:

```bash
cd AnthropicAPIFileTools
pip install -e .
```

## Usage
Import the package and initialize the Anthropic client:

```python
import anthropic
from AnthropicAPIFileTools.anthropic_api_file_tools import (
    test_api,
    upload_file_to_workspace,
    list_files_in_workspace,
    delete_file_from_workspace,
    delete_all_files_from_workspace
)

client = anthropic.Anthropic(api_key="YOUR_API_KEY")
```

### Example operations
```python
# Test API connection
test_api(client)

# Upload a file
file_id = upload_file_to_workspace(client, "./test.pdf")

# List files
list_files_in_workspace(client)

# Delete a file
delete_file_from_workspace(client, file_id)

# Delete all files
delete_all_files_from_workspace(client)
```

## Supported File Types
- PDF (`application/pdf`)
- Plain text (`text/plain`)
- Markdown and JSON files are auto-converted to plain text for upload

## Notes
- These are just simple wrappers for convenience, not a full-featured SDK.
- The package prints status and error messages to stdout for all operations.
- For details on each function, use Python's built-in `help()` function, e.g. `help(upload_file_to_workspace)`.
- Requires Python 3.8+ and the `anthropic` and `pandas` packages.

## License
MIT License
