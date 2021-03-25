
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.post("/")
def index(request: Request):
    """Log in view."""

    return templates.TemplateResponse("index.html", context={"request": request})


@router.get("/")
def index(request: Request):
    """Log in view."""

    return templates.TemplateResponse("index.html", context={"request": request})
