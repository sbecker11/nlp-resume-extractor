"""
Module for processing a resume document and
extracting json-schema formatted output
using Groq's latest LLM
"""

import os
import json
import logging
import tiktoken

from typing import Optional
from devtools import debug
from dotenv import load_dotenv
import src.json_schema as json_schema

from pydantic import ValidationError as PydanticValidationError
from groq import Groq
from src.content_loader import load_docx_data
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

def groq_process_resume_text(
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

def test_schema_def(schema_def):
    """
    given a schema_def object, 
        tests the resume_schema with resume_text
        and attempts to extract a resume object 
        usng the groq_process_resume_text function.
        if successful, saves the extracted object 
        to the results_path and returns the 
        extracted object, otherwise None 

    Args:
        schema_def (pbkect): with the following fields:
        "schema_path" required path to a schema_file
        "results_path":  required path to save the extracted object
        "resume_text_path": required path to the resume text
        "data_object_path": optionl path to a data object file

    Returns:
        bool: True if successful, False otherwise
    """
    # attempt to load the resume text
    resume_text = None
    if schema_def['resume_text_path']:
        resume_text = load_docx_data(schema_def['resume_text_path'])
        if resume_text is None:
            logging.error("Error: resume_text is None")
            return None
    else:
        logging.error("Error: resume_text_path is not set")
        return None
    
    # use teh schema_def to create a JsonSchemaFactory
    # and retrieve the validated resume_schema
    resume_schema_path = schema_def['schema_path']
    resume_schema_object = json_schema.read_json_schema_file(resume_schema_path)
    resume_schema_str = json.dumps(resume_schema_object, indent=2)
    
    known_data_object = None
    optional_data_object_path = schema_def['data_object_path'] if 'data_object_path' in schema_def else None
    if optional_data_object_path:
        known_data_object = json_schema.read_json_file(optional_data_object_path)
        json_schema.validate_json_schema_object(resume_schema_object, known_data_object)
    
    extracted_object = groq_process_resume_text(
        resume_text=resume_text,
        resume_schema_str=resume_schema_str)
    
    if extracted_object is None:
        logging.error("Error: extracted_object is null")
        return None
    else:
        results_path = schema_def['results_path']
        logging.info("saving extracted_object to %s", results_path)
        with open(results_path, "w") as f:
            json.dump(extracted_object, f, indent=2)
        return extracted_object

def test_pydantic_resume( groc_resume_object) -> bool:
    """
    Test to see if the given groc_resume_object
    can be used to crate a pydantic_resume_object.
    Returns true if successful, false otherwise.

    Args:
        groc_resume_object (object): object extracted from resume text_

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # pydantic_json_schema = PydanticResume.model_json_schema()
        # print("Pydantic JSON schema:")
        # print(json.dumps(pydantic_json_schema, indent=2))
        
        # if this works, the groq_resume_object is valid
        # againt the pydantic_resume model
        pydantic_resume_object = PydanticResume(**groc_resume_object)

        # pydantic models are not json serializable, so using devtools.debug instead
        logging.info("pydantic_resume_object:")
        debug(pydantic_resume_object)

        print("SUCCESS groq_resume_object is valid against the PydanticResume model")
        return True

    except PydanticValidationError as e:
        error_file = "./errors/pydantic_validation_error.txt"
        print("groq_resume_object is invalid against the PydanticResume model. Error saved to: %s", error_file)
        return False

def test_resume_master_schema():
    """ 
    Test the master resume schema against 
    a known data object
    """
    resumeMasterSchema_def = {
        "title": "ResumeSchema",
        "schema_path": "./src/resume-schema.json",
        "results_path": "./results/resume-schema-results.json",
        "resume_text_path": os.getenv("RESUME_DOCX_PATH"),
        "data_object_path": os.getenv("TEST_DATA_OBJECT_PATH")
    }
    groq_extracted_object = test_schema_def(resumeMasterSchema_def)
    if not groq_extracted_object:
        logging.error("Error: resumeMasterSchema_def failed")
        return False
    else:
        logging.info("SUCCESS: master_groq_extracted_mobject extracted")
    
    # now validate the groq_extracted_object with the resume_schema
    resume_schema_object = json_schema.read_json_schema_file(resumeMasterSchema_def['schema_path'])
    try:
        json_schema.validate_data_object(resume_schema_object, groq_extracted_object)
    except Exception as e:
        error_file = "./errors/schema_validation_error.txt"
        logging.error("Error: groq_extracted_object failed schema validation. Error saved to: %s", error_file)
        json_schema.write_error_file(error_file, str(e))
    else:
        logging.info("SUCCESS: groq_extracted_object passed schema validation")
    
    # special pydantic_resume testing for master groq_extracted_object
    try:
        test_pydantic_resume(groq_extracted_object)
    except PydanticValidationError as e:
        error_file = "./errors/pydantic_validation_error.txt"
        logging.error("Error: groq_extracted_object failed Pydantic validation. Error saved to: %s", error_file)
        json_schema.write_error_file(error_file, str(e))
    else:
        logging.info("SUCCESS: groq_extracted_object passed PydanticResume test")
    
    return True


def test_resume_section_schemas():
    section_errors = []
    section_schema_defs = [
        {
            "title": "ResumeContactInformationSchema",
            "schema_path": "./src/resume-contact-information-schema.json",
            "results_path": "./results/resume-contact-information-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
       },
        {
            "title": "ResumeEmploymentHistorySchema",
            "schema_path": "./src/resume_employment_history_schema.json",
            "results_path": "./results/resume-employment-history-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
        },
        {
            "title": "ResumeEducationHistorySchema",
            "schema_path": "./src/resume_education_history_schema.json",
            "results_path": "./results/resume-education-history-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
        },
        {
            "title": "ResumeSkillsSchema",
            "schema_path": "./src/resume_skills_schema.json",
            "results_path": "./results/resume-skills-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
        },
        {
            "title": "ResumeProjectsSchema",
            "schema_path": "./src/resume_projects_schema.json",
            "results_path": "./results/resume-projects-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
        },
        {
            "title": "ResumePublicationsSchema",
            "schema_path": "./src/resume_publications_schema.json",
            "results_path": "./results/resume-publications-results.json",
            "resume_text_path": os.getenv("RESUME_DOCX_PATH")
        }
    ]
    
    for section_schema_def in section_schema_defs:
        title = section_schema_def['title']
        extracted_object = test_schema_def(section_schema_def)
        if not extracted_object:
            section_errors.append(f"Error: {title} extraction failure")
        else:
            logging.info(f"SUCCESS: {title} extraction successful")
            try:
                json_schema.validate_data_object(section_schema_def['schema_path'], extracted_object)
            except Exception as f:
                error_file = f"errors/{title}_extracted_object_validation_error.txt"
                logging.error(f"Error: {title} extracted object failed schema validation. Error saved to: %s", error_file)
                json_schema.write_error_file(error_file, str(f))
                section_errors.append(f)
        # break after the first section
        break
            
    if len(section_errors) > 0:
        
        logging.error("section_errors count: %d", len(section_errors))
        for error in section_errors:
            logging.error(error)
        return False
    else:
        return True

if __name__ == "__main__":
    test_resume_master_schema()
    test_resume_section_schemas()

print("!!! DONE !!!")
