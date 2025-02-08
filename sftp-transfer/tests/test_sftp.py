import paramiko
import pytest
from src.strategy.sftp import SftpTransferOptions, SftpTransferStrategy


# ダミー SFTP クラス（put 呼び出しを記録）
class DummySFTP:
    def __init__(self):
        self.put_called = False
        self.source = None
        self.destination = None

    def put(self, source, destination):
        self.put_called = True
        self.source = source
        self.destination = destination

    def close(self):
        pass


# ダミー SSHClient クラス
class DummySSHClient:
    def __init__(self):
        self.sftp = DummySFTP()

    def set_missing_host_key_policy(self, policy):
        self.policy = policy

    def connect(self, hostname, port, username, pkey):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.pkey = pkey

    def open_sftp(self):
        return self.sftp

    def close(self):
        pass


# pytest の monkeypatch を使って paramiko のクラスと秘密鍵取得関数をモックする
@pytest.fixture(autouse=True)
def patch_paramiko(monkeypatch):
    dummy_key = object()  # ダミーの秘密鍵オブジェクト
    # SSHClient をダミー版に差し替え
    monkeypatch.setattr(paramiko, "SSHClient", lambda: DummySSHClient())
    # RSAKey.from_private_key をダミーに差し替え
    monkeypatch.setattr(paramiko.RSAKey, "from_private_key", lambda file: dummy_key)
    # sftp.py 内でインポートされている retrieve_private_key_from_ssm をダミー関数に差し替え
    monkeypatch.setattr(
        "src.strategy.sftp.retrieve_private_key_from_ssm",
        lambda credential_id: "dummy_key_str",
    )


def test_sftp_transfer():
    strategy = SftpTransferStrategy()
    options_data = {
        "host": "sftp.example.com",
        "username": "ec2-user",
        "credential_id": "/EC2/private_key/dummy",
    }
    options = SftpTransferOptions(**options_data)
    source = "/var/task/app.py"
    destination = "/home/ec2-user/app.py"

    result = strategy.transfer(source, destination, options)
    # 戻り値が success であることを確認
    assert result["status"] == "success"
