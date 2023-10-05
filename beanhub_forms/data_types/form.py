import enum
import typing

import pydantic
from pydantic import BaseModel
from pydantic import conlist
from pydantic import field_validator

SLUG_REGEX = "^[a-z0-9]+(?:-[a-z0-9]+)*$"


class FormBase(BaseModel):
    pass


@enum.unique
class FieldType(enum.Enum):
    str = "str"
    number = "number"
    date = "date"
    file = "file"
    currency = "currency"
    account = "account"


@enum.unique
class OperationType(enum.Enum):
    append = "append"


class FormFieldBase(FormBase):
    name: str = pydantic.Field(min_length=1, max_length=32)
    required: bool = False
    default: typing.Optional[str] = None
    display_name: typing.Optional[str] = pydantic.Field(None, min_length=1, max_length=64)


class StrFormField(FormFieldBase):
    type: typing.Literal[FieldType.str] = FieldType.str


class NumberFormField(FormFieldBase):
    type: typing.Literal[FieldType.number] = FieldType.number


class DateFormField(FormFieldBase):
    type: typing.Literal[FieldType.date] = FieldType.date


class FileFormField(FormFieldBase):
    type: typing.Literal[FieldType.file] = FieldType.file
    creatable: bool = False


class AccountFormField(FormFieldBase):
    type: typing.Literal[FieldType.account] = FieldType.account
    creatable: bool = False


class CurrencyFormField(FormFieldBase):
    type: typing.Literal[FieldType.currency] = FieldType.currency
    creatable: bool = False
    multiple: bool = False


FormField = typing.Union[
    StrFormField,
    NumberFormField,
    DateFormField,
    FileFormField,
    AccountFormField,
    CurrencyFormField
]


class Operation(FormBase):
    file: str
    content: str
    type: OperationType = OperationType.append


class CommitOptions(FormBase):
    message: typing.Optional[str]= None


class FormSchema(FormBase):
    name: str = pydantic.Field(pattern=SLUG_REGEX, min_length=1, max_length=32)
    fields: conlist(FormField, max_length=32)
    operations: list[Operation]
    auto_format: bool = True
    commit: typing.Optional[CommitOptions] = None
    display_name: typing.Optional[str] = pydantic.Field(None, min_length=1, max_length=64)

    @field_validator("fields")
    @classmethod
    def check_field_name_uniqueness(cls, v: list[FormField]) -> list[FormField]:
        field_names = set()
        for field in v:
            if field.name in field_names:
                raise ValueError(f"Duplicate field name {field.name!r}")
            field_names.add(field.name)
        return v


class FormDoc(FormBase):
    forms: conlist(FormSchema, max_length=10)

    @field_validator ("forms")
    @classmethod
    def check_form_name_uniqueness(cls, v: list[FormSchema]) -> list[FormSchema]:
        form_names = set()
        for form in v:
            if form.name in form_names:
                raise ValueError(f"Duplicate form name {form.name!r}")
            form_names.add(form.name)
        return v
