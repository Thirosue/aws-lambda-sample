from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar

import boto3
from pydantic import BaseModel

In = TypeVar("In", bound=BaseModel)
Out = TypeVar("Out", bound=BaseModel)


class DataProcessorBase(ABC, Generic[In, Out]):
    def __init__(self, source_bucket, source_key, dest_bucket, dest_key=None):
        self.source_bucket = source_bucket
        self.source_key = source_key
        self.dest_bucket = dest_bucket
        self.dest_key = dest_key if dest_key else source_key
        self.s3_client = boto3.client("s3")

    def process(self):
        csv_data = self.load_data()
        processed_data = self.process_data(csv_data)
        self.save_data(processed_data)

    @abstractmethod
    def load_data(self) -> List[In]:
        pass

    @abstractmethod
    def process_data(self, csv_data: List[Dict]) -> List[Out]:
        pass

    @abstractmethod
    def save_data(self, processed_data: List[Out]):
        pass
