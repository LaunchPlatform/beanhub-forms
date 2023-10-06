import io
import textwrap
import typing

import pytest
import yaml
from multidict import MultiDict

from beanhub_forms.data_types.form import AccountFormField
from beanhub_forms.data_types.form import CurrencyFormField
from beanhub_forms.data_types.form import DateFormField
from beanhub_forms.data_types.form import FileFormField
from beanhub_forms.data_types.form import FormDoc
from beanhub_forms.data_types.form import FormField
from beanhub_forms.data_types.form import FormSchema
from beanhub_forms.data_types.form import NumberFormField
from beanhub_forms.data_types.form import StrFormField
from beanhub_forms.form import make_custom_form


@pytest.fixture
def sample_form_doc() -> str:
    return textwrap.dedent(
        """\
    forms:
    - name: add-xyz-hours
      display_name: "Hours spent on XYZ contracting project"
      fields:
      - name: date
        type: date
        display_name: "Date"
        required: true
      - name: hours
        type: number
        display_name: "Hours"
        required: true
      - name: rate
        type: number
        display_name: "Rate (USD)"
        default: "300"
        required: true
      - name: narration
        type: str
        default: "Hours spent on the software development project for client XYZ"
        display_name: "Narration"
      operations:
      - type: append
        file: "books/{{ date.year }}.bean"
        content: |
          {{ date }} * {{ narration | tojson }}
            Assets:AccountsReceivable:Contracting:XYZ      {{  hours }} XYZ.HOUR @ {{ rate }} USD
            Income:Contracting:XYZ      
    """
    )


@pytest.mark.parametrize(
    ", ".join(["fields", "kwargs", "form_data", "expected_errors"]),
    [
        (
            [
                StrFormField(name="str", required=True),
                NumberFormField(name="number", required=True),
                DateFormField(name="date", required=True),
                FileFormField(name="file", required=True),
                AccountFormField(name="account", required=True),
                CurrencyFormField(name="currency", required=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            {},
            dict(
                str=["This field is required."],
                number=["This field is required."],
                date=["This field is required."],
                file=["This field is required."],
                account=["This field is required."],
                currency=["This field is required."],
            ),
        ),
        (
            [
                DateFormField(name="date"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            {},
            {},
        ),
        (
            [
                DateFormField(name="date"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(date="bad-date"),
            dict(date=["Not a valid date value."]),
        ),
        # number
        (
            [
                NumberFormField(name="amount"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(amount="bad-number"),
            dict(amount=["Not a valid decimal value."]),
        ),
        (
            [
                NumberFormField(name="amount"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(amount="12.34"),
            {},
        ),
        # file
        (
            [
                FileFormField(name="file"),
            ],
            dict(accounts=[], currencies=[], files=["main.bean"]),
            dict(file="main.bean"),
            {},
        ),
        (
            [
                FileFormField(name="file"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(file="bad-file.bean"),
            dict(file=["Not a valid choice."]),
        ),
        (
            [
                FileFormField(name="file", creatable=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(file="new-file.bean"),
            {},
        ),
        # account
        (
            [
                AccountFormField(name="account"),
            ],
            dict(accounts=["Assets:Cash"], currencies=[], files=[]),
            dict(account="Assets:Cash"),
            {},
        ),
        (
            [
                AccountFormField(name="account"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(account="Assets:Cash"),
            dict(account=["Not a valid choice."]),
        ),
        (
            [
                AccountFormField(name="account", creatable=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(account="Assets:Cash"),
            {},
        ),
        (
            [
                AccountFormField(name="account", creatable=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(account="bad-account-name"),
            dict(account=["Invalid account name."]),
        ),
        # currency
        (
            [
                CurrencyFormField(name="currency"),
            ],
            dict(accounts=[], currencies=["BTC"], files=[]),
            dict(currency="BTC"),
            {},
        ),
        (
            [
                CurrencyFormField(name="currency"),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(currency="BTC"),
            dict(currency=["Not a valid choice."]),
        ),
        (
            [
                CurrencyFormField(name="currency", creatable=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(currency="BTC"),
            {},
        ),
        (
            [
                CurrencyFormField(name="currency", creatable=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            dict(currency="btc"),
            dict(currency=["Currency value is invalid."]),
        ),
        (
            [
                CurrencyFormField(name="currency", creatable=True, multiple=True),
            ],
            dict(accounts=[], currencies=[], files=[]),
            MultiDict(
                [
                    ("currency", "USD"),
                    ("currency", "btc"),
                    ("currency", "twd"),
                ]
            ),
            dict(currency=["Currency btc is invalid.", "Currency twd is invalid."]),
        ),
    ],
)
def test_custom_form_validation(
    fields: list[FormField],
    form_data: dict,
    kwargs: dict,
    expected_errors: dict[str, typing.Any],
):
    schema = FormSchema(name="add-contracting-hours", fields=fields, operations=[])
    CustomForm = make_custom_form(form_schema=schema, **kwargs)
    form = CustomForm(MultiDict(form_data))
    form.validate()
    assert form.errors == expected_errors


def test_parse_form_doc(sample_form_doc: str):
    payload = yaml.safe_load(io.StringIO(sample_form_doc))
    FormDoc.model_validate(payload)
