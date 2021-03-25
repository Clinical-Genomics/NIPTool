from fastapi import APIRouter, Depends, Request
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from fastapi.templating import Jinja2Templates
from NIPTool.parse.batch import validate_file_path
from pathlib import Path
from fastapi.responses import RedirectResponse, FileResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/batch_download/{batch_id}/{file_id}")
def batch_download(request: Request, batch_id: str, file_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """View for batch downloads"""

    batch = adapter.batch(batch_id)
    file_path = batch.get(file_id)

    if not validate_file_path(file_path):
        # handle the redirect responce!
        return RedirectResponse(request.url)

    path = Path(file_path)

    return FileResponse(str(path.absolute()), media_type='application/octet-stream', filename=path.name)


@router.get("/sample_download/{sample_id}/{file_id}")
def sample_download(request: Request, sample_id: str, file_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """View for sample downloads"""

    sample = adapter.sample(sample_id)
    file_path = sample.get(file_id)
    if not validate_file_path(file_path):
        # handle the redirect responce!
        return RedirectResponse(request.url)

    file = Path(file_path)
    return FileResponse(str(file.absolute()), media_type='application/octet-stream', filename=file.name)
