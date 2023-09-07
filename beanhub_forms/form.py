import re
import typing

from starlette_wtf import StarletteForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import Field
from wtforms import Form
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms import StringField
from wtforms.validators import InputRequired
from wtforms.validators import Optional
from wtforms.validators import Regexp

from .data_types.form import AccountFormField
from .data_types.form import CurrencyFormField
from .data_types.form import DateFormField
from .data_types.form import FileFormField
from .data_types.form import FormSchema
from .data_types.form import NumberFormField
from .data_types.form import StrFormField

ACCOUNT_REGEX = "^[A-Z][0-9a-zA-Z-]*(:[A-Z0-9][0-9a-zA-Z-]*)*$"
CURRENCY_REGEX = "^[A-Z](([0-9A-Z._-]*)[0-9A-Z])?$"


def validate_currencies(form: Form, field: Field):
    for value in field.data:
        if re.match(CURRENCY_REGEX, value) is None:
            field.errors.append(f"Currency {value} is invalid.")


class DecimalAsStrField(DecimalField):
    def process_formdata(self, valuelist: list):
        super().process_formdata(valuelist)
        if self.data is not None:
            self.data = str(self.data)


def make_custom_form(
    form_schema: FormSchema,
    accounts: list[str],
    currencies: list[str],
    files: list[str],
) -> typing.Type[StarletteForm]:
    class CustomForm(StarletteForm):
        pass

    for field in form_schema.fields:
        display_name = field.display_name or field.name
        required_validators = [InputRequired() if field.required else Optional()]
        if isinstance(field, StrFormField):
            form_field = StringField(
                label=display_name,
                name=field.name,
                validators=required_validators,
            )
        elif isinstance(field, NumberFormField):
            form_field = DecimalAsStrField(
                label=display_name,
                name=field.name,
                validators=required_validators,
            )
        elif isinstance(field, DateFormField):
            form_field = DateField(
                label=display_name,
                name=field.name,
                validators=required_validators,
            )
        elif isinstance(field, FileFormField):
            form_field = SelectField(
                label=display_name,
                name=field.name,
                validators=required_validators,
                choices=files,
                validate_choice=not field.creatable,
            )
        elif isinstance(field, AccountFormField):
            form_field = SelectField(
                label=display_name,
                name=field.name,
                validators=[
                    *required_validators,
                    Regexp(regex=ACCOUNT_REGEX, message="Invalid account name."),
                ],
                choices=accounts,
                validate_choice=not field.creatable,
            )
        elif isinstance(field, CurrencyFormField):
            if field.multiple:
                field_cls = SelectMultipleField
                currency_validator = validate_currencies
            else:
                field_cls = SelectField
                currency_validator = Regexp(
                    regex=CURRENCY_REGEX, message=f"Currency value is invalid."
                )
            form_field = field_cls(
                label=field.display_name or field.name,
                name=field.name,
                validators=[*required_validators, currency_validator],
                choices=currencies,
                validate_choice=not field.creatable,
            )
        else:
            raise ValueError(f"Unsupported form type {field.type}")
        setattr(CustomForm, field.name, form_field)

    return CustomForm
