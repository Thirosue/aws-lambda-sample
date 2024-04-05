import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../lambda_handler"))
)

# env variables
os.environ["S3_DESTINATION_BUCKET"] = "my-test-bucket"
