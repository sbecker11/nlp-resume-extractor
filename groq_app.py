"""
Module for processing a resume document and 
extracting json-schema formatted output 
using Groq's latest LLM
"""

import os
import json
import logging
import sys
from devtools import debug
from dotenv import load_dotenv
from src.content_loader import load_docx_data
from src.json_schema_factory import JsonSchemaFactory
from src.pydantic_resume import PydanticResume
from pydantic import ValidationError as PydanticValidationError
from groq import Groq
from typing import Optional

load_dotenv()

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

def groq_process_resume_text(resume_content, resume_schema) -> Optional[dict]:

    if isinstance(resume_schema, dict) is False:
        # pretty-printed json schema works best 
        resume_schema = json.dumps(resume_schema, indent=2)
        
    groq_client = Groq(api_key=os.getenv("GROC_API_KEY"))
    groq_client_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    
    completion = groq_client.chat.completions.create(
        model=groq_client_model,
        messages=[
            {
                "role": "system",
                "content": "You are a recipe database that outputs recipes in JSON.\n"
                f" The JSON object must use the schema: {resume_schema}"
            },
            {
                "role": "user",
                "content": f"Resume Text: \\n------\\n{resume_content}\\n------"
            }
        ],
        temperature=0,
        max_tokens=9024,
        top_p=1,
        stream=False,
        response_format={
            "type": "json_object",
            "schema": resume_schema,
        },
        stop=None,
    )
    
    json_str = ""
    for chunk in completion:
        json_str += chunk.choices[0].delta.content
    
    extracted_object = json.loads(json_str)
    return extracted_object


if __name__ == "__main__":
    
    resume_docx_path = os.getenv("RESUME_DOCX_PATH")
    resume_schema_path = os.getenv("RESUME_SCHEMA_PATH")
    test_data_object_path = os.getenv("TEST_DATA_OBJECT_PATH")

    # validate the resume schema
    try:
        factory = JsonSchemaFactory(resume_schema_path, test_data_object_path)
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

    ## call groq_process_resume_text to extract the resume data 
    ## from the resume text using groq_client_model the resume schema
    groq_extracted_object = groq_process_resume_text(
        resume_content=resume_text,
        resume_schema=resume_schema)

    if groq_extracted_object is None:
        logging.error("Error groq_extracted_object is null")
        sys.exit(1)
    
    # validate the groq_extracted_pbkect against the resume schema 
    if factory.validate_instance(groq_extracted_object) is False:
        logging.error("Error groq_extracted_object does not conform to the resume_schema")
        sys.exit(1)

    logging.info("SUCCESS!! groq_extracted_object conforms to the resume_schema!!")
    
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
