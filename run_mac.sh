#!/bin/bash

# macOS用実行スクリプト

# 引数チェック
if [ $# -lt 1 ]; then
    echo "使用方法: $0 <動画ファイル> [タイトル]"
    echo "例: $0 video.mp4 'AIツールの使い方'"
    exit 1
fi

# 仮想環境有効化
source venv/bin/activate

# メインスクリプト実行
if [ -n "$2" ]; then
    python3 main.py "$1" --title "$2"
else
    python3 main.py "$1"
fi
