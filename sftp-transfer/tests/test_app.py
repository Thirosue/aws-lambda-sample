import pytest
from src.app import lambda_handler


def test_lambda_handler_sftp(monkeypatch):
    event = {
        "protocol": "s3",
        "source": "/var/task/app.py",
        "destination": "/home/ec2-user/app.py",
        "options": {},
    }

    result = lambda_handler(event, None)
    assert result["statusCode"] == 200
    body = result["body"]
    assert body["source"] == "/var/task/app.py"
    assert body["destination"] == "/home/ec2-user/app.py"
