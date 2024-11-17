"""
Module for processing, validating, and using any json-schema object
"""
import json
import os
from dotenv import load_dotenv
import logging
import traceback
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
    Returns a data object read from a json_file,
    otherwise raises error

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
    
def write_error_file(error_file :str, error_string: str) -> bool:
    """
    Writes the given error string to an error file and returns True
    if the operation was successful, otherwise raises an error.

    Args:
        error_file (str): The path to the error file to be written.
        error_string (str): The string to be written
    
    Returns:
        bool: True if 1) the error_string is written to the error_file,
        otherwise raises an error
    
    Raises:
        ValueError: Error undefined error file path
        ValueError: Error writing to to the error file
    """
    if error_file is None:
        raise ValueError("Error undefined error file path")
    try:
        with open(error_file, "w", encoding="utf8") as file:
            file.write(error_string)
            return True        
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise e
    
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
        error_message_head = f"Validation error: {e}"
        error_message = f"{error_message_head}\n\nTraceback:\n{traceback.format_exc()}"
        error_file = "./errors/validate_json_schema_object_error_1.txt"
        write_error_file(error_file, error_message)
        logging.error(error_message_head)
        logging.error(traceback.format_exc())
        return False
    except SchemaError as e:
        error_message_head = f"Schema error: {e}"
        error_message = f"{error_message_head}\n\nTraceback:\n{traceback.format_exc()}"
        error_file = "./errors/validate_json_schema_object_error_2.txt"
        write_error_file(error_file, error_message)
        logging.error(error_message_head)
        logging.error(traceback.format_exc())
        return False
    except Exception as e:
        error_message_head = f"Exception: {e}"
        error_message = f"{error_message_head}\n\nTraceback:\n{traceback.format_exc()}"
        error_file = "./errors/validate_json_schema_object_error_3.txt"
        write_error_file(error_file, error_message)
        logging.error(error_message_head)
        logging.error(traceback.format_exc())
        return False

def validate_data_object(json_schema_object: object, data_object: object) -> bool:
    """
    Validates a given data object against the given json schema 
    Returns True if the data object is valid against the schema,
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
        if not json_schema_object:
            raise ValueError("Error: undefined json schema object")
        if not isinstance(json_schema_object, dict):
            raise ValueError(f"Error: invalid json schema object type: {type(json_schema_object)}")
        if not data_object:
            raise ValueError("Error: undefined data object")
        if not isinstance(data_object, dict):
            raise ValueError(f"Error: invalid data object type: {type(data_object)}")

        validator = get_json_schema_validator(json_schema_object)
        validator.validate(instance=data_object)
        return True

    except ValueError as e:
        error_file = "./errors/validate_data_object_error_1.txt"
        logger.error("Value error. See error in %s", error_file)
        write_error_file(error_file, str(e))
        raise
    except ValidationError as e:
        error_file = "./errors/validate_data_object_error_2.txt"
        logger.error("Validation error. See error in %s", error_file)
        write_error_file(error_file, str(e))
        raise e
    except SchemaError as e:
        error_file = "./errors/validate_data_object_error_3.txt"
        logger.error("Schema error. See error in %s", error_file)
        write_error_file(error_file, str(e))
        raise e
    except Exception as e:
        error_file = "./errors/validate_data_object_error_4.txt"
        logger.error("Exception. See error in %s", error_file)
        write_error_file(error_file, str(e))
        raise e

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

    resume_schema_path = os.getenv("RESUME_SCHEMA_PATH")
    if resume_schema_path is None:
        raise ValueError("RESUME_SCHEMA_PATH environment variable is not set")
    resume_schema_object = read_json_schema_file(resume_schema_path)
    logger.info("SUCCESS: resume_schema_object is valid against Draft7Validator")
    
    test_data_object_path = os.getenv("TEST_DATA_OBJECT_PATH")
    if test_data_object_path is None:
        raise ValueError("TEST_DATA_OBJECT_PATH environment variable is not set")
    test_data_object = read_json_file(test_data_object_path)
    validate_json_schema_object(resume_schema_object, test_data_object)
    logger.info("SUCCESS: resume_schema_object is valid against test_data_object_path")
