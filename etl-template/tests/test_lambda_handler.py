import pytest
from datetime import datetime

from lambda_handler.lambda_handler import InputSchema, OutPutSchema, SampleProcessor


@pytest.fixture(scope="function")
def test_processor():
    processor = SampleProcessor(
        source_bucket="mybucket",
        source_key="test.csv",
        model=InputSchema,
        dest_bucket="destbucket",
    )
    return processor


def test_process_data(test_processor):
    response = test_processor.process_data(
        [
            InputSchema(
                first_name="John", last_name="Doe", timestamp=datetime.now(), deleted=0
            ),
            InputSchema(
                first_name="Jane", last_name="Doe", timestamp=datetime.now(), deleted=1
            ),
            InputSchema(
                first_name="John", last_name="Does", timestamp=datetime.now(), deleted=0
            ),
        ]
    )
    assert response == [
        OutPutSchema(name="John Doe", is_deleted=0),
        OutPutSchema(name="John Does", is_deleted=0),
    ]
