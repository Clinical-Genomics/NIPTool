from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.utils import *
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from datetime import datetime

router = APIRouter()


@router.post("/update")
def update(request: Request, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Update the database"""

    time_stamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    user = app.user
    if user.role != "RW":
        return "", 201

    if request.form.get("form_id") == "set_sample_status":
        sample_id = request.form["sample_id"]
        sample = adapter.sample(sample_id)
        for abnormality in CHROM_ABNORM:
            new_abnormality_status = request.form[abnormality]
            if sample.get(f"status_{abnormality}") != new_abnormality_status:
                sample[f"status_{abnormality}"] = new_abnormality_status
                sample[f"status_change_{abnormality}"] = " ".join(
                    [user.name, time_stamp]
                )
        adapter.add_or_update_document(sample, adapter.sample_collection)

    if request.form.get("form_id") == "set_sample_comment":
        sample_id = request.form["sample_id"]
        sample = adapter.sample(sample_id)
        if request.form.get("comment") != sample.get("comment"):
            sample["comment"] = request.form.get("comment")
        adapter.add_or_update_document(sample, adapter.sample_collection)

    if request.form.get("button_id") == "Save":
        samples = request.form.getlist("samples")
        for sample_id in samples:
            sample = adapter.sample(sample_id)
            comment = request.form.get(f"comment_{sample_id}")
            include = request.form.get(f"include_{sample_id}")
            if comment != sample.get("comment"):
                sample["comment"] = comment
            if include and sample.get("include", False) == False:
                sample["include"] = True
                sample["change_include_date"] = " ".join([user.name, time_stamp])
            elif not include and sample.get("include") == True:
                sample["include"] = False
            adapter.add_or_update_document(sample, adapter.sample_collection)

    if request.form.get("button_id") == "include all samples":
        samples = request.form.getlist("samples")
        for sample_id in samples:
            sample = adapter.sample(sample_id)
            if sample.get("include", False) == False:
                sample["include"] = True
                sample["change_include_date"] = " ".join([user.name, time_stamp])
                adapter.add_or_update_document(
                    sample, adapter.sample_collection
                )

    return RedirectResponse(request.url)
