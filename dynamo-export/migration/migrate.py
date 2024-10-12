import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from faker import Faker

# Fakerの初期化
fake = Faker()

# DynamoDBリソースの作成
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
# dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='http://localhost:8000')

# テーブルの指定
table = dynamodb.Table("CognitoUserBackup")


def create_table():
    table = dynamodb.create_table(
        TableName="CognitoUserBackup",
        KeySchema=[{"AttributeName": "sub", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "sub", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    table.meta.client.get_waiter("table_exists").wait(TableName="CognitoUserBackup")
    print("Table created")
    return table


def generate_fake_user():
    user = {
        "sub": str(uuid.uuid4()),
        "name": fake.name(),
        "family_name": fake.last_name(),
        "given_name": fake.first_name(),
        "middle_name": fake.first_name(),
        "nickname": fake.user_name(),
        "preferred_username": fake.user_name(),
        "profile": fake.url(),
        "picture": fake.image_url(),
        "website": fake.url(),
        "gender": fake.random_element(elements=("male", "female", "other")),
        "birthdate": fake.date_of_birth().isoformat(),
        "zoneinfo": fake.timezone(),
        "locale": fake.locale(),
        "updated_at": int(fake.date_time().timestamp()),
        "address": {
            "formatted": fake.address(),
            "street_address": fake.street_address(),
            "locality": fake.city(),
            "region": fake.state(),
            "postal_code": fake.postcode(),
            "country": fake.country(),
        },
        "email": fake.email(),
        "phone_number": fake.phone_number(),
    }
    return user


def batch_insert_fake_users(start, count):
    """
    指定された範囲で、バッチ処理でユーザを挿入する
    """
    with table.batch_writer() as batch:
        for _ in range(start, start + count):
            user = generate_fake_user()
            batch.put_item(Item=user)
        print(f"Inserted batch from {start} to {start + count}")


def insert_fake_users_multithreaded(total_count, batch_size, max_workers=4):
    """
    マルチスレッドでバッチ書き込みを行う
    """
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, total_count, batch_size):
            futures.append(executor.submit(batch_insert_fake_users, i, batch_size))

        # 完了したタスクの確認
        for future in as_completed(futures):
            future.result()  # エラーチェック用


if __name__ == "__main__":
    # create_table()

    # 合計100,000ユーザを、バッチサイズ1000で、マルチスレッド4スレッドで処理
    insert_fake_users_multithreaded(total_count=100000, batch_size=1000, max_workers=4)
