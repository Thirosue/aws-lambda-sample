# 概要

* zipファイルを解凍して、別の`s3`に同期する
> `CodePipline`で作成された最新の成果物を別の`s3`へコピーする

# Deploy

```
$ yarn
$ zip -r src.zip index.js node_modules/
```