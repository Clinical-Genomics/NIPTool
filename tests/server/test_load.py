import json


def test_user(mock_app):
    # GIVEN the following request data:
    data = dict(email='maya.papaya@something.se', name="Maya Papaya", role="RW")

    # WHEN running the user request with the data
    response = mock_app.test_client().post('/user', data=data)

    # The user should be added to the database
    assert mock_app.adapter.user_collection.estimated_document_count() == 1
    resp_data = json.loads(response.data)
    assert resp_data["message"] == "Data loaded into database"
    assert response.status_code == 200

def test_user_empty_data(mock_app):
    # GIVEN no data

    # WHEN running the user request with empty data
    response = mock_app.test_client().post('/user', data=dict())

    # THEN assert BadRequestKeyError: 400 Bad Request
    assert response.status_code == 400


def test_batch_valid_files(mock_app, valid_concentrations, valid_csv, segmental_calls, multiqc_report):
    # GIVEN the following request data:
    #   a valid csv file with three samples
    #   a valid concentrations file
    #   segmental_calls and multiqc_report files with random content, but that do exist.

    project_name = "project_name"
    data = dict(multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=valid_csv,
                concentrations=valid_concentrations, project_name=project_name)

    # WHEN running the request with the data
    response = mock_app.test_client().post('/batch', data=data)

    # THEN assert the samples should be added to the sample collection
    # and the batch should be added to the batch collection
    assert mock_app.adapter.sample_collection.estimated_document_count() == 3
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1
    resp_data = json.loads(response.data)
    assert resp_data["message"] == "Data loaded into database"
    assert response.status_code == 200


def test_batch_no_data(mock_app):
    # GIVEN no data

    # WHEN running the request with empty data
    response = mock_app.test_client().post('/batch', data=dict())

    # THEN assert nothing added to sample or batch collections
    assert mock_app.adapter.sample_collection.estimated_document_count() == 0
    assert mock_app.adapter.batch_collection.estimated_document_count() == 0

    # THEN assert BadRequestKeyError: 400 Bad Request
    assert response.status_code == 400


def test_batch_missing_files(mock_app, valid_concentrations, valid_csv):
    # GIVEN the following request data:
    #   a valid csv file with three samples
    #   a valid concentrations file
    #   but no segmental_calls and multiqc_report

    data = dict(result_file=valid_csv, concentrations=valid_concentrations, project_name="project_name")

    # WHEN running the request with the data
    response = mock_app.test_client().post('/batch', data=data)

    # THEN assert the samples are being added
    assert mock_app.adapter.sample_collection.estimated_document_count() == 3

    # THEN assert batch is being added without error
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1
    resp_data = json.loads(response.data)
    assert resp_data["message"] == "Data loaded into database"
    assert response.status_code == 200


def test_batch_invalid_file(mock_app, valid_concentrations, invalid_csv, segmental_calls, multiqc_report):
    # GIVEN the following request data:
    #   a invalid csv file with three samples - required field SampleID has bad format
    #   a valid concentrations file
    #   segmental_calls and multiqc_report files with random content, but that do exist.

    project_name = "project_name"
    data = dict(multiqc_report=multiqc_report, segmental_calls=segmental_calls, result_file=invalid_csv,
                concentrations=valid_concentrations, project_name=project_name)

    # WHEN running the3 request with the data
    response = mock_app.test_client().post('/batch', data=data)

    # THEN assert nothing added to sample the collection
    assert mock_app.adapter.sample_collection.estimated_document_count() == 0

    # THEN assert batch collection added with expected keys
    keys = ['_id', 'multiqc_report', 'segmental_calls', 'fluffy_result_file', 'added']
    assert mock_app.adapter.batch_collection.estimated_document_count() == 1
    assert set(mock_app.adapter.batch(project_name).keys()) == set(keys)
    resp_data = json.loads(response.data)
    assert resp_data["message"] == "Data loaded into database"
    assert response.status_code == 200


