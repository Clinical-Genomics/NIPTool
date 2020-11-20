  
from NIPTool.parse.batch import parse_batch_file	
import pytest	
from NIPTool.exeptions import MissingResultsError, FileValidationError

def test_parse_batch(valid_csv):	
    # GIVEN a valid csv file 	
    # WHEN running parse_batch_file
    results = parse_batch_file(valid_csv)	

    # THEN assert results is a list and it has length 3
    assert isinstance(results, list)
    assert len(results)==3


def test_parse_batch_file_with_missing_data(invalid_csv):	
    # GIVEN a csv file with missing SampleID

    # WHEN running parse_batch_file
    results = parse_batch_file(invalid_csv)	

    # THEN assert results is a list and it has length 3
    assert isinstance(results, list)
    for sample in results:
        assert sample == {}


def test_parse_batch_file_with_missing_file():	
    # GIVEN a non existing csv file

    # WHEN running parse_batch_file	

    # THEN assert MissingResultsError
    with pytest.raises(MissingResultsError):	
        parse_batch_file('file_path')