# 概要

* GitHubにpushする

# ssh key settings

```
$ mkdir -p src/ssh
$ cd src/ssh
$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/Users/(username)/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
$ chmod 777 src/ssh/*
```

# Deploy

```
$ sam build
$ sam package --s3-bucket lambda-artifact-bucket-XXXXXXXXXXX --s3-prefix github-push-sample/prod --output-template-file packaged-template.yml
$ sam deploy --template-file packaged-template.yml --stack-name github-push --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides BucketName=sample-bucket FunctionName=SampleSyncS3toGIthub Committer='Name\ <test@exapmle.com>'
```