#!/usr/bin/env bash
set -euo pipefail

# git diffの出力を取得（ステージング済みの変更を優先、なければ未ステージングの変更）
DIFF=$(git diff --staged)
if [ -z "$DIFF" ]; then
    DIFF=$(git diff)
fi

# 変更がない場合は終了
if [ -z "$DIFF" ]; then
    echo "変更がないで。コミットするもんがないわ。" >&2
    exit 1
fi

# codex execでコミットメッセージを生成
echo "コミットメッセージ生成中..." >&2
PROMPT="以下のgit diffの出力を元に、適切なコミットメッセージを生成してください。
git diffコマンドを実行しないでください。
形式は「動詞: 変更内容」の形式で、簡潔に1行で記述してください。
メッセージのみを出力し、説明や追加のテキストは不要です。

--- git diff の出力 ---
$DIFF
--- ここまで ---"

COMMIT_MSG=$(echo "$PROMPT" | codex exec -)

# 生成されたメッセージを表示
echo "生成されたコミットメッセージ:" >&2
echo "$COMMIT_MSG" >&2
echo "" >&2

# ステージングされていない変更がある場合は全てステージング
if [ -z "$(git diff --staged)" ]; then
    git add -A
fi

# 一時ファイルにコミットメッセージを保存してエディターで開く
TEMP_MSG=$(mktemp)
echo "$COMMIT_MSG" > "$TEMP_MSG"

# コミット実行（エディターが開く）
git commit -t "$TEMP_MSG"

# 一時ファイルを削除
rm -f "$TEMP_MSG"

echo "コミット完了や！" >&2
