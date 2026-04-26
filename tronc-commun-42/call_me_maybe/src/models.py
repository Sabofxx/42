#!/usr/bin/env python3
"""
Models for function calling data validation using Pydantic.
Ensures strict type checking for input definitions and output results.
"""

from pydantic import BaseModel
from typing import Dict, Any, Literal


class ParameterType(BaseModel):
    """
    Schema for defining the data type of a function parameter or return value.

    Attributes:
        type: The allowed data type string (number, string, or boolean).
    """
    type: Literal["number", "string", "boolean"]


class FunctionDefinition(BaseModel):
    """
    Represents the schema and metadata of a callable function.

    Attributes:
        name: The unique identifier of the function.
        description: A brief explanation of what the function does.
        parameters: A dictionary mapping parameter names
                    to their type definitions.
        returns: The expected return type of the function.
    """
    name: str
    description: str
    parameters: Dict[str, ParameterType]
    returns: ParameterType


class FunctionCallTest(BaseModel):
    """
    Represents an individual test case for function calling.

    Attributes:
        prompt: The natural language request to be processed by the LLM.
    """
    prompt: str


class FunctionCallResult(BaseModel):
    """
    Schema for the final output of a function calling operation.

    This matches the structure required by the subject:
    keys are 'prompt', 'name', and 'parameters'.

    Attributes:
        prompt: The original input prompt.
        name: The name of the function identified by the model.
        parameters: A dictionary of key-value pairs representing
                    the generated arguments with their typed values.
    """
    prompt: str
    name: str
    parameters: Dict[str, Any]
