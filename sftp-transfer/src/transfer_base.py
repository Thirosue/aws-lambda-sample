import io
from typing import Any, Dict

import boto3
from pydantic import BaseModel


class TransferOptions(BaseModel):
    pass


class TransferStrategy:
    def transfer(
        self, source: str, destination: str, options: TransferOptions
    ) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")


def retrieve_private_key_from_ssm(credential_id: str) -> str:
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=credential_id, WithDecryption=True)
    return response["Parameter"]["Value"]
