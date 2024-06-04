from io import StringIO
from datetime import datetime
from typing import Dict, Generic, List, Type, Optional

import pandas as pd
from data_processor_base import DataProcessorBase, In, Out


class CSVDataProcessor(DataProcessorBase, Generic[In, Out]):
    def __init__(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        model: Type[In],
        dest_key: str = None,
    ):
        super().__init__(source_bucket, source_key, dest_bucket, dest_key)
        self.model = model

    def parse_model_from_dataframe_row(self, row: Dict) -> In:
        model_fields = self.model.__annotations__
        model_data = {}
        for field, field_type in model_fields.items():
            value = row.get(field)
            if field_type == Optional[datetime]:
                model_data[field] = pd.to_datetime(value) if value else None
            elif field_type == int:
                model_data[field] = int(value) if value else None
            elif field_type == str:
                model_data[field] = str(value) if value else None
            else:
                model_data[field] = value
        return self.model(**model_data)

    def load_data(self) -> List[In]:
        response = self.s3_client.get_object(
            Bucket=self.source_bucket, Key=self.source_key
        )
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data), keep_default_na=False)

        # データフレームの行ごとにPydanticモデルに変換
        models = [self.parse_model_from_dataframe_row(row) for _, row in df.iterrows()]
        return models

    def save_data(self, processed_data: List[Out]):
        df = pd.DataFrame([record.model_dump() for record in processed_data])
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        self.s3_client.put_object(
            Bucket=self.dest_bucket,
            Key=self.dest_key,
            Body=csv_buffer.getvalue(),
        )
