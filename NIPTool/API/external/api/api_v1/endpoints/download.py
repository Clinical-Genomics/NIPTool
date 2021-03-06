from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse

from NIPTool.API.external.api.deps import get_current_user
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.config import get_nipt_adapter, templates
from NIPTool.crud import find
from NIPTool.models.database import User
from NIPTool.parse.batch import validate_file_path

router = APIRouter()


@router.get("/batch_download/{batch_id}/{file_id}")
def batch_download(
    request: Request,
    batch_id: str,
    file_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """View for batch downloads"""

    batch: dict = find.batch(adapter=adapter, batch_id=batch_id).dict()
    file_path = batch.get(file_id)

    if not validate_file_path(file_path):
        # handle the redirect response!
        return RedirectResponse(request.url)

    path = Path(file_path)

    return FileResponse(
        str(path.absolute()), media_type="application/octet-stream", filename=path.name
    )


@router.get("/sample_download/{sample_id}/{file_id}")
def sample_download(
    request: Request,
    sample_id: str,
    file_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """View for sample downloads"""

    sample: dict = find.sample(adapter=adapter, sample_id=sample_id).dict()
    file_path = sample.get(file_id)
    if not validate_file_path(file_path):
        # warn file missing!
        return RedirectResponse(request.headers.get("referer"))

    file = Path(file_path)
    return FileResponse(
        str(file.absolute()), media_type="application/octet-stream", filename=file.name
    )
