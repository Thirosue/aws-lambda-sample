import pytest

from lambda_handler.lambda_handler import OutPutSchema, SampleProcessor


@pytest.fixture(scope="function")
def test_processor():
    processor = SampleProcessor(
        source_bucket="mybucket", source_key="test.csv", dest_bucket="destbucket"
    )
    return processor


def test_process_data(test_processor):
    response = test_processor.process_data(
        [
            {"first_name": "John", "last_name": "Doe", "deleted": 0},
            {"first_name": "Jane", "last_name": "Doe", "deleted": 1},
            {"first_name": "John", "last_name": "Does", "deleted": 0},
        ]
    )
    assert response == [
        OutPutSchema(name="John Doe", is_deleted=0),
        OutPutSchema(name="John Does", is_deleted=0),
    ]
