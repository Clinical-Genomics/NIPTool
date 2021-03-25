from fastapi import APIRouter, Depends, Request
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.utils import *
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/samples/{sample_id}/")
def sample(request: Request, sample_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Sample view with sample information."""
    sample = adapter.sample(sample_id)
    batch = adapter.batch(sample.get("SampleProject"))

    return templates.TemplateResponse(
        "sample/sample.html",
        context=dict(
            request=request,
            current_user='mayapapaya',
            chrom_abnorm=CHROM_ABNORM,
            sample=sample,
            status_classes=STATUS_CLASSES,
            batch=batch,
            page_id="sample")
    )


@router.get("/samples/{sample_id}/tris")
def sample_tris(request: Request, sample_id: str, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Sample view with trisomi plot."""
    sample = adapter.sample(sample_id)
    batch = adapter.batch(sample.get("SampleProject"))
    abnormal_data, data_per_abnormaliy = get_abn_for_samp_tris_plot(adapter)
    normal_data = get_normal_for_samp_tris_plot(adapter)
    sample_data = get_sample_for_samp_tris_plot(sample)
    return templates.TemplateResponse(
        "sample/sample_tris.html",
        context=dict(
            request=request,
            current_user='mayapapaya',
            tris_abn=data_per_abnormaliy,
            normal_data=normal_data,
            abnormal_data=abnormal_data,
            sample_data=sample_data,
            sample=sample,
            batch=batch,
            status_colors=STATUS_COLORS,
            page_id="sample_tris")
    )
