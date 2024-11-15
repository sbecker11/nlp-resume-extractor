"""
Module for processing a resume document and
extracting json-schema formatted output
using Groq's latest LLM
"""

import os
import json
import logging
import sys
import tiktoken

from typing import Optional
from devtools import debug
from dotenv import load_dotenv
from pydantic import ValidationError as PydanticValidationError
from groq import Groq
from src.content_loader import load_docx_data
from src.json_schema_factory import JsonSchemaFactory
from src.pydantic_resume import PydanticResume

load_dotenv()

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def groq_process_resume_text_1(
    resume_content :str, 
    resume_schema_str: str) -> Optional[dict]:

    messages=[
        {
            "role": "system",
            "content": "You are a recipe database that outputs resumes in JSON.\n"
            f" The JSON object must use the schema: {resume_schema_str}"
        },
        {
            "role": "user",
            "content": f"Resume Text: \\n------\\n{resume_content}\\n------"
        }
    ]

    response_format = {
        "type": "json_object",
        "schema": resume_schema_str,
    }

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    groq_client_model = "llama3-groq-8b-8192-tool-use-preview"

    max_putput_tokens = 8192 - len(resume_schema_str)
                                     
    response = groq_client.chat.completions.create(
        model=groq_client_model,
        messages=messages,
        temperature=0,
        max_tokens=max_putput_tokens,
        response_format=response_format
    )

    # Extracting and printing the JSON response
    try:
        json_response = json.loads(response.choices[0].message.content)
        return json_response
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        print(response.choices[0].message.content)
        return None


def groq_process_resume_text_2(
    resume_text: str, 
    resume_schema_str: str) -> Optional[dict]:
    messages = [
        {
            "role": "system",
            "content": f"You are a helper designed to provide structured JSON responses from this resume text: {resume_text}."
        },
        {
            "role": "user",
            "content": "The JSON response should be formatted as defined in the given json schema."
        }   
    ]
    
    response_format = {
        "type": "json_object",
        "schema": resume_schema_str
    }
    
    model = "llama3-groq-8b-8192-tool-use-preview"
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=8192,
        response_format=response_format
    )
    extracted_object = None
    try: 
        extracted_json_str = response.choices[0].message.content
        extracted_object = json.loads(extracted_json_str)
    except KeyError as e:
        print(e)
    return extracted_object



if __name__ == "__main__":

    resume_docx_path = os.getenv("RESUME_DOCX_PATH")
    resume_schema_path = os.getenv("RESUME_CONTACT_INFOROMATION_SCHEMA_PATH")
    # test_data_object_path = os.getenv("TEST_DATA_OBJECT_PATH")
    test_data_object_path = None
    
    # validate the resume schema
    if not resume_schema_path:
        logging.error("Error: RESUME_SCHEMA_PATH is not set")
        sys.exit(1)

    try:
        factory = JsonSchemaFactory(
            resume_schema_path, 
            test_data_object_path)
        
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
    resume_schema_str = json.dumps(resume_schema, indent=2)

    # Load the resume content from the DOCX file
    if not resume_docx_path:
        logging.error("Error: RESUME_DOCX_PATH is not set")
        sys.exit(1)
    resume_text = load_docx_data(resume_docx_path)

    ## call groq_process_resume_text to extract the resume data
    ## from the resume text using groq_client_model the resume schema
    groq_extracted_object = groq_process_resume_text_2(
        resume_text=resume_text,
        resume_schema_str=resume_schema_str)

    if groq_extracted_object is None:
        logging.error("Error groq_extracted_object is null")
        sys.exit(1)
        
    mainSchemaTitle = '"title": "Resume"'
    sectionSchemas = [
        {
            "title": "ResumeContactInformationSchema",
            "file": "resume_contact_information_schema.json"
        }
    ]
    
    if "ResumeContactInformationSchema" in resume_schema_str:
        logging.info("validating groq_extracted_object against the current resume schema")
    
    keep_validating = True
    if keep_validating:
        if factory.validate_instance(groq_extracted_object) is False:
            logging.error("Error: groq_extracted_object does not conform to the resume_schema")
            keep_validating = False
        else:
            logging.info("SUCCESS!! groq_extracted_object conforms to the resume_schema!!")
    
    
    if keep_validating:
        # rename the groq_extracted_data to groq_resume_object
        groq_resume_object = groq_extracted_object
        logging.info("groq_resume_object:")
        logging.info(json.dumps(groq_resume_object, indent=2))

    # validate the groq_resume_object against the PydanticResume model
    # by testing if a pudandic_resume_object is created without errors
    try:
        pydantic_resume_object = PydanticResume(**groq_resume_object)

        # pydantic models are not json serializable, so using devtools.debug instead
        logging.info("pydantic_resume_object:")
        debug(pydantic_resume_object)

        print("SUCCESS groq_resume_object is valid against the PydanticResume model")

    except PydanticValidationError as e:
        print("groq_resume_object is invalid against the PydanticResume model.")
        print(str(e))
        exit(1)

print("!!! DONE !!!")
