from fastapi import APIRouter
from fastapi import Request
from fastapi import Response

from . import deps

router = APIRouter()


@router.get("/")
async def home(
    request: Request,
    templates: deps.Jinja2TemplatesDep,
):
    return templates.TemplateResponse(
        "home.html",
        dict(
            request=request,
        ),
    )


@router.api_route("/form/{form_name}", methods=["GET", "POST"])
async def submit_form(
    request: Request,
    templates: deps.Jinja2TemplatesDep,
    flash: deps.FlashDep,
    form_name: str,
) -> Response:
    pass
