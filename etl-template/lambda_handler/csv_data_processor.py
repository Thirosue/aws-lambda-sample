from io import StringIO
from typing import Dict, Generic, List

import pandas as pd
from data_processor_base import DataProcessorBase, In, Out


class CSVDataProcessor(DataProcessorBase, Generic[In, Out]):
    def load_data(self) -> List[Dict]:
        response = self.s3_client.get_object(
            Bucket=self.source_bucket, Key=self.source_key
        )
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data), keep_default_na=False)

        return df.to_dict(orient="records")

    def save_data(self, processed_data: List[Out]):
        df = pd.DataFrame([record.model_dump() for record in processed_data])
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        self.s3_client.put_object(
            Bucket=self.dest_bucket,
            Key=self.dest_key,
            Body=csv_buffer.getvalue(),
        )
