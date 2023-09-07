import typing

import pytest
from pytest_mock import MockFixture
from starlette.datastructures import ImmutableMultiDict

from beanhub_forms.data_types.form import AccountFormField
from beanhub_forms.data_types.form import CurrencyFormField
from beanhub_forms.data_types.form import DateFormField
from beanhub_forms.data_types.form import FileFormField
from beanhub_forms.data_types.form import FormField
from beanhub_forms.data_types.form import FormSchema
from beanhub_forms.data_types.form import NumberFormField
from beanhub_forms.data_types.form import StrFormField
from beanhub_forms.form import make_custom_form


@pytest.fixture
def post_request(mocker: MockFixture) -> typing.Any:
    request = mocker.Mock()
    request.state = object()
    request.method = "POST"
    return request


@pytest.mark.asyncio
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
            ImmutableMultiDict(
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
async def test_custom_form_validation(
    post_request: typing.Any,
    fields: list[FormField],
    form_data: dict,
    kwargs: dict,
    expected_errors: dict[str, typing.Any],
):
    schema = FormSchema(name="add-contracting-hours", fields=fields, operations=[])
    CustomForm = make_custom_form(form_schema=schema, **kwargs)
    form = CustomForm(post_request, ImmutableMultiDict(form_data))
    await form.validate_on_submit()
    assert form.errors == expected_errors
