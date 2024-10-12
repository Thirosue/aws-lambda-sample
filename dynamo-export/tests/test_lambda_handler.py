import os
import warnings
from io import StringIO
from unittest.mock import MagicMock, patch

import boto3
import pandas as pd
import pytest
from lambda_handler.lambda_handler import DynamoProcessor
from moto import mock_aws

bucket_name = os.environ["S3_DESTINATION_BUCKET"]
bucket_key = os.environ["S3_DESTINATION_KEY"]


@pytest.fixture(scope="function")
def mock_s3_fixture():
    with mock_aws():
        # Suppress DeprecationWarning
        warnings.simplefilter("ignore", DeprecationWarning)
        conn = boto3.resource("s3", region_name="ap-northeast-1")

        # Specify the LocationConstraint when creating the bucket
        conn.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-northeast-1"},
        )
        yield conn


# Sample data for parameterized tests
sample_data = [
    # Test Case 1: Single page, single item
    (
        [{"Items": [{"sub": "user1", "name": "Alice", "email": "alice@example.com"}]}],
        ["user1"],
        ["Alice"],
    ),
    # Additional test cases can be uncommented and added as needed
    # Test Case 2: Multiple pages, multiple items
    (
        [
            {
                "Items": [
                    {"sub": "user1", "name": "Bob", "email": "bob@example.com"},
                    {"sub": "user2", "name": "John", "email": "john@example.com"},
                ],
                "LastEvaluatedKey": "key1",
            },
            {
                "Items": [
                    {"sub": "user3", "name": "Charlie", "email": "charlie@example.com"}
                ]
            },
        ],
        ["user1", "user2", "user3"],
        ["Bob", "John", "Charlie"],
    ),
    # Test Case 3: Field exceeding maximum length
    (
        [
            {
                "Items": [
                    {
                        "sub": "user4",
                        "name": "AB01234567890123456789",
                        "email": "alice@example.com",
                    }
                ]
            }
        ],
        ["user4"],
        ["AB0123456789"],  # Expected truncated name
    ),
]


@pytest.mark.parametrize("dynamo_responses, expected_subs, expected_names", sample_data)
def test_load_data_to_s3(
    mock_s3_fixture, dynamo_responses, expected_subs, expected_names
):
    # Suppress DeprecationWarning
    warnings.simplefilter("ignore", DeprecationWarning)

    # Use the S3 resource from the fixture
    conn = mock_s3_fixture

    # Mock DynamoDB resource
    with patch(
        "lambda_handler.lambda_handler.boto3.resource"
    ) as mock_dynamodb_resource:
        # Create a mock table
        mock_table = MagicMock()
        mock_table.scan = MagicMock(side_effect=dynamo_responses)

        # Set up the mock DynamoDB resource to return our mock table
        mock_dynamodb_resource.return_value.Table.return_value = mock_table

        # Create an instance of DynamoProcessor and execute the method
        processor = DynamoProcessor()
        processor.load_data_to_s3()

        # Retrieve the CSV data from S3
        obj = conn.Object(bucket_name, bucket_key).get()
        csv_content = obj["Body"].read().decode("utf-8")

        # Load the CSV data into a DataFrame
        df = pd.read_csv(StringIO(csv_content))

        # Validate the results
        assert len(df) == len(expected_subs)
        for i, sub in enumerate(expected_subs):
            assert df.iloc[i]["sub"] == sub
            assert df.iloc[i]["name"] == expected_names[i]
