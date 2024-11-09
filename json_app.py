"""
Module for processing a resume document and 
extracting json-schema formatted output 
using OpenAI's GPT-3.5.
"""

import os
import json
import logging
import sys
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-2024-08-06"
from src.content_loader import load_docx_data
# from gpt4all import GPT4All

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-2024-08-06"

def process_resume_text(resume_content, resume_schema) -> Optional[dict]:
    """
    Process the given resume content and extract data per 
    given named-resume-schema using OpenAI's GPT-3.5.
    and returns the extracted data in the form of an object
    that conforms to the given named-resume-schema.

    Args:
        resume_content (str): The resume content to be processed.
        resume_schema (dict): The json-schema to be used for the output.

    Returns:
        resume_json: The extracted resume data in the form
        of an object that conforms to the given resume_schema.
    """
    response_format = {
        "type": "json_schema",
        "json_schema_name": "named-resume-schema",
        "json_schema": resume_schema
    }

    messages = [
        { "role": "system", "content": "You are an expert assitant for taking 'Resume Text' and returning the extracted resume data in JSON format. \nYou extract data from the given 'Resume Text' and return it in a JSON format that conforms to the provided 'named-resume-schema'. \nREMEMBER to return extracted data only from provided 'Resume Text', and format the extracted data in JSON format as defined in 'named-resume-schema'" },
        { "role": "user", "content": f"Resume Text: \n------\n{resume_content}\n------" }
    ]

    # Expected type of response is a dictionary with a 'choices' key containing a list of dictionaries
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format=response_format
    )
    extracted_resume_data = response['choices'][0]['message']['content']
    if extracted_resume_data is None:
        logging.error("Error no output from process_resume_text")
        return None
    if "error" in extracted_resume_data:
        logging.error("Error: %s", extracted_resume_data['error'])
        return None
    if not isinstance(extracted_resume_data, dict):
        logging.error("Error output is not a dictionary")
        return None

    # The caller will check if the extracted
    # data is valid against the schema
    return extracted_resume_data



if __name__ == "__main__":
    JSON_SCHEMA_PATH = "src/new-resume-schema.json"
    # TEST_DATA_OBJECT_PATH = "src/test-data-object.json"

    try:
        FACTORY = JsonSchemaFactory(JSON_SCHEMA_PATH)
    except json.JSONDecodeError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except ValueError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error("Error: %s", e)
        sys.exit(1)

    RESUME_SCHEMA = FACTORY.get_validated_json_schema()

    RESUME_TEXT = load_docx_data("resume.docx")

    extracted_data = process_resume_text(
        resume_content=RESUME_TEXT,
        resume_schema=RESUME_SCHEMA)

    if extracted_data is None:
        logging.error("Error no extracted_data from process_resume_text")
        sys.exit(1)

    resume_object = extracted_data
    if FACTORY.validate_instance(resume_object) is False:
        logging.error("Error extracted data does not conform to the resume_schema")
        sys.exit(1)

    logging.info("SUCCESS!! Extracted data conforms to the resume_schema!!")
    logging.info("Extracted data: \n%s", json.dumps(resume_object, indent=2))
