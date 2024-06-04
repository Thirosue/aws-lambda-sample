import boto3
import pytest
from datetime import datetime
from moto import mock_aws
from pydantic import BaseModel
from typing import Optional

from lambda_handler.csv_data_processor import CSVDataProcessor


class TestProcessor(CSVDataProcessor):
    def process_data(self, csv_data):
        return None


class TestSchema(BaseModel):
    col1: str
    col2: Optional[str]
    col3: int
    col4: Optional[datetime]


@pytest.fixture(scope="function")
def mock_s3():
    with mock_aws():
        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="mybucket")
        conn.create_bucket(Bucket="destbucket")
        yield


@pytest.fixture(scope="function")
def test_processor():
    processor = TestProcessor(
        source_bucket="mybucket",
        source_key="test.csv",
        model=TestSchema,
        dest_bucket="destbucket",
    )
    return processor


@mock_aws
def test_load_data(mock_s3, test_processor):
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.Object("mybucket", "test.csv").put(Body="col1,col2,col3,col4\nval1,,1,\n")

    response = test_processor.load_data()

    assert response == [TestSchema(col1="val1", col2="", col3=1, col4=None)]


@mock_aws
def test_save_data(mock_s3, test_processor):
    conn = boto3.resource("s3", region_name="us-east-1")

    data = [TestSchema(col1="val1", col2="", col3=1, col4=None)]
    test_processor.save_data(data)

    obj = conn.Object("destbucket", "test.csv").get()
    assert obj["Body"].read().decode("utf-8") == "col1,col2,col3,col4\nval1,,1,\n"
