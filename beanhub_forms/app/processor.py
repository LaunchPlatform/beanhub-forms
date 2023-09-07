import logging
import pathlib

from jinja2.sandbox import SandboxedEnvironment

from ..data_types.form import FormSchema
from ..data_types.form import OperationType
from .settings import settings


class RenderError(RuntimeError):
    def __init__(self, which: str, original_exc: Exception):
        self.original_exc = original_exc
        super().__init__(f"Failed to render {which} with error: {original_exc}")

    @property
    def message(self) -> str:
        return self.args[0]


def process_form(form_schema: FormSchema, form_data: dict) -> set[pathlib.Path]:
    logger = logging.getLogger(__name__)
    jinja_env = SandboxedEnvironment()
    errors: list[str] = []
    updated_files: set[pathlib.Path] = set()

    def render(which: str, template: str) -> str:
        try:
            return jinja_env.from_string(template).render(**form_data)
        except Exception as exc:
            raise RenderError(which=which, original_exc=exc)

    for i, operation in enumerate(form_schema.operations):
        op_name = f"operations[{i}]"
        file_name = render(which=f"{op_name}.file", template=operation.file)
        file_path = pathlib.Path(file_name)
        if not file_path.parts or ".." in file_path.parts:
            errors.append(f"Invalid path {file_name!r}")
            continue
        # Ensure the file path is still inside the beancount dir
        abs_file_path = file_path.absolute()
        if not abs_file_path.is_relative_to(settings.BEANCOUNT_DIR):
            errors.append(f"Invalid path {file_name!r}")
            continue
        text = render(which=f"{op_name}.content", template=operation.content) + "\n"
        if operation.type == OperationType.append:
            logger.info("Operation %s appends text to %s", i, file_name)
            with abs_file_path.open(mode="at") as fo:
                fo.write(text)
            updated_files.add(abs_file_path)
        else:
            raise ValueError(f"Unsupported type {operation.type.value}")
    return updated_files
