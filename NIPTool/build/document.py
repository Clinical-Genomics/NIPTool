from NIPTool.models.constants import SAMPLE_KEYS, BATCH_KEYS
from typing import Optional


def build_document(csv_data: dict, document_keys: list) -> dict:
    """Build a general document"""

    document = {}
    for key in document_keys:
        value = csv_data.get(key)
        if value:
            document[key] = value

    return document


def build_sample(sample_data: dict) -> dict:
    """Builds a document for the sample collection"""

    sample = build_document(sample_data, SAMPLE_KEYS)
    sample["_id"] = sample_data["SampleID"]

    return sample


def build_batch(batch_data: dict, request_data: dict) -> dict:
    """Builds a document for the batch collection"""

    batch = build_document(batch_data, BATCH_KEYS)
    batch["_id"] = request_data['project_name']
    batch["fluffy_result_file"] = request_data['result_file']

    if request_data.get('multiqc_report'):
        batch["multiqc_report"] = request_data['multiqc_report']
    if request_data.get('segmental_calls'):
        batch["segmental_calls"] = request_data['segmental_calls']

    return batch
