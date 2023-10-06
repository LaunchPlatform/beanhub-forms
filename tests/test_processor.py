import datetime
import pathlib

import pytest
from jinja2.exceptions import TemplateAssertionError

from beanhub_forms.data_types.form import DateFormField
from beanhub_forms.data_types.form import FormSchema
from beanhub_forms.data_types.form import Operation
from beanhub_forms.data_types.form import OperationType
from beanhub_forms.data_types.form import StrFormField
from beanhub_forms.data_types.processor import FileUpdate
from beanhub_forms.processor import process_form
from beanhub_forms.processor import ProcessError
from beanhub_forms.processor import render
from beanhub_forms.processor import RenderError


def test_render():
    result = render(
        which="operations[0].file",
        template="val={{ my_val }}",
        form_data=dict(my_val="MOCK_VAL"),
    )
    assert result == "val=MOCK_VAL"


def test_render_error():
    which = "operations[0].file"
    with pytest.raises(RenderError) as error:
        render(which=which, template="val={{ my_val | non_existing }}", form_data={})
    assert isinstance(error.value.original_exc, TemplateAssertionError)


@pytest.mark.parametrize(
    "form_schema, form_data, expected_updates",
    [
        pytest.param(
            FormSchema(
                name="my-form",
                fields=[
                    DateFormField(name="date"),
                    StrFormField(name="name"),
                ],
                operations=[
                    Operation(
                        file="{{ date }}.bean",
                        type=OperationType.append,
                        content="; name={{ name }}",
                    )
                ],
            ),
            dict(date=datetime.date(2023, 10, 5), name="BeanHub"),
            [
                FileUpdate(
                    file="2023-10-05.bean",
                    new_file=True,
                    type=OperationType.append,
                    content="; name=BeanHub\n",
                )
            ],
            id="simple",
        ),
        pytest.param(
            FormSchema(
                name="my-form",
                fields=[
                    StrFormField(name="name"),
                ],
                operations=[
                    Operation(
                        file="main.bean",
                        type=OperationType.append,
                        content="; name={{ name }}",
                    )
                ],
            ),
            dict(name="BeanHub"),
            [
                FileUpdate(
                    file="main.bean",
                    new_file=False,
                    type=OperationType.append,
                    content="; name=BeanHub\n",
                )
            ],
            id="existing-file",
        ),
    ],
)
def test_process_form(
    tmp_path: pathlib.Path,
    form_schema: FormSchema,
    form_data: dict,
    expected_updates: list[FileUpdate],
):
    bean_file = tmp_path / "main.bean"
    bean_file.write_text("; empty")
    updates = process_form(form_schema, form_data=form_data, beancount_dir=tmp_path)
    for expected_update in expected_updates:
        expected_update.file = str(tmp_path / expected_update.file)
    assert updates == expected_updates


@pytest.mark.parametrize(
    "form_schema, form_data, expected_errors",
    [
        pytest.param(
            FormSchema(
                name="my-form",
                fields=[
                    StrFormField(name="name"),
                ],
                operations=[
                    Operation(
                        file="../../etc/password",
                        type=OperationType.append,
                        content="some evil stuff",
                    )
                ],
            ),
            dict(),
            ["Invalid path '../../etc/password'"],
            id="relative-path",
        ),
        pytest.param(
            FormSchema(
                name="my-form",
                fields=[
                    StrFormField(name="name"),
                ],
                operations=[
                    Operation(
                        file="/etc/password",
                        type=OperationType.append,
                        content="some evil stuff",
                    )
                ],
            ),
            dict(),
            ["Invalid path '/etc/password'"],
            id="abs-escaping-path",
        ),
    ],
)
def test_process_form_with_errors(
    tmp_path: pathlib.Path,
    form_schema: FormSchema,
    form_data: dict,
    expected_errors: list[str],
):
    with pytest.raises(ProcessError) as error:
        process_form(form_schema, form_data=form_data, beancount_dir=tmp_path)
    assert error.value.errors == expected_errors
