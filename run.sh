#!/bin/bash

# Video Content System 実行スクリプト
# 使用方法: ./run.sh video.mp4 "タイトル"

set -e

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# バナー表示
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║       Video Content System                   ║"
echo "║    動画→ブログ自動変換システム              ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# 引数チェック
if [ $# -lt 1 ]; then
    echo -e "${RED}エラー: 動画ファイルを指定してください${NC}"
    echo "使用方法: $0 <動画ファイル> [タイトル]"
    echo "例: $0 video.mp4 'AIツールの使い方'"
    exit 1
fi

VIDEO_FILE="$1"
TITLE="${2:-}"

# ファイル存在確認
if [ ! -f "$VIDEO_FILE" ]; then
    echo -e "${RED}エラー: 動画ファイルが見つかりません: $VIDEO_FILE${NC}"
    exit 1
fi

# Python環境確認
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}エラー: Python3がインストールされていません${NC}"
    exit 1
fi

# ffmpeg確認
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}警告: ffmpegがインストールされていません${NC}"
    echo "動画情報の取得ができない可能性があります"
fi

# 実行
echo -e "${GREEN}🎬 処理開始${NC}"
echo "動画: $VIDEO_FILE"
if [ -n "$TITLE" ]; then
    echo "タイトル: $TITLE"
fi
echo "================================"

# メインスクリプト実行
if [ -n "$TITLE" ]; then
    python3 main.py "$VIDEO_FILE" --title "$TITLE"
else
    python3 main.py "$VIDEO_FILE"
fi

# 完了メッセージ
echo -e "\n${GREEN}✅ 処理完了！${NC}"
echo "出力ファイルを確認してください:"
echo "  - Jekyll記事: _posts/"
echo "  - その他: output/"

# Jekyllサーバー起動オプション
read -p "Jekyllサーバーを起動しますか？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v jekyll &> /dev/null; then
        echo -e "${GREEN}🚀 Jekyllサーバー起動中...${NC}"
        bundle exec jekyll serve --watch
    else
        echo -e "${YELLOW}Jekyllがインストールされていません${NC}"
        echo "インストール: gem install bundler jekyll"
    fi
fi