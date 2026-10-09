---
name: aws-operations
description: Operating rules for running AWS CLI commands and proposing AWS operations - the AWS_PROFILE prefix form, the profile confirmation, and what that confirmation shows for a billed or writing operation under a production profile (cost estimate, write destination), including Athena scan estimation. ALWAYS invoke before running or proposing any `aws` command, including ones that look read-only such as an Athena SELECT, a CloudWatch Logs Insights query, or an S3 listing, and when an AWS call under a read-only profile returns AccessDenied and another profile is being considered.
---

# AWS Operations

## profileの指定と確認

- AWS CLIを実行する際は `AWS_PROFILE=<profile> aws ...` の形式で環境変数をコマンドの先頭に付与する
    - settings.jsonのallow pattern（`Bash(AWS_PROFILE=stg-ro aws *)` 等）はこの形に一致するため
- 使用するprofileは必ずユーザーに確認してから実行する

## 本番profileで課金や書き込みを伴う操作

- 課金と書き込みの有無は、呼び出すAPIの課金対象と書き込み先で判定する
    - 例: on-demandのworkgroupでのAthenaの `SELECT` はスキャンしたバイト数で課金され、結果をクエリ結果の出力先に書き込む
- 本番アカウントのprofileで課金か書き込みを伴う操作を提案する時は、実行前に、profileを確認するメッセージに費用の見積もりと書き込み先を含める
    - 費用の見積もりには、算出根拠（対象のデータ量と単価）を添える
    - 書き込み先は、バケット、プレフィックス、テーブル等の場所と、書き込まれる内容で示す
    - ユーザーがprofileの承認と同時に費用と副作用を判断でき、実行開始後に止めてもそれまでの課金と書き込みは取り消せないため

## Athena

- スキャン量の目安を、クエリが読む対象パーティション配下のS3オブジェクトの合計サイズから見積もる
    - 例: `aws s3 ls s3://<bucket>/<prefix>/ --recursive --summarize` の `Total Size`
    - 期間が長い時は、1日分などの一部を実測して日数を掛ける
    - 列指向形式（Parquet、ORC）では読む列だけがスキャンされ、実際のスキャン量は目安より小さくなる
    - 同じテーブルを複数回読むクエリ（自己結合、繰り返し参照するCTE）や、パーティションを絞り込めない条件では、目安より大きくなる
- on-demandのworkgroupでは、費用はスキャン量に、料金ページにあるリージョンのTBあたり単価を掛けて出す
    - provisioned capacityのworkgroupはDPU時間で課金されるため、この計算は当てはまらない
- クエリ結果の出力先は、`aws athena get-work-group --work-group <name>` の結果から次の順で特定して示す
    - `WorkGroup.Configuration.ManagedQueryResultsConfiguration.Enabled` がtrueなら、Athenaが所有するストレージと示す
    - `WorkGroup.Configuration.EnforceWorkGroupConfiguration` がfalseで `--result-configuration` を渡すなら、その出力先を示す
    - それ以外は `WorkGroup.Configuration.ResultConfiguration.OutputLocation` を示す
    - キャンセルや失敗で終わったクエリも、それまでの部分的な結果をこの出力先に残すことがある
- CTAS、`INSERT INTO`、`UNLOAD` は文が指定する場所（`external_location`、挿入先テーブルのlocation、`UNLOAD` の `TO`）に書き込むので、その場所も示す

## read-only profileで権限が足りない時

- read-only profileがAccessDeniedを返し、書き込み権限のあるprofileを代わりに提案する時は、その操作が何をどこに書き込むかを同じメッセージで示す
    - read-only profileを使っていたこと自体が、書き込みを避けたいというユーザーの意図を表すため

## References

- https://aws.amazon.com/athena/pricing/
- https://docs.aws.amazon.com/athena/latest/ug/querying.html
