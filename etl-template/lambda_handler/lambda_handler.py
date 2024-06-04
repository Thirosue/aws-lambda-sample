import os
from typing import Dict, List

from csv_data_processor import CSVDataProcessor
from schema import InputSchema, OutPutSchema

dest_bucket = os.environ["S3_DESTINATION_BUCKET"]


class SampleProcessor(CSVDataProcessor[InputSchema, OutPutSchema]):
    def process_data(self, csv_data: List[InputSchema]) -> List[OutPutSchema]:
        return [
            OutPutSchema(
                name=f"{item.first_name} {item.last_name}", is_deleted=item.deleted
            )  # create output schema edit here
            for item in csv_data
            if not item.deleted  # filter out deleted items
        ]


def lambda_handler(event, context):
    src_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    src_key = event["Records"][0]["s3"]["object"]["key"]

    processor = SampleProcessor(src_bucket, src_key, dest_bucket, model=InputSchema)
    processor.process()

    return {"statusCode": 200, "body": "Process completed."}


# run lambda_handler
if __name__ == "__main__":
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "source-bucket"},
                    "object": {"key": "dummy.csv"},
                }
            }
        ]
    }
    lambda_handler(event, None)
