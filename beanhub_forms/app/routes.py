from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status

from . import deps
from ..form import make_custom_form
from .helpers import convert_fields_for_js

router = APIRouter()


@router.get("/")
async def home(
    request: Request,
    templates: deps.Jinja2TemplatesDep,
    form_doc: deps.FormDocDep,
):
    return templates.TemplateResponse(
        "home.html",
        dict(
            request=request,
            form_doc=form_doc,
        ),
    )


@router.api_route("/form/{form_name}", methods=["GET", "POST"])
async def submit_form(
    request: Request,
    templates: deps.Jinja2TemplatesDep,
    flash: deps.FlashDep,
    form_doc: deps.FormDocDep,
    form_name: str,
) -> Response:
    if form_doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    forms = {form.name: form for form in form_doc.forms}
    form_schema = forms.get(form_name)
    if form_schema is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    CustomForm = make_custom_form(
        form_schema=form_schema,
        accounts=[],
        currencies=[],
        files=[],
    )
    form = await CustomForm.from_formdata(request)
    fields = convert_fields_for_js(form=form, form_schema=form_schema)
    if await form.validate_on_submit():
        pass
    return templates.TemplateResponse(
        "form.html",
        dict(
            request=request,
            form_schema=form_schema,
            form=form,
            fields=fields,
        ),
    )
