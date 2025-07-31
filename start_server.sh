#!/bin/bash

# シンプルな開発サーバー起動スクリプト

echo "🚀 開発サーバーを起動します..."
echo "📍 URL: http://localhost:8000"
echo "🛑 終了するには Ctrl+C を押してください"
echo ""
echo "📁 ブラウザで以下を確認できます:"
echo "  http://localhost:8000/output/  - 生成されたファイル"
echo "  http://localhost:8000/_posts/  - Jekyll記事"
echo ""

# Python 3のHTTPサーバーを起動
cd /Users/leadfive/Desktop/system/0731/blog-platform/video-content-system
python3 -m http.server 8000