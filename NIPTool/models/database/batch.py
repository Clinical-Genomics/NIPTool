from typing import Optional

from pydantic import BaseModel, Field


class Batch(BaseModel):
    SampleProject: str
    result_file: Optional[str]
    multiqc_report: Optional[str]
    segmental_calls: Optional[str]
    Flowcell: Optional[str]
    SequencingDate: Optional[str]
    Median_13: Optional[float]
    Median_18: Optional[float]
    Median_21: Optional[float]
    Median_X: Optional[float]
    Median_Y: Optional[float]
    Stdev_13: Optional[float]
    Stdev_18: Optional[float]
    Stdev_21: Optional[float]
    Stdev_X: Optional[float]
    Stdev_Y: Optional[float]

    class Config:
        validate_assignment = True
