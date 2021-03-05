import csv
import logging
from pathlib import Path

from typing import Optional, List, Dict
from pydantic import parse_obj_as

from NIPTool.schemas import db_models

LOG = logging.getLogger(__name__)

def pars_segmental_calls(segmental_calls_path: Optional[str]) -> dict:
    """Builds a dict with segmental calls bed files.
        key: sample ids
        value: bed file path"""

    segmental_calls = {}
    if not validate_file_path(segmental_calls_path):
        return segmental_calls

    segmental_calls_dir = Path(segmental_calls_path)
    if not segmental_calls_dir.exists():
        LOG.info('Segmental Calls file path missing.')
        return segmental_calls

    for file in segmental_calls_dir.iterdir():
        if file.suffix == '.bed':
            sample_id = file.name.split('.')[0]
            segmental_calls[sample_id] = str(file.absolute())

    return segmental_calls


def validate_file_path(file_path: Optional[str])-> bool:
    """File path validation"""

    if not file_path:
        return False

    file = Path(file_path)

    if not file.exists():
        return False

    return True

def convert_empty_str_to_none(data: dict) -> dict:
    """Convert all values that are empty string to None in a dict"""
    for key, value in data.items():
        if not value:
            data[key] = None
    return data

def parse_csv(infile: Path) -> List[Dict[str, str]]:
    with open(infile, "r") as csv_file:
        entries = [convert_empty_str_to_none(entry) for entry in csv.DictReader(csv_file)]
    return entries


def get_samples(nipt_results_path: Path) -> List[db_models.SampleModel]:
    """Parse NIPT result file into samples"""

    return parse_obj_as(List[db_models.SampleModel], parse_csv(nipt_results_path))


def get_batch(nipt_results_path: Path) -> db_models.BatchModel:
    """Parse NIPT result file and create a batch object from the first sample information"""

    sample_data: List[dict] = parse_csv(nipt_results_path)

    return db_models.BatchModel.parse_obj(sample_data[0])