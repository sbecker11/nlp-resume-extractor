"""
Module for processing a resume document and 
extracting json-schema formatted output 
using OpenAI's GPT-3.5.
"""

import os
import json
import logging
import sys
from devtools import debug
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from src.content_loader import load_docx_data
from src.json_schema_factory import JsonSchemaFactory, read_json_schema_file
from src.pydantic_resume import PydanticResume
from pydantic import ValidationError as PydanticValidationError


load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_client_model = "gpt-4o-2024-08-06"

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

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
        "json_schema": {
            "name": "resume-schema",
            "schema": resume_schema
        }
    }

    messages = [
        { "role": "system", "content": "You are an expert assitant for taking 'Resume Text' and returning the extracted resume data in JSON format. \nYou extract data from the given 'Resume Text' and return it in a JSON format that conforms to the provided 'resume-schema'. \nREMEMBER to return extracted data only from provided 'Resume Text', and format the extracted data in JSON format as defined in 'resume-schema'" },
        { "role": "user", "content": f"Resume Text: \n------\n{resume_content}\n------" }
    ]

    response =  openai_client.chat.completions.create(
        model=openai_client_model,
        messages=messages,
        response_format=response_format
    )
    
    logging.info("isResponse: %s", response)
    
    # Expected resoonse is a non-null dictionary with a 'choices' key containing a list of dictionaries
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

    extracted_data = response.choices[0].message.content
    if extracted_data is None:
        logging.error("Error no extracted data in response")
        return None
        logging.error("Error no output from openai_process_resume_text")
        return None

    if "error" in extracted_data:
        logging.error("Error: %s", extracted_data['error'])
        return None

    extracted_object = None
    if isinstance(extracted_data, dict):
        extracted_object = extracted_data
    elif isinstance(extracted_data, str):
        try:
            extracted_object = json.loads(extracted_data)
        except json.JSONDecodeError as e:
            logging.error("Error extracted_data is a string that cannot be converted to a dict. error: %s", str(e) )
            return None 
    else:
        logging.error("Error extracted_data is not a dict or string")
        return None
    

    ## !!! Success !!! 
    # caller validates the extracted_object against the resume_schema
    return extracted_object


if __name__ == "__main__":
    resume_docx_path = "src/resume.docx"
    resume_schema_path = "src/resume-schema.json"
    # test_data_path = "src/test-data-object.json"

    # validate the resume schema
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

    # get the validated resume schema
    resume_schema = factory.get_validated_json_schema()
    
    # Load the resume content from the DOCX file
    resume_text = load_docx_data(resume_docx_path)

    ## call openai_process_resume_text to extract the resume data 
    ## from the resume text using openai_client_model the resume schema
    openai_extracted_object = openai_process_resume_text(
        resume_content=resume_text,
        resume_schema=resume_schema)

    if openai_extracted_object is None:
        logging.error("Error openai_extracted_object is null")
        sys.exit(1)
    
    # validate the openai_extracted_pbkect against the resume schema 
    if factory.validate_instance(openai_extracted_object) is False:
        logging.error("Error openai_extracted_object does not conform to the resume_schema")
        sys.exit(1)

    logging.info("SUCCESS!! openai_extracted_object conforms to the resume_schema!!")
    
    # rename the openai_extracted_data to openai_resume_object
    openai_resume_object = openai_extracted_object
    logging.info("openai_resume_object:")
    logging.info(json.dumps(openai_resume_object, indent=2))
 
    # validate the openai_resume_object against the PydanticResume model
    # by testing if a pudandic_resume_object is created without errors
    try:
        pydantic_resume_object = PydanticResume(**openai_resume_object)
        
        # pydantic models are not json serializable, so using devtools.debug instead
        logging.info("pydantic_resume_object:")
        debug(pydantic_resume_object)
        
        print("SUCCESS openai_resume_object is valid against the PydanticResume model")

    except PydanticValidationError as e:
        print("openai_resume_object is invalid against the PydanticResume model.")
        print(str(e))
        exit(1)
        
print("!!! DONE !!!")