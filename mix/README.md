# 概要

`e2e`テストの終了処理

+ `e2e`テストは`EC2`で実施
+ `e2e`テストは、`mochawesome`で実施
+ `e2e`テスト結果は、`EC2`より`S3`にsyncしている前提（※`S3`のPutイベントを本`Lambda`ファンクションのトリガーとする）
+ `mochawesome`のjson出力を元に、Slackの通知内容を切り分ける

# Deploy

```
$ yarn
$ zip -r src.zip index.js node_modules/
```