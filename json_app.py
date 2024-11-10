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
from src.content_loader import load_docx_data
from src.json_schema_factory import JsonSchemaFactory, read_json_schema_file
from src.pydantic_resume import PydanticResume

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-2024-08-06"

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-2024-08-06"

def openai_process_resume_text(resume_content, resume_schema) -> Optional[dict]:
    """
    Process the given resume content and extract data per 
    given resume-schema using OpenAI's GPT-3.5.
    and returns the extracted data in the form of an object
    that conforms to the given resume-schema.

    Args:
        resume_content (str): The resume content to be processed.
        resume_schema (dict): The json-schema to be used for the output.

    Returns:
        resume_json: The extracted resume data in the form
        of an object that conforms to the given resume_schema.
    """
    response_format = {
        "type": "json_schema",
        "json_schema": resume_schema
    }

    messages = [
        { "role": "system", "content": "You are an expert assitant for taking 'Resume Text' and returning the extracted resume data in JSON format. \nYou extract data from the given 'Resume Text' and return it in a JSON format that conforms to the provided 'resume-schema'. \nREMEMBER to return extracted data only from provided 'Resume Text', and format the extracted data in JSON format as defined in 'resume-schema'" },
        { "role": "user", "content": f"Resume Text: \n------\n{resume_content}\n------" }
    ]

    # Expected type of response is a dictionary with a 'choices' key containing a list of dictionaries
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format=response_format
    )
    logging.info("isResponse: %s", response)
    if response is None:
        logging.error("Error no response from OpenAI")
        return None

    if not hasattr(response, 'choices') or not isinstance(response.choices, list):
        logging.error("Error no choices in response or choices is not a list")
        return None

    if len(response.choices) == 0:
        logging.error("Error no choices in response")
        return None

    if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
        logging.error("Error no message or content in response")
        return None

    extracted_resume_data = response.choices[0].message.content
    if extracted_resume_data is None:
        logging.error("Error no output from openai_process_resume_text")
        return None

    if "error" in extracted_resume_data:
        logging.error("Error: %s", extracted_resume_data['error'])
        return None

    if not isinstance(extracted_resume_data, dict):
        logging.error("Error output is not a dictionary")
        return None

    return extracted_resume_data


if __name__ == "__main__":
    resume_docx_path = "src/resume.docx"
    resume_schema_path = "src/resume-schema.json"
    # test_data_path = "src/test-data-object.json"

    try:
        factory = JsonSchemaFactory(resume_schema_path)
    except json.JSONDecodeError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except ValueError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error("Error: %s", e)
        sys.exit(1)

    resume_schema = read_json_schema_file(resume_schema_path)
    # resume_schema = factory.get_validated_json_schema()
    resume_text = load_docx_data(resume_docx_path)

    openai_extracted_data = openai_process_resume_text(
        resume_content=resume_text,
        resume_schema=resume_schema)

    if openai_extracted_data is None:
        logging.error("Error openai_extracted_data is null")
        sys.exit(1)
    if not isinstance(openai_extracted_data, dict):
        logging.error("Error openai_extracted_data is not a dict")
        sys.exit(1)

    # validate against the resume schema 
    if factory.validate_instance(openai_extracted_data) is False:
        logging.error("Error openai_extracted_data does not conform to the resume_schema")
        sys.exit(1)

    logging.info("SUCCESS!! openai_extracted_data conforms to the resume_schema!!")
    openai_resume_object = openai_extracted_data
    logging.info("openai_resume_object: \n%s", json.dumps(openai_resume_object, indent=2))
 
    # validate against the PydanticResume model
    pydantic_resume_object = PydanticResume(**openai_resume_object)
    if pydantic_resume_object is None:
        logging.error("Error pydantic_resume_object is null")
        sys.exit(1)
    logging.info("pydantic_resume_object type: %s", type(pydantic_resume_object))

    logging.info("pydantic_resume_object: \n%s", json.dumps(pydantic_resume_object, indent=2))
    
    logging.info("SUCCESS!! openai_resume_object conforms to the PydanticResume model!!")
    sys.exit(0)