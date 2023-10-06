import pytest
from jinja2.exceptions import TemplateAssertionError

from beanhub_forms.processor import process_form
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


def test_process_form():
    process_form()
