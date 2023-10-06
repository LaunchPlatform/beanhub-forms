import pydantic

from .form import OperationType


class FileUpdate(pydantic.BaseModel):
    file: str
    new_file: bool
    content: str
    type: OperationType
