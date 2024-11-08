"""
Module for processing, validating, and using any json-schema object
"""
import json
import logging
from jsonschema import Draft7Validator, validate
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

# This should probably be removed.
# Define the required elements in a JSON schema object
# used to validate the structural integrity of the schema object
static_required_name_types = {
    "$schema": str,
    "type": str,
}
# This should probably be removed.
# Define the optional elements in a JSON schema object
# used to validate the structural integrity of the schema object
static_optional_name_types = {
    "additionalItems": bool,
    "additionalProperties": bool,
    "const": type,
    "contentEncoding": str,
    "contentMediaType": str,
    "definitions": dict,
    "dependencies": dict,
    "enum": list,
    "exclusiveMaximum": (int, float),
    "exclusiveMinimum": (int, float),
    "format": str,
    "items": dict,
    "maximum": (int, float),
    "maxItems": int,
    "maxLength": int,
    "maxProperties": int,
    "minimum": (int, float),
    "minItems": int,
    "minLength": int,
    "minProperties": int,
    "multipleOf": (int, float, type),
    "pattern": str,
    "patternProperties": dict,
    "propertyNames": dict,
    "uniqueItems": bool,
    "examples": list,
    "if": dict,
    "then": dict,
    "else": dict,
    "allOf": list,
    "anyOf": list,
    "oneOf": list,
    "not": dict,
    "contains": dict
}
"""
Raises:
    ValueError: Invalid or empty json schema:
    ValueError: Invalid or empty legitimateDataObject
    ValueError: Undefined or invalid data object

Returns:
    JsonSchemaFactory: an instance of the JsonSchemaFactory class
"""

class JsonSchemaFactory:
    """
    JsonSchemaFactory is a class that provides functionality to validate a JSON schemas 
    and then to validate any data objects against that validated schemas.

    Attributes:
        json_schema_path (str): The to the JSON schema file.
        legitimate_data_object_path (str): The path to the legitimate data object.
        validator (Draft7Validator): The JSON schema validator.

    Methods:
        __init__(json_schema_path, legitimate_data_object_path):
            Loads the json schema 
            loads the legitimate data object - an object which 
            is known to be valid against the json-schema.

        check_structural_integrity(schema_object):
            Checks the structural validity of the given schema object
            returns True if the json schema is valid, raises SchemaError if not.

        validate_data_object(data_object):
            Validates the given data object against the loaded JSON 
            returns True if the json schema is valid, raises SchemaError if not.
            
        check_schema_validity(schema):
            Validates the given data object against the Draft7Validator 
            returns True if the json schema is valid, raises SchemaError if not.
            
    Exce[ption]:
        ValueError: If the JSON schema file is does not contain a JSON object.
        ValueError: If the legitimate data object file does not contain a JSON object.
        SchemaError: if the json schema fails the structural integrity check,
        SchemaError: If the JSON schema fails the test against the legititmate data object.
        SchemaError: If the JSON schema fails the test against the Draft7Validator.

    """
    def __init__(self, json_schema_path, legitimate_data_object_path):

        candidate_json_schema = read_json_schema_file(json_schema_path)
        if not candidate_json_schema:
            raise ValueError(f"Invalid or empty json schema: {json_schema_path}")

        legitimate_data_object = read_json_file(legitimate_data_object_path)
        if not legitimate_data_object:
            raise ValueError(f"Error: Invalid or empty legitimateDataObject: {legitimate_data_object_path}")

        self.validated_json_schema = None
        self.validator = None

        ## apply the different json schema validation checks
        self.check_schema_validity(candidate_json_schema)

        self.check_structural_integrity(candidate_json_schema)

        self.validate_data_object(legitimate_data_object)

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


    def validate_instance(self, instance: object, schema: dict) -> bool:
        """
        Validates a given instance against a given schema.
        logs validation errors if any and returns False if 
        the instance is invalid against the schema, True otherwise.

        Args:
            instance (_type_): _description_
            schema (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            validate(instance=instance, schema=schema)
            return True
        except ValidationError as e:
            logger.error("Validation error: %s", e.message)
            return False
        except SchemaError as e:
            print("Schema error: %s", e.message)
            return False


    def validate_data_object(self, data_object) -> bool:
        """
        Validates a given data object against the predefined JSON schema of the factory.

        Args:
            data_object (dict): The JSON object to be validated.

        Returns:
            bool: True if the data object is valid against the json_schema, False otherwise.

        Raises:
            None.
        """
        try:
            validate(instance=data_object, schema=self.validated_json_schema)
            return True
        except ValidationError as e:
            logger.error("Insance validation error: %s", e.message)
            return False
        except SchemaError as e:
            logger.error("Schema validation error: %s", e.message)
            return False

    def count_schema_name_type_check_failures(self, schema_object:dict, name_types:dict) -> int:
        """
        Checks the structural validity of the given JSON schema object.
        This method counts the number of name_types that the json schema
        object does not have.

        Parameters:
        schema_object (dict): The JSON schema object to be validated.
        name_types (dict): A dictionary of the expected types for each 
        element in the schema_object.
        
        Returns:
            int: the number of check failures
        Raises:
            SchemaError: If the schema is invalid
        """
        if schema_object is None or not isinstance(schema_object, dict):
            logger.error("schemaObject is not a dictionary")
            return False

        num_failures = 0
        names = name_types.keys()
        for name in names:
            if name in schema_object:
                expected_type = name_types[name]
                actual_type = schema_object[name]
                if isinstance(expected_type, tuple):
                    if actual_type not in expected_type:
                        logger.error("schemaObject.%s is not in type %s", name, expected_type)
                        num_failures += 1
                    elif isinstance(expected_type, str):
                        if actual_type != expected_type:
                            logger.error("schemaObject.%s is not of type %s", name, expected_type)
                            num_failures += 1
                    else:
                        logger.error("schemaObject.%s has unhandled type %s", name, actual_type)
                        num_failures += 1
                        
        return num_failures == 0
                            
             

    def check_structural_integrity(self, schema_object:dict, name_types: dict) -> bool:
        """
        Checks the structural validity of the given JSON schema object.
        This method verifies that the elements in the provided schema_object
        """
        total_failures = count_schema_name_type_check_failures(schema_object, static_required_name_types)
        if total_failures == 0:
            return True
        else:
            schema_error_message = \
                f"Structural integrity checks totalled {total_failures} check failures"
            raise SchemaError(schema_error_message)


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
            print(f"Schema error: {e.message}")
            raise
