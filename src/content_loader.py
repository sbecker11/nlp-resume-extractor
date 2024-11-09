"""
Module for loading resume content from
MicrosoftWord docx file and
PDF file formats.
"""

import logging
from docx import Document
from pdfminer.high_level import extract_text

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)


def load_docx_data(file_path: str) -> str:
    """
    Load the content of a DOCX file.

    Args:
        file_path (str): The path to the DOCX file.

    Returns:
        str: The content of the DOCX file as a string.
        
    Exceptions raised:
        ValueError: If there is an error reading the DOCX file
    """
    try:
        doc = Document(file_path)
        if doc is None:
            raise ValueError("Error reading DOCX file")
        
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        content_str = '\n'.join(content)
        logging.info("Content Str type: %s", type(content_str))
        logging.info("Content Str len: %d", len(content_str))
        logging.info("Content Str[:1000]: [[%s]]", content_str[:1000])
        return content_str
    except Exception as e:
        logging.error("Error reading DOCX file: %s", e)
        raise e

def load_pdf_data(file_path: str) -> str:
    """
    Load the content of a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The content of the PDF file as a string.
    
    Exceptions raised:
        Exception: If there is an error reading the DOCX file

    """
    try:
        return extract_text(file_path)
    except Exception as e:
        logging.error("Error reading PDF file: %s", e)
        raise e
