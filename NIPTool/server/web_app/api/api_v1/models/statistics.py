from fastapi import APIRouter, Depends, Request
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.utils import *
from NIPTool.server.web_app.api.deps import get_nipt_adapter, get_current_active_user
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/statistics")
def statistics(request: Request, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Statistics view."""

    nr_batches = 3
    scatter_plots = ["Stdev_13", "Stdev_18", "Stdev_21"]
    box_plots = [
        "Chr13_Ratio",
        "Chr18_Ratio",
        "Chr21_Ratio",
        "FF_Formatted",
        "DuplicationRate",
        "MappedReads",
        "GC_Dropout",
    ]

    batches = get_last_batches(adapter=adapter, nr=nr_batches)
    batch_ids = [batch.get("_id") for batch in batches]
    box_stat = get_statistics_for_box_plot(
        adapter=adapter, batches=batch_ids, fields=box_plots
    )
    scatter_stat = get_statistics_for_scatter_plot(
        batches=batches, fields=scatter_plots
    )
    return templates.TemplateResponse(
        "statistics.html",
        context=dict(
            request=request,
            current_user='mayapapaya',
            ticks=list(range(1, nr_batches + 1)),
            nr_batches=nr_batches,
            batch_ids=batch_ids,
            box_stat=box_stat,
            box_plots=box_plots,
            scatter_stat=scatter_stat,
            scatter_plots=scatter_plots,
            page_id="statistics")
    )
