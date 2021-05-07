from fastapi import APIRouter, Depends, Request

from NIPTool.API.external.api.deps import (
    get_current_user,
    redirect_unauthorized,
    return_500_if_errors,
)
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.API.external.utils import *
from NIPTool.config import get_nipt_adapter, templates
from NIPTool.crud import find
from NIPTool.models.database import Batch, User

router = APIRouter()


@router.post("/")
@return_500_if_errors
def batches(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """List of all batches"""

    all_batches: List[Batch] = find.batches(adapter=adapter)
    return templates.TemplateResponse(
        "batches.html",
        context={
            "request": request,
            "batches": all_batches,
            "current_user": user,
            "page_id": "all_batches",
        },
    )


@router.get("/")
@return_500_if_errors
def batches(
    request: Request,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """List of all batches"""
    all_batches: List[Batch] = find.batches(adapter=adapter)
    return templates.TemplateResponse(
        "batches.html",
        context={
            "request": request,
            "batches": all_batches,
            "current_user": user,
            "page_id": "all_batches",
        },
    )


@router.post("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with table of all samples in the batch."""

    samples: List[Sample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return templates.TemplateResponse(
        "batch/tabs/table.html",
        context={
            "request": request,
            "batch": find.batch(batch_id=batch_id, adapter=adapter),
            "sample_info": [get_sample_info(sample) for sample in samples],
            "page_id": "batches",
            "current_user": user,
        },
    )


@router.get("/{batch_id}/")
def batch(
    request: Request,
    batch_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with table of all samples in the batch."""
    samples: List[Sample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    return templates.TemplateResponse(
        "batch/tabs/table.html",
        context={
            "request": request,
            "batch": find.batch(batch_id=batch_id, adapter=adapter),
            "sample_info": [get_sample_info(sample) for sample in samples],
            "page_id": "batches",
            "current_user": user,
        },
    )


@router.get("/{batch_id}/{ncv}")
def NCV(
    request: Request,
    batch_id: str,
    ncv,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with with NCV plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    return templates.TemplateResponse(
        "batch/tabs/NCV.html",
        context=dict(
            request=request,
            tris_thresholds=TRISOMI_TRESHOLDS,
            batch=batch.dict(),
            chr=ncv,
            ncv_chrom_data={ncv: get_tris_cases(adapter, ncv, batch_id)},
            normal_data=get_tris_control_normal(adapter, ncv),
            abnormal_data=get_tris_control_abnormal(adapter, ncv, 0),
            page_id=f"batches_NCV{ncv}",
            current_user=user,
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction_XY")
def fetal_fraction_XY(
    request: Request,
    batch_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with fetal fraction (X against Y) plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    control = get_ff_control_normal(adapter)
    abnormal = get_ff_control_abnormal(adapter)
    return templates.TemplateResponse(
        "batch/tabs/FF_XY.html",
        context=dict(
            request=request,
            current_user=user,
            control=control,
            abnormal=abnormal,
            cases=get_ff_cases(adapter, batch_id),
            max_x=max(control["FFX"]) + 1,
            min_x=min(control["FFX"]) - 1,
            batch=batch.dict(),
            page_id="batches_FF_XY",
        ),
    )


@router.get("/batches/{batch_id}/fetal_fraction")
def fetal_fraction(
    request: Request,
    batch_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with fetal fraction plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

    return templates.TemplateResponse(
        "batch/tabs/FF.html",
        context=dict(
            request=request,
            current_user=user,
            control=get_ff_control_normal(adapter),
            cases=get_ff_cases(adapter, batch_id),
            batch=batch.dict(),
            page_id="batches_FF",
        ),
    )


@router.get("/batches/{batch_id}/coverage")
def coverage(
    request: Request,
    batch_id: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Batch view with coverage plot"""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = find.batch_samples(batch_id=batch_id, adapter=adapter)

    scatter_data = get_scatter_data_for_coverage_plot(samples)
    box_data = get_box_data_for_coverage_plot(samples)
    return templates.TemplateResponse(
        "batch/tabs/coverage.html",
        context=dict(
            request=request,
            current_user=user,
            batch=batch.dict(),
            x_axis=list(range(1, 23)),
            scatter_data=scatter_data,
            box_data=box_data,
            page_id="batches_cov",
        ),
    )


@router.get("/batches/{batch_id}/report/{coverage}")
def report(
    request: Request,
    batch_id: str,
    coverage: str,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """Report view, collecting all tables and plots from one batch."""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = find.batch_samples(batch_id=batch_id, adapter=adapter)

    scatter_data = get_scatter_data_for_coverage_plot(samples)
    box_data = get_box_data_for_coverage_plot(samples)
    control = get_ff_control_normal(adapter)
    return templates.TemplateResponse(
        "batch/report.html",
        context=dict(
            request=request,
            current_user=user,
            batch=batch.dict(),
            # NCV
            ncv_chrom_data={
                "13": get_tris_cases(adapter, "13", batch_id),
                "18": get_tris_cases(adapter, "18", batch_id),
                "21": get_tris_cases(adapter, "21", batch_id),
            },
            normal_data=get_tris_control_normal(adapter, "21"),
            abnormal_data=get_tris_control_abnormal(adapter, "21", 0),
            # FF
            control=control,
            cases=get_ff_cases(adapter, batch_id),
            abnormal=get_ff_control_abnormal(adapter),
            max_x=max(control["FFX"]) + 1,
            min_x=min(control["FFX"]) - 1,
            # table
            sample_info=[get_sample_info(sample) for sample in samples],
            # coverage
            coverage=coverage,
            x_axis=list(range(1, 23)),
            scatter_data=scatter_data,
            box_data=box_data,
            page_id="batches",
        ),
    )
