#!/usr/bin/env python3

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Literal


class ParameterType(BaseModel):
    type: Literal["number", "string", "boolean"]


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ParameterType]
    returns: ParameterType


class FunctionCallTest(BaseModel):
    prompt: str


class FunctionCallResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str
    name: str = Field(alias="fn_name")
    parameters: Dict[str, Any] = Field(alias="args")
