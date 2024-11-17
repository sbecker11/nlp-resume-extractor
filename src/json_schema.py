"""
Module for processing, validating, and using any json-schema object
"""
import json
import sys
import os
from dotenv import load_dotenv
import logging
from typing import Optional

# pip install jsonschema
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError, SchemaError

logging.basicConfig(
    format='%(filename)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def read_json_file(json_file:str) -> object:
    """
    Reads and validates a json schema from a json file 
    Returns the validated schema, otherwise raises
    an Error

    Args:
        json_file (str): The path to the JSON file.

    Returns:
        object: The contents of the JSON file (type dict).
    
    Raises:
        ValueError: Error reading undefined JSON file path
        ValueError: Error invalid json_file
        ValueError: Error reading json
    """
    if json_file is None:
        raise ValueError("Error reading undefined json file path")
    with open(json_file, "r", encoding="utf8") as file:
        json_file_data = file.read()
        json_object = json.loads(json_file_data)
        if json_object is None:
            raise ValueError(f"Error empty json_file: {json_file}")
        if not isinstance(json_object, dict):
            raise ValueError(f"Error: invalid json_file: {json_file}")
        
        return json_object

def read_json_schema_file(json_schema_file:str) -> object:
    """
    Reads a json schema file and returns the validated
    json schema object or raises an error.

    Args:
        json_schema_file (str): The path to the JSON schema file.

    Returns:
        object: the validated json schema object (type dict)
    
    Raises:
        # from read_json_file
        ValueError: Error reading undefined JSON file path
        ValueError: Error invalid json_file
        ValueError: Error reading json
        # from Draft7Validator.check_schema
        SchemaError: Error json schema is not valid
    """
    json_schema_object = read_json_file(json_schema_file)

    Draft7Validator.check_schema(json_schema_object)
    
    return json_schema_object

def validate_json_schema_object(json_schema_object: object, known_data_object: object) -> bool:
    """
    Validates a given json_schema_object by 
    using it to validate a data object that is guaranteed
    to be valid against the schema. If any errors are
    encounted then the json_schema_object is considered
    invalid.

    Args:
        json_schema_object (object): the schema being tested
        known_data_object (object): a data object known to be valid
        against the concept of the json schema object

    Returns:
        bool: True if json_schema_object is valid,
        False otherwise
    
    Raises:
        nothing
    """
    try:
        validate_data_object(json_schema_object, known_data_object)
        return True
    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        return False
    except SchemaError as e:
        logger.error("Schema error: %s", str(e))
        return False
    except Exception as e:
        logger.error("Error: %s", str(e))
        return False

def validate_data_object(json_schema_object: object, data_object: object) -> bool:
    """
    Validates a given data object against the given json schema outside of the 
    JsonSchemaFactory class. Returns True if the data object is valid against the schema,
    raises Errors otherwise.

    Args:
        json_schema_object (object): The json schema object
        data_object (object): The JSON object to be validated.

    Returns:
        bool: True if the data object is valid against the json_schema_object,
        raises Errors otherwise

    Raises:
        ValueError: If the schema is undefined or invalid
        ValueError: If the data object is undefined or invalid
        ValidationError: If the validator is invalid
        SchemaError: If the json schema is invalid
        Exception: For any other error
    """
    try:
        if not isinstance(json_schema_object, dict):
            raise ValueError("Error: invalid json schema")
        if not isinstance(data_object, dict):
            raise ValueError("Error: invalid data object")

        validator = get_json_schema_validator(json_schema_object)
        validator.validate(instance=data_object)
        return True

    except ValueError as e:
        logger.error("Value error: %s", str(e))
        raise
    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        raise
    except SchemaError as e:
        logger.error("Schema validation error: %s", str(e))
        raise
    except Exception as e:
        logger.error("Error: %s", str(e))
        raise

def get_json_schema_validator(json_schema_object: object) -> Draft7Validator:
    """
    Returns a Draft7Validator initialized by the given
    json_schema_object if the schema is valid, raises 
    SchemaError otherwise.

    Args:
        json_schema_object (object): The json schema object

    Returns:
        an initialized Draft7Validator if the json_schema_object
        is valid against the Draft7Validator, raises SchemaError otherwise

    Raises:
        SchemaError: If the schema is invalid
    """
    return Draft7Validator(json_schema_object)


if __name__ == "__main__":
    load_dotenv()

    resume_schema_object = read_json_schema_file(os.getenv("RESUME_SCHEMA_PATH"))
    logger.info("SUCCESS: resume_schema_object is valid against Draft7Validator")
    
    test_data_object = read_json_file(os.getenv("TEST_DATA_OBJECT_PATH"))
    validate_json_schema_object(resume_schema_object, test_data_object)
    logger.info("SUCCESS: resume_schema_object is valid against test_data_object_path")
