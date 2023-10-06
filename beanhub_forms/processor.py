import functools
import logging
import pathlib

from jinja2.sandbox import SandboxedEnvironment

from .data_types.form import FormSchema
from .data_types.form import OperationType
from .data_types.processor import FileUpdate

jinja_env = SandboxedEnvironment()


def render(which: str, template: str, form_data: dict) -> str:
    try:
        return jinja_env.from_string(template).render(**form_data)
    except Exception as exc:
        raise RenderError(which=which, original_exc=exc)


class RenderError(RuntimeError):
    def __init__(self, which: str, original_exc: Exception):
        self.original_exc = original_exc
        super().__init__(f"Failed to render {which} with error: {original_exc}")

    @property
    def message(self) -> str:
        return self.args[0]


class ProcessError(RuntimeError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Process error")


def process_form(
    form_schema: FormSchema, form_data: dict, beancount_dir: pathlib.Path
) -> list[FileUpdate]:
    logger = logging.getLogger(__name__)
    errors: list[str] = []
    render_func = functools.partial(render, form_data=form_data)
    changed_files: set[pathlib.Path] = set()
    added_files: set[pathlib.Path] = set()
    file_updates: list[FileUpdate] = []

    for i, operation in enumerate(form_schema.operations):
        op_name = f"operations[{i}]"
        file_name = render_func(which=f"{op_name}.file", template=operation.file)
        file_path = beancount_dir / file_name
        if not file_path.parts or ".." in file_path.parts:
            errors.append(f"Invalid path {file_name!r}")
            continue
        # Ensure the file path is still inside the beancount dir
        abs_file_path = file_path.absolute()
        if not abs_file_path.is_relative_to(beancount_dir):
            errors.append(f"Invalid path {file_name!r}")
            continue
        if file_path not in changed_files and file_path not in added_files:
            if file_path.exists():
                changed_files.add(file_path)
            else:
                added_files.add(file_path)
        text = (
            render_func(which=f"{op_name}.content", template=operation.content) + "\n"
        )
        if operation.type == OperationType.append:
            logger.info("Operation %s appends text to %s", i, file_name)
            file_updates.append(
                FileUpdate(
                    file=str(file_path),
                    content=text,
                    new_file=file_path in added_files,
                    type=operation.type,
                )
            )
        else:
            raise ValueError(f"Unsupported type {operation.type.value}")
    if errors:
        raise ProcessError(errors=errors)
    return file_updates
