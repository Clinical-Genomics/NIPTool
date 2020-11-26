import logging
from NIPTool.build.document import build_sample, build_batch
from NIPTool.models.validation import requiered_fields
from NIPTool.exeptions import MissingResultsError
from pathlib import Path

import json


LOG = logging.getLogger(__name__)


def check_requiered_fields(document):
    """Check if document keys contain required fields"""

    if not set(requiered_fields).issubset(set(document.keys())):
        LOG.info(f"Could not add document {document}. Requiered fields missing.")
        return False
    return True


def load_batch(adapter, batch_data: dict, request_data: dict) -> None:
    """Function to load data from fluffy result file."""

    mongo_batch = build_batch(batch_data, request_data)
    adapter.add_or_update_document(mongo_batch, adapter.batch_collection)


def load_samples(adapter, batch_data: list, project_name: str) -> None:
    """Function to load data from fluffy result file."""

    for sample in batch_data:
        if not check_requiered_fields(sample):
            continue
        mongo_sample = build_sample(sample)
        mongo_sample["SampleProject"] = project_name
        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)


def load_concentrations(adapter, concentrations_file: str) -> None:
    """Function to load concentrations to samples in the database."""

    file = Path(concentrations_file)

    if not file.exists():
        raise MissingResultsError("Concentrations file missing.")

    with open(file) as data_file:
        concentrations = json.load(data_file)

    for sample, concentration in concentrations.items():
        mongo_sample = adapter.sample(sample)
        if not mongo_sample:
            LOG.warning(
                f"Trying to add concentration to sample {sample} but it doesnt exist in the database."
            )
            return
        mongo_sample["concentration"] = concentration

        adapter.add_or_update_document(mongo_sample, adapter.sample_collection)

