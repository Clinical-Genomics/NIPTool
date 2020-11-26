from NIPTool.build.document import build_batch, build_sample
from NIPTool.models.constants import BATCH_KEYS, SAMPLE_KEYS
import pytest


@pytest.mark.parametrize("sample_key", SAMPLE_KEYS)
@pytest.mark.parametrize("value", [124, 2.08, "randomstring"])
def test_build_sample(sample_key, value):
    # GIVEN a sample_data dict with requiered key 'SampleID' and a sample_key with some value and a non sample_key

    sample_data = {"SampleID": "someid", sample_key: value, "other_key": 8983}

    # WHEN building a mongo sample
    mongo_sample = build_sample(sample_data=sample_data)

    # THEN the SampleID will be _id and the non sample key will be removed
    assert mongo_sample == {"_id": "someid", sample_key: value}


@pytest.mark.parametrize("batch_key", BATCH_KEYS)
@pytest.mark.parametrize("value", [124, 2.08, "randomstring"])
def test_build_batch(batch_key, value):
    # GIVEN a batch_data dict a batch_key with some value and a non batch_key

    batch_data = {batch_key: value, "other_key": 8983}
    project_name = "project_name"
    file_path = "path"
    request_data = {"result_file": file_path, "project_name": project_name}
    # WHEN building a mongo batch
    mongo_batch = build_batch(batch_data=batch_data, request_data=request_data)

    # THEN the non batch_key will be removed
    assert mongo_batch == {'_id': project_name, 'fluffy_result_file': file_path, batch_key: value}
