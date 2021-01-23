import boto3
import os
import json
import datetime
import shutil
import paramiko
import dulwich
import dulwich.client
from dulwich import porcelain
from dulwich.contrib.paramiko_vendor import _ParamikoWrapper

s3 = boto3.resource('s3')

class KeyParamikoSSHVendor(object):

    def __init__(self):
        # 秘密鍵のパスを書きます。
        self.ssh_kwargs = {'key_filename': './ssh/id_rsa'}

    def run_command(self, host, command, username=None, port=None):
        """ssh 接続でコマンドを実行します。たぶん。"""
        if port is None:
            port = 22
        client = paramiko.SSHClient()
        policy = paramiko.client.MissingHostKeyPolicy()
        client.set_missing_host_key_policy(policy)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, port=port, **self.ssh_kwargs)
        channel = client.get_transport().open_session()
        channel.exec_command(command)
        return _ParamikoWrapper(client, channel)


def lambda_handler(event, context):
    # ssh vendor を定義します。
    dulwich.client.get_ssh_vendor = KeyParamikoSSHVendor

    # コミット先のリポジトリです。環境変数 GITHUB_REPO は AWS Lambda で設定します。
    GITHUB_REPO = 'git@github.com:Thirosue/hosting-image.git'

    # 現在日時です。
    # NOTE: フォルダ名とかコミットメッセージに使用します。
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

    # Clone するフォルダです。
    # NOTE: AWS Lambda は一時作業ディレクトリとして /tmp を提供してくれています。
    local_repo_path = '/tmp/repo' + current_time

    # Clone
    repo = dulwich.porcelain.clone(
        GITHUB_REPO,
        target=local_repo_path,
    )

    # file modify
    bucket = s3.Bucket(os.environ['BUCKET_NAME'])
    bucket.download_file('public/0.min.json', f'{local_repo_path}/booking/public/0.min.json')

    # git add
    dulwich.porcelain.add(repo, f'{local_repo_path}/booking/public/0.min.json')

    print(os.listdir(f'{local_repo_path}/booking/public'))
    print(print(os.path.getsize(f'{local_repo_path}/booking/public/0.min.json')))

    # Commit
    # NOTE: 返り値は commit のハッシュ値みたいです。
    # NOTE: author と committer は両方設定します。でないと Lambda のログインユーザがコミッターになったりします。
    dulwich.porcelain.commit(
        repo,
        message=f'Update at {current_time}',
        author=os.environ['COMMITTER'],
        committer=os.environ['COMMITTER'],
    )

    # Push
    dulwich.porcelain.push(repo, GITHUB_REPO, 'master')

    # Clone した repository の片付けです。
    shutil.rmtree(local_repo_path)

    # リクエストの返却値です。
    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

# AWS Lambda に載せなくとも、これで実行することもできます。
# NOTE: 引数の event, context は関数内で使っていないのでてきとーです。
if __name__ == '__main__':
    lambda_handler(None, None)