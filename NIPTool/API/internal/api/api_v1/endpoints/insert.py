from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Response, status
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.crud.insert import insert_batch, insert_samples, insert_user
from NIPTool.exeptions import NIPToolError
from NIPTool.models.database import Batch, Sample
from NIPTool.models.server.load import BatchRequestBody, UserRequestBody
from NIPTool.parse.batch import get_batch, get_samples
from NIPTool.API.internal.api.deps import get_nipt_adapter

router = APIRouter()


@router.post("/batch")
def batch(
    response: Response,
    batch_files: BatchRequestBody,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
):
    """Function to load batch data into the database with rest"""

    nipt_results = Path(batch_files.result_file)
    if not nipt_results.exists():
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "Results file missing."}
    samples: List[Sample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    try:
        insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
        insert_samples(
            adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls
        )
    except NIPToolError as e:
        response.status_code = e.code
        return {"message": e.message}

    response.status_code = status.HTTP_200_OK
    return {"message": f"Batch {batch.batch_id} inserted to the database"}


@router.post("/user")
def user(
    response: Response, user: UserRequestBody, adapter: NiptAdapter = Depends(get_nipt_adapter)
):
    """Function to load user into the database with rest"""

    try:
        insert_user(adapter, user)
    except NIPToolError as e:
        response.status_code = e.code
        return {"message": e.message}

    response.status_code = status.HTTP_200_OK
    return {"message": f"User {user.email} inserted to the database."}