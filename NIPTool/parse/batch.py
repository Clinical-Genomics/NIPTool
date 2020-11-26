import logging
import pandas
from pathlib import Path

from typing import Optional, List

from NIPTool.exeptions import MissingResultsError
from NIPTool.models.validation import (
    ints,
    floats,
    strings,
    exceptions,
)

LOG = logging.getLogger(__name__)



def form(val: Optional, function) -> Optional:
    """Returning formatted value or None"""

    try:
        return function(val)
    except:
        return None


def validate(key: str, val: Optional) -> Optional:
    """Formatting value according to defined models."""

    if val in exceptions:
        formatted_value = None
    elif key in ints:
        formatted_value = form(val, int)
    elif key in floats:
        formatted_value = form(val, float)
    elif key in strings:
        formatted_value = form(val, str)
    else:
        formatted_value = None
    return formatted_value


def parse_batch_file(nipt_results_path: str) -> List[dict]:
    """Parsing file content. Formatting values. Ignoring values
    that could not be formatted according to defined models"""

    file = Path(nipt_results_path)

    if not file.exists():
        raise MissingResultsError("Results file missing.")

    data_frame = pandas.read_csv(file, na_filter=False)
    results = data_frame.to_dict(orient="records")

    samples = []
    for sample in results:
        formatted_results = {}
        for key, val in sample.items():
            formatted_value = validate(key, val)
            if formatted_value is None:
                LOG.info(f"invalid format of {key}.")
                continue
            formatted_results[key] = formatted_value
        samples.append(formatted_results)

    return samples
