import io
from typing import Any, Dict, Optional

import paramiko
from transfer_base import (
    TransferOptions,
    TransferStrategy,
    retrieve_private_key_from_ssm,
)


class SftpTransferOptions(TransferOptions):
    host: str
    port: Optional[int] = 22
    username: str
    credential_id: str


class SftpTransferStrategy(TransferStrategy):
    def transfer(
        self, source: str, destination: str, options: SftpTransferOptions
    ) -> Dict[str, Any]:
        try:
            private_key_str = retrieve_private_key_from_ssm(options.credential_id)

            private_key_file = io.StringIO(private_key_str)
            private_key = paramiko.RSAKey.from_private_key(private_key_file)

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=options.host,
                port=options.port,
                username=options.username,
                pkey=private_key,
            )

            sftp = ssh.open_sftp()
            sftp.put(source, destination)
            sftp.close()
            ssh.close()

            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
