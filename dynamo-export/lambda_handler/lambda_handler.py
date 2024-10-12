import os
import time
from io import StringIO
from typing import List

import boto3
import pandas as pd
from pydantic import ValidationError
from schema import OutputSchema

# 環境変数の取得
src_table = os.environ.get("DYNAMODB_TABLE", "CognitoUserBackup")
dest_bucket = os.environ.get("S3_DESTINATION_BUCKET", "your-destination-bucket")
dest_key = os.environ.get("S3_DESTINATION_KEY", "output.csv")


class DynamoProcessor:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        self.s3 = boto3.client("s3", region_name="ap-northeast-1")
        self.table = self.dynamodb.Table(src_table)

    def load_data_to_s3(self, batch_size=1000):
        scan_kwargs = {}
        total_items = 0
        is_first_batch = True  # ヘッダー行の制御

        csv_buffer = StringIO()

        while True:
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])
            batch_data = []

            for item in items:
                user_data = {
                    "sub": item.get("sub"),
                    "name": item.get("name"),
                    "family_name": item.get("family_name"),
                    "given_name": item.get("given_name"),
                    "middle_name": item.get("middle_name"),
                    "nickname": item.get("nickname"),
                    "preferred_username": item.get("preferred_username"),
                    "profile": item.get("profile"),
                    "picture": item.get("picture"),
                    "website": item.get("website"),
                    "gender": item.get("gender"),
                    "birthdate": item.get("birthdate"),
                    "zoneinfo": item.get("zoneinfo"),
                    "locale": item.get("locale"),
                    "updated_at": item.get("updated_at"),
                    "address": item.get("address"),
                    "email": item.get("email"),
                    "phone_number": item.get("phone_number"),
                }
                # OutputSchemaを使用してデータを検証し、長さ制限を適用
                validated_user_data = OutputSchema(**user_data)
                batch_data.append(validated_user_data.dict())

            # データをCSVに変換
            df = pd.DataFrame(batch_data)

            # CSV形式でS3に書き込み（最初のバッチのみヘッダー付き）
            if not df.empty:
                df.to_csv(csv_buffer, header=is_first_batch, index=False, mode="a")

                # S3にアップロード（appendモードでアップロード）
                # self.s3.put_object(
                #     Bucket=dest_bucket,
                #     Key=dest_key,
                #     Body=csv_buffer.getvalue()
                # )

                is_first_batch = False  # 次回以降のバッチではヘッダー行を出力しない

            total_items += len(batch_data)
            print(f"Processed {total_items} items")

            # ページネーションのチェック
            last_evaluated_key = response.get("LastEvaluatedKey")
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key
            else:
                break  # データ取得完了

        # S3にストリーミングで書き込む
        # 処理時間短縮のため、一括でアップロードする
        self.s3.put_object(Bucket=dest_bucket, Key=dest_key, Body=csv_buffer.getvalue())
        print(f"Data successfully uploaded to S3: {dest_key}")


def lambda_handler(event, context):
    # DynamoDB からデータを取得し、CSV を生成
    start_time = time.time()
    processor = DynamoProcessor()
    processor.load_data_to_s3()
    print(f"elapsed_time: {time.time() - start_time}")

    return {"statusCode": 200, "body": "Process completed."}


# run lambda_handler
if __name__ == "__main__":
    lambda_handler(None, None)
