#!/bin/bash
# VideoAI Studio クイックスタート

echo "🚀 VideoAI Studio を起動します..."

# 仮想環境がなければ作成
if [ ! -d "venv" ]; then
    echo "📦 初回セットアップ中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 必要なパッケージをインストール（初回のみ）
if [ ! -f "venv/.installed" ]; then
    echo "📦 必要なパッケージをインストール中..."
    pip install --upgrade pip
    pip install -r requirements.txt
    # FastAPIが確実にインストールされるよう追加
    pip install fastapi uvicorn python-multipart aiofiles
    touch venv/.installed
    echo "✅ インストール完了"
fi

# Webアプリを起動
echo "🌐 Webアプリを起動中..."
echo "📍 ブラウザで http://localhost:8004 を開いてください"
echo ""
echo "終了するには Ctrl+C を押してください"
echo ""
python web_app.py