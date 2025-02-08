from strategy.s3 import S3TransferStrategy
from strategy.sftp import SftpTransferOptions, SftpTransferStrategy
from transfer_base import TransferOptions, TransferStrategy

# --- Strategy マッピング ---
STRATEGY_MAP = {
    "sftp": {"option": SftpTransferOptions, "strategy": SftpTransferStrategy},
    "s3": {"option": TransferOptions, "strategy": S3TransferStrategy},
}


def get_transfer_strategy(protocol: str, options_data: dict) -> TransferStrategy:
    try:
        mapping = STRATEGY_MAP[protocol]
        # options は各プロトコルに合わせた Pydantic モデルでバリデーション
        option_cls = mapping["option"]
        options = option_cls(**options_data)
        # strategy インスタンスを生成
        strategy_instance = mapping["strategy"]()
        return strategy_instance, options
    except KeyError:
        raise ValueError(f"Unsupported protocol: {protocol}")


# --- Lambda ハンドラー ---
def lambda_handler(event, context):
    """
    イベント例:
    {
        "protocol": "sftp",
        "source": "/var/task/app.py",
        "destination": "/home/ec2-user/app.py",
        "options": {
            "host": "sftp.example.com",
            "username": "ec2-user",
            "credential_id": "/EC2/private_key/i-09ea578c391a739ec",
        }
    }
    """
    try:
        protocol = event.get("protocol")
        source = event.get("source")
        destination = event.get("destination")
        options_data = event.get("options", {})

        # マッピングから strategy インスタンスと転送設定を取得
        strategy, options = get_transfer_strategy(protocol, options_data)
        result = strategy.transfer(source, destination, options)

        return {"statusCode": 200, "body": result}

    except Exception as e:
        return {"statusCode": 500, "body": f"Error occurred: {str(e)}"}
