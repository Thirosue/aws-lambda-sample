from typing import Any, Dict

from transfer_base import TransferOptions, TransferStrategy


class S3TransferStrategy(TransferStrategy):
    def transfer(
        self, source: str, destination: str, options: TransferOptions
    ) -> Dict[str, Any]:
        return {
            "protocol": "s3",
            "source": source,
            "destination": destination,
            "bucket": "dummy",
        }
