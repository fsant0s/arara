# Required libraries:
# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os
import re # For URL parsing
from typing import List, Union, Dict, Any, Optional

# Imports as per the previous example
from .skill import Skill
from agents import BaseAgent # Make sure this import matches your project structure

# Google-specific imports
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False
    # Allows module import, but class instantiation will fail
    Credentials = None #type: ignore
    build = None #type: ignore
    HttpError = None #type: ignore


class GoogleDocsReader(Skill):
    """
    A skill that enables an agent to read the content of Google Docs documents,
    provided as URLs, and incorporate them into its context.
    """

    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    def _extract_doc_id_from_url(self, url: str) -> Optional[str]:
        """
        Extracts the Google Document ID from a URL.
        Example: https://docs.google.com/document/d/1pAsptw5QUqHWSx-aj47SFbHEUGDvep6q8gHhI5tVE5A/edit
        The ID is typically between /d/ and the next /.
        """
        # Regex to find the document ID in common Google Docs URL patterns
        match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return match.group(1)
        return None

    def __init__(
        self,
        urls: Union[str, List[str]],
        credentials_path: Optional[str] = None,
        credentials_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes the GoogleDocsReader skill.

        Args:
            urls (Union[str, List[str]]): A single Google Docs URL or a list of URLs.
                                          The document ID will be extracted from these URLs.
            credentials_path (Optional[str]): Path to the Google Cloud service account key JSON file.
                                              If None, will try `credentials_info` or the
                                              GOOGLE_APPLICATION_CREDENTIALS environment variable.
            credentials_info (Optional[Dict[str, Any]]): A dictionary containing the service account information
                                                       (content of the JSON file). Ignored if `credentials_path` is provided.

        Raises:
            ImportError: If the required Google libraries are not installed.
            ValueError: If URLs are invalid, document IDs cannot be extracted, or credentials cannot be resolved.
            RuntimeError: If the Google Docs service fails to initialize.
        """
        super().__init__()

        if not GOOGLE_LIBS_AVAILABLE:
            raise ImportError(
                "Google libraries not found. Please install them with: "
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )

        # --- URL Parsing and Document ID Extraction ---
        self._document_ids: List[str] = []
        input_urls_list: List[str]

        if isinstance(urls, str):
            if not urls.strip():
                raise ValueError("If 'urls' is a string, it must not be empty.")
            input_urls_list = [urls.strip()]
        elif isinstance(urls, list):
            if not urls:
                raise ValueError("If 'urls' is a list, it must not be empty.")
            if not all(isinstance(u, str) and u.strip() for u in urls):
                raise ValueError("Each URL in the list must be a non-empty string.")
            input_urls_list = [u.strip() for u in urls]
        else:
            raise TypeError(
                f"Expected 'urls' to be a string or list of strings, but got {type(urls).__name__}."
            )

        for url in input_urls_list:
            doc_id = self._extract_doc_id_from_url(url)
            if doc_id:
                self._document_ids.append(doc_id)
            else:
                raise ValueError(f"Could not extract a valid Google Doc ID from URL: {url}")

        if not self._document_ids:
            raise ValueError("No valid Google Doc IDs could be extracted from the provided URLs.")
        # --- End of URL Parsing ---


        # --- Credentials Handling ---
        creds = None
        if credentials_path:
            if not os.path.exists(credentials_path):
                raise ValueError(f"Credentials file not found at: {credentials_path}")
            creds = Credentials.from_service_account_file(credentials_path, scopes=self.SCOPES)
        elif credentials_info:
            creds = Credentials.from_service_account_info(credentials_info, scopes=self.SCOPES)
        else:
            gac_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if gac_path and os.path.exists(gac_path):
                creds = Credentials.from_service_account_file(gac_path, scopes=self.SCOPES)
            else:
                raise ValueError(
                    "Google credentials not provided. Set 'credentials_path', 'credentials_info', "
                    "or the GOOGLE_APPLICATION_CREDENTIALS environment variable with a valid path."
                )

        if not creds: # Final check
             raise ValueError("Failed to load Google credentials.")
        self._credentials = creds
        # --- End of Credentials Handling ---

        try:
            # cache_discovery=False is recommended to avoid issues with discovery cache in long-running applications
            self._service = build('docs', 'v1', credentials=self._credentials, cache_discovery=False)
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Docs service: {e}")

    def _extract_text_from_elements(self, elements: List[Dict[str, Any]]) -> str:
        """Extracts text from a list of paragraph elements or cell content."""
        text_content = ""
        for element in elements:
            if 'textRun' in element:
                text_run = element.get('textRun', {})
                text_content += text_run.get('content', '')
        return text_content

    def _extract_text_from_doc_body(self, body_content: List[Dict[str, Any]]) -> str:
        """Extracts plain text from the body content of a Google Doc."""
        doc_text_parts = []
        for element in body_content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                paragraph_text = ""
                prefix = ""

                if 'bullet' in paragraph and paragraph['bullet']:
                    prefix = "- " # Simple marker for list item

                elements = paragraph.get('elements', [])
                paragraph_text = self._extract_text_from_elements(elements)

                if paragraph_text.strip(): # Only add if there's actual text
                    doc_text_parts.append(prefix + paragraph_text)
                elif prefix: # Add if it was a bullet point, even if empty (e.g. empty list item)
                    doc_text_parts.append(prefix.strip())


            elif 'table' in element:
                # Basic table extraction
                table = element['table']
                table_representation = ["[Start of Table]"]
                for row_index, row in enumerate(table.get('tableRows', [])):
                    row_cells_text = []
                    for cell in row.get('tableCells', []):
                        # Cell content is a list of StructuralElement
                        cell_content_elements = cell.get('content', [])
                        cell_text = self._extract_text_from_doc_body(cell_content_elements) # Recursive call for cell content
                        row_cells_text.append(cell_text.strip().replace('\n', ' / ')) # Removes internal newlines from the cell
                    if any(cell_text for cell_text in row_cells_text): # Adds row if any cell has content
                        table_representation.append(f"  Row {row_index + 1}: | " + " | ".join(row_cells_text) + " |")
                table_representation.append("[End of Table]")
                doc_text_parts.append("\n".join(table_representation))

        return "\n".join(doc_text_parts)

    def on_add_to_agent(self, agent: BaseAgent) -> None:
        """
        Registers this skill's document reading functionality with the agent.
        Assumes self._agent has already been set by the Skill base class or agent framework.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Expected parameter 'agent' to be of type 'BaseAgent', but got {type(agent).__name__}."
            )

        if not hasattr(self, '_agent') or self._agent is None:
            super().on_add_to_agent(agent) # Ensures self._agent is set if the base Skill does this.

        self._agent.register_hook( # type: ignore
            hookable_method="process_all_messages_before_reply", # Or another appropriate hook
            hook=self.read_docs_and_collate_content
        )

    def read_docs_and_collate_content(
        self,
        processed_messages: Union[List[Dict[str, Any]], Dict[str, Any], str]
    ) -> List[Dict[str, Any]]:
        """
        Reads the configured Google Docs (using internally stored IDs from URLs),
        formats their content, and appends it to the processed messages.
        Normalizes processed messages to a list of message dictionaries.
        """
        all_docs_content_strings = []

        for doc_id in self._document_ids: # Iterates over the extracted IDs
            try:
                fields_to_fetch = "documentId,title,body(content(paragraph(elements(textRun(content,textStyle),inlineObjectElement),bullet),table(tableRows(tableCells(content(paragraph(elements(textRun(content,textStyle),inlineObjectElement),bullet)))))))"

                document = self._service.documents().get(documentId=doc_id, fields=fields_to_fetch).execute() # type: ignore

                title = document.get('title', 'Untitled Document')
                doc_body_content = document.get('body', {}).get('content', [])

                extracted_text = self._extract_text_from_doc_body(doc_body_content)

                doc_info_string = (
                    f"--- Google Doc Content ---\n"
                    f"Document ID: {doc_id}\n" # Displaying the ID can be useful for debugging
                    f"Title: {title}\n\n"
                    f"{extracted_text}\n"
                    f"--- End of Google Doc Content ---"
                )
                all_docs_content_strings.append(doc_info_string)

            except HttpError as e: # type: ignore
                error_reason = e._get_reason() if hasattr(e, '_get_reason') else str(e)
                error_message = f"[Error reading Google Doc ID '{doc_id}': Status {e.resp.status} - {error_reason}]"
                all_docs_content_strings.append(error_message)
            except Exception as e:
                error_message = f"[Unexpected error reading Google Doc ID '{doc_id}': {type(e).__name__} - {str(e)}]"
                all_docs_content_strings.append(error_message)

        collated_content = "\n\n".join(all_docs_content_strings)

        if not collated_content:
            collated_content = "No content was extracted from the specified Google Docs."

        system_response_part = [{
            "content": collated_content,
            "role": "system"
        }]

        return processed_messages + system_response_part
