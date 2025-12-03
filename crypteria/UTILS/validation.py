import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from pydantic import BaseModel, field_validator

import os, sys
from pathlib import Path


max_size = 10_000_000
data_accepted_types = ["jpg", "jpeg", "png", "pdf", "txt", "key", "bin"]


def is_valid_file_type(path: Path) -> bool: return str(path).lower().endswith(tuple(data_accepted_types))


class DataPayload(BaseModel):
    data : bytes

    @field_validator("data")
    @classmethod
    def validate_data(cls, value):
        if not value:
           raise ValueError("Data must not be empty.")

        if not isinstance(value, bytes):
            raise TypeError("Data must be of type bytes.")

        if len(value) > max_size:
            raise ValueError("Data Payload is Too Long")

        return value


class DataTypeValidate(BaseModel):
    file_path: Path = Path()

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: Path) -> Path:

        if value.suffix.lower().lstrip('.') in data_accepted_types:
            return value

        raise ValueError(f"File type '{value.suffix}' not supported.")

