import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../lambda_handler"))
)

# env variables
os.environ["S3_DESTINATION_BUCKET"] = "your-destination-bucket"
os.environ["S3_DESTINATION_KEY"] = "output.csv"
os.environ["DYNAMODB_TABLE"] = "CognitoUserBackup"
