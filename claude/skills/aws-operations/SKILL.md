---
name: aws-operations
description: Operating rules for running AWS CLI commands and proposing AWS operations - the AWS_PROFILE prefix form, the profile confirmation, and what that confirmation shows for a billed or writing operation under a production profile (cost estimate, write destination), including Athena scan estimation. ALWAYS invoke before running or proposing any `aws` command, including ones that look read-only such as an Athena SELECT, a CloudWatch Logs Insights query, or an S3 listing, and when an AWS call under a read-only profile returns AccessDenied and another profile is being considered.
---

# AWS Operations

## profileの指定と確認

- AWS CLIを実行する際は必ず `AWS_PROFILE=<profile> aws ...` の形式で環境変数をコマンドの先頭に付与する
    - settings.jsonのallow pattern（`Bash(AWS_PROFILE=stg-ro aws *)` 等）はこの形に一致するため
- 使用するprofileは必ずユーザーに確認してから実行する

## 本番profileで課金・書き込みを伴う操作

- 操作が課金されるか、書き込みを伴うかは、SQLやサブコマンドの動詞ではなく、呼び出すAPIが何に課金し何を書き込むかで判定する
    - 例: Athenaの `SELECT` はスキャンしたバイト数で課金され、結果をクエリ結果の出力先に書き込む
- 本番アカウントのprofileでこの種の操作を提案する時は、実行前に、profileを確認するメッセージに次の2点を含める
    - 費用の見積もりと、その算出根拠（対象のデータ量と単価）
    - 書き込み先（バケット・プレフィックス・テーブル等）と、書き込まれる内容
- 見積もりと書き込み先はprofileの確認と同じメッセージで示す
    - ユーザーがprofileの承認と同時に費用と副作用を判断でき、実行開始後に示しても課金と書き込みは止められないため

## Athena

- スキャン量は、クエリが読む対象パーティション配下のS3オブジェクトの合計サイズから見積もる
    - 例: `aws s3 ls s3://<bucket>/<prefix>/ --recursive --summarize` の `Total Size`
    - 期間が長い時は、1日分などの一部を実測して日数を掛ける
- 費用はスキャン量に、料金ページにあるリージョンのTBあたり単価を掛けて出す
- 書き込み先は、使うworkgroupの設定から特定する
    - `aws athena get-work-group --work-group <name>` の `WorkGroup.Configuration.ResultConfiguration.OutputLocation`
    - `ManagedQueryResultsConfiguration.Enabled` がtrueなら、結果はAthenaが所有するストレージに保存される
    - `EnforceWorkGroupConfiguration` がfalseなら、`--result-configuration` で指定した出力先がworkgroupの設定より優先される

## read-only profileで権限が足りない時

- read-only profileがAccessDeniedを返し、書き込み権限のあるprofileを代わりに提案する時は、その操作が何をどこに書き込むかを同じメッセージで示す
    - read-only profileを使っていたこと自体が、書き込みを避けたいというユーザーの意図を表すため

## References

- https://aws.amazon.com/athena/pricing/
- https://docs.aws.amazon.com/athena/latest/ug/querying.html
