# 概要

* `CodePipline`で利用
* `CodeBuild`で作成された成果物（zip）を解凍して、別の`S3`に配置するサンプル

# Deploy

```
$ yarn
$ zip -r src.zip index.js node_modules/
```