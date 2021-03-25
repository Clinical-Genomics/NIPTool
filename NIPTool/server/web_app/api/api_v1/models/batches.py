from typing import List

from fastapi import Request
from pydantic import BaseModel
from NIPTool.schemas.db_models.batch import BatchModel


def ResponceModel(BaseModel):
    current_user: str = 'mayapapaya'
    page_id: str
    request: Request


def BatchesResponceModel(ResponceModel):
    batches: List[dict]  # ?


def BatchResponceModel(ResponceModel):
    batch: BatchModel  # not really true. This is a database object


def BatchTableResponceModel(BatchResponceModel):
    sample_info: List[dict]  # ?


def NCVResponceModel(BatchResponceModel):
    tris_thresholds = TRISOMI_TRESHOLDS,
    chr = ncv,
    ncv_chrom_data = {ncv: get_tris_cases(adapter, ncv, batch_id)},
    normal_data = get_tris_control_normal(adapter, ncv),
    abnormal_data = get_tris_control_abnormal(adapter, ncv, 0),


def FetalFractionResponceModel(BatchResponceModel):
    control = get_ff_control_normal(adapter),
    cases = get_ff_cases(adapter, batch_id),


def FetalFractionXYResponceModel(FetalFractionResponceModel):
    abnormal = abnormal,
    max_x = max(control["FFX"]) + 1,
    min_x = min(control["FFX"]) - 1,


def CoverageResponceModel(BatchResponceModel):
    x_axis = list(range(1, 23)),
    scatter_data = scatter_data,
    box_data = box_data


def ReportResponceModel(BatchResponceModel):
    # NCV
    ncv_chrom_data = {
                         "13": get_tris_cases(adapter, "13", batch_id),
                         "18": get_tris_cases(adapter, "18", batch_id),
                         "21": get_tris_cases(adapter, "21", batch_id),
                     },
    normal_data = get_tris_control_normal(adapter, "21"),
    abnormal_data = get_tris_control_abnormal(adapter, "21", 0),
    # FF
    control = control,
    cases = get_ff_cases(adapter, batch_id),
    abnormal = get_ff_control_abnormal(adapter),
    max_x = max(control["FFX"]) + 1,
    min_x = min(control["FFX"]) - 1,
    # table
    sample_info = [get_sample_info(sample) for sample in samples],
    # coverage
    coverage = coverage,
    x_axis = list(range(1, 23)),
    scatter_data = scatter_data,
    box_data = box_data,
