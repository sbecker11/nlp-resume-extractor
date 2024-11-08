"""
Module for processing a resume document and extracting json-schema formatted output using OpenAI's GPT-3.5.
"""

import os
import json
import logging
import sys
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from src.content_loader import load_docx_data
from src.json_schema_factory import read_json_schema_file
from gpt4all import GPT4All

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) 
MODEL = GPT4All(model_name="gpt-4o-2024-08-06")

def process_resume_text(resume_content, resume_schema) -> Optional(dict):
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
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format=response_format,
        temperature = 0.0
    )
    output = response['choices'][0]['message']['content']  # Assuming response is a valid method to get the JSON response
    if output is None:
        logging.error("Error no output from process_resume_text")
        return None
    if not isinstance(output, dict):
        logging.error("Error output is not a dictionary")
        return None
    if "error" in output:
        logging.error(f"Error: {output['error']}")
        return None
    
    return output



if __name__ == "__main__":
    resume_text = load_docx_data("resume.docx")        
    named_resume_schema = read_json_schema_file("src/named-resume-schema.json")
        
    output = process_resume_text(resume_content=resume_text, resume_schema=named_resume_schema)
    
    if output is None:
        logging.error("Error no output from process_resume_text")
        sys.exit(1)
        
    resume_json = output
    logging.info("output type: %s", type(resume_json))
    logging.info(json.dumps(resume_json, indent=4))

    logging.info("done")
