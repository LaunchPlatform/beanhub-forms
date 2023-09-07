import enum

import pydantic
from pydantic import BaseModel
from pydantic import conlist
from pydantic import validator

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
    default: str | None = None
    display_name: str | None = pydantic.Field(None, min_length=1, max_length=64)


class StrFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.str, const=True)


class NumberFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.number, const=True)


class DateFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.date, const=True)


class FileFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.file, const=True)
    creatable: bool = False


class AccountFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.account, const=True)
    creatable: bool = False


class CurrencyFormField(FormFieldBase):
    type: FieldType = pydantic.Field(FieldType.currency, const=True)
    creatable: bool = False
    multiple: bool = False


FormField = (
    StrFormField
    | NumberFormField
    | DateFormField
    | FileFormField
    | AccountFormField
    | CurrencyFormField
)


class Operation(FormBase):
    file: str
    content: str
    type: OperationType = OperationType.append


class CommitOptions(FormBase):
    message: str | None = None


class FormSchema(FormBase):
    name: str = pydantic.Field(regex=SLUG_REGEX, min_length=1, max_length=32)
    fields: conlist(FormField, max_items=32)
    operations: list[Operation]
    auto_format: bool = True
    commit: CommitOptions | None = None
    display_name: str | None = pydantic.Field(None, min_length=1, max_length=64)

    @validator("fields")
    def check_field_name_uniqueness(cls, v: list[FormField]) -> list[FormField]:
        field_names = set()
        for field in v:
            if field.name in field_names:
                raise ValueError(f"Duplicate field name {field.name!r}")
            field_names.add(field.name)
        return v


class FormDoc(FormBase):
    forms: conlist(FormSchema, max_items=10)

    @validator("forms")
    def check_form_name_uniqueness(cls, v: list[FormSchema]) -> list[FormSchema]:
        form_names = set()
        for form in v:
            if form.name in form_names:
                raise ValueError(f"Duplicate form name {form.name!r}")
            form_names.add(form.name)
        return v
