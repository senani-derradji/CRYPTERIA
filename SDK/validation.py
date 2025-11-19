import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import os, sys
from pathlib import Path

max_size = 5_000_000
cloud_providers = ['dropbox', 'google_drive']

data_accepted_types = ["jpg", "jpeg", "png",
                       "pdf", "txt", "key", "bin", ]

def is_valid_file_type(path: str) -> bool: return path.lower().endswith(tuple(data_accepted_types))

class DataPayload(BaseModel):
    data: bytes
    @field_validator("data", mode='before')
    def validate_data(cls, value):
        if not value:
           raise ValueError("Data must not be empty.")
        if not isinstance(value, bytes):
            raise TypeError("Data must be of type bytes.")
        if len(value) > max_size:
            raise ValueError("Data Payload is Too Long")
        return value


class DataTypeValidate(BaseModel):
    file_path: Path

    @field_validator("file_path")
    def validate_file_path(cls, value):
        if not value:
            raise ValueError("File path must not be empty.")
        if not isinstance(value, Path):
            raise TypeError("File path must be of type Path.")
        if not value.exists():
            raise FileNotFoundError(f"File not found at {value}")
        if not is_valid_file_type(str(value)):
            raise ValueError("File Type Not Supported")
        return value

class DataTypes(BaseModel):
    data_type: str

    @field_validator("data_type")
    def validate_data_type(cls, value):
        if value.lower() not in data_accepted_types:
            raise ValueError("Data Type Not Supported")
        return value.lower()

class ProvidorValidation(BaseModel):
    providor: str

    @field_validator("providor")
    def validate_providor(cls, value):
        if value.upper() not in cloud_providers:
            raise ValueError("Cloud Providor Not Supported")
        return value

