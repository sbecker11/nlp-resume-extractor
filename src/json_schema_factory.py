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

def read_json_file(json_file:str) -> dict:
    """
    Reads a JSON file and returns the content as a dictionary.
    Does not validate the JSON object.

    Args:
        json_file (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.
    
    Raises:
        ValueError: Error reading undefined JSON file path
        ValueError: Error invalid json_file
        ValueError: Error reading json
    """
    try:
        if json_file is None:
            raise ValueError("Error reading undefined json file path")
        # logging.info("** Reading JSON file: %s", json_file)
        with open(json_file, "r", encoding="utf8") as file:
            json_file_data = file.read()
            # logging.info("json filedata type: %s", type(json_file_data))
            # logging.info("json filedata len: %s", len(json_file_data))
            json_object = json.loads(json_file_data)
            # logging.info("json object type: %s", type(json_object))
            # logging.info("read_json_file returning: %s", json.dumps(json_object, indent=2))
            if json_object is None:
                raise ValueError(f"Error reading json_file: {json_file}")
            if not isinstance(json_object, dict):
                raise ValueError(f"Error: invalid json_file: {json_file}")
            return json_object

    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Error reading json_file: %s %s", json_file, e)
        raise e


def read_json_schema_file(json_schema_file:str) -> dict:
    """
    Reads a JSON schema file and returns the content as a dictionary.
    Does not validate the JSON schema object.

    Args:
        json_schema_file (str): The path to the JSON schema file.

    Returns:
        dict: The content of the JSON schema file as a dictionary.
    
    Raises:
        ValueError: Error undefined json schema file
        ValueError: Error invalid data object in json schema file
    """
    if json_schema_file is None:
        raise ValueError("Error undefined json schema file")
    json_schema = read_json_file(json_schema_file)
    if json_schema is None:
        raise ValueError("Error undefined json schema file")
    if not isinstance(json_schema, dict):
        raise ValueError("Error: invalid ison schema")
    return json_schema


def external_validate_data_object(json_schema: dict, data_object: object) -> bool:
    """
    Validates a given data object against the given json schema outside of the 
    JsonSchemaFactory class. Returns True if the data object is valid against the schema,
    raises Errors otherwise.

    Args:
        json_schema (dict): The json schema object
        data_object (dict): The JSON object to be validated.

    Returns:
        bool: True if the data object is valid against the json_schema,
        raises Errors otherwise

    Raises:
        ValueError: If the schema is undefined or invalid
        ValueError: If the data object is undefined or invalid
        ValidationError: If the validator is invalid
        SchemaError: If the json schema is invalid
        Exception: For any other error
    """
    try:
        if not isinstance(json_schema, dict):
            raise ValueError("Error: invalid json schema")
        if not isinstance(data_object, dict):
            raise ValueError("Error: invalid data object")

        validator = Draft7Validator(json_schema)
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


class JsonSchemaFactory:
    """
    JsonSchemaFactory is a class that provides functionality to validate a JSON schemas 
    and then to validate any data objects against that validated schemas.

    Attributes:
        json_schema_path (str): The to the JSON schema file.
        optional_test_data_object_path Optional[str]: The optional path to the test data object.
        validator (Draft7Validator): The JSON schema validator.

    Methods:
        __init__(json_schema_path, optinal_test_data_object_path):
            Loads the json schema 
            loads the test data object if the optinal_test_data_object_path is defined

        validate_data_object(data_object):
            Validates the given data object against the validated json schema
            returns True if the json schema is valid, raises ValidationError if not.
            
        check_schema_validity(schema):
            Validates the given json schema against the Draft7Validator 
            returns True if the json schema is valid, raises SchemaError if not.
            
    Raises:
        ValueError: If the JSON schema file is does not contain a JSON object.
        ValueError: If the test data object file does not contain a JSON object.
        SchemaError: If the JSON schema fails the test against the legititmate data object.
        SchemaError: If the JSON schema fails the test against the Draft7Validator.

    """
    def __init__(self, json_schema_path:str, optional_test_data_object_path: Optional[str] = None):

        candidate_json_schema = read_json_schema_file(json_schema_path)
        if not candidate_json_schema:
            raise ValueError(f"Error: json schema file path invalid: {json_schema_path}")

        # optional test data object used to validate the schema
        self.test_data_object = None
        if optional_test_data_object_path:
            self.test_data_object = read_json_file(optional_test_data_object_path)
            if not self.test_data_object:
                raise ValueError(f"Error: optional_test_path invalid: \
                    {optional_test_data_object_path}")

        self.validated_json_schema = None
        self.validator = None

        ## apply the different json schema validation checks
        self.check_schema_validity(candidate_json_schema)

        # optional check against a test data object
        if self.test_data_object:
            try:
                external_validate_data_object(candidate_json_schema, self.test_data_object)
                print("SUCCESS - json schema passed test against known test data object")
            except ValidationError as e:
                raise SchemaError(f"Error: json schema failed test against \
                    known test data object: {e.message}") from e
            except SchemaError as e:
                raise SchemaError(f"Error: json schema failed test against \
                    Draft7Validator: {e.message}") from e

        # If all checks pass, save the validated_json_schema
        # and use it to create a Draft7Validator instance
        # to be used to validate other data objects against
        # the validated_json schema
        self.validated_json_schema = candidate_json_schema

        self.validator = Draft7Validator(self.validated_json_schema)


    def get_validated_json_schema(self) -> dict:
        """
        Returns the validated JSON schema object of the factory
        if it exists, otherwise raises a ValueError.

        Returns:
            dict: The validated JSON schema object.
        """
        if self.validated_json_schema is None:
            raise ValueError("Error: validated_json_schema is Undefined")
        return self.validated_json_schema


    def validate_instance(self, instance: object) -> bool:
        """
        Validates a given instance against the factory's validated schema.
        logs validation errors if any and returns False if 
        the instance is invalid against the schema, True otherwise.

        Args:
            instance (_type_): _description_

        Returns:
            bool: True if the instance is valid, returns False otherwise 
            
        Raises: (logs them only, does not raise exceptions)
            ValueError: If the validator is undefined
            ValueError: If the validated_schema is undefined
            ValidationError: If the instance is invalid against the schema
            SchemaError: If the schema is invalid
        """
        try:
            if self.validator is None:
                raise ValueError("Error: validator is undefined")
            if self.validated_json_schema is None:
                raise ValueError("Error: validated_schema is undefined")

            self.validator.validate(instance=instance)
            return True

        except ValueError as e:
            logger.error("Value error: %s", str(e))
            return False
        except ValidationError as e:
            logger.error("Validation error: %s", str(e))
            return False
        except SchemaError as e:
            logger.error("Schema error: %s", str(e))
            return False


    def check_schema_validity(self, schema:dict) -> bool:
        """
        Validate the given json schema using Draft7Validator.check_schema.     
        Args:
            schema (dict): The schema to be validated
        Returns:
            bool: True if the schema is valid
        Raises:
            SchemaError: If the schema is invalid
        """
        try:
            Draft7Validator.check_schema(schema)
            return True
        except SchemaError as e:
            logger.error("Schema error: %s", str(e))
            raise

if __name__ == "__main__":
    load_dotenv()

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
    
    logger.info("SUCCESS!! resume_schema is valid against Draft7Validator!!")
    logger.info("SUCCESS!! resume_schema is valid against test_data_object!!")
    
