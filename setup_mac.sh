#!/bin/bash

# macOS用セットアップスクリプト

echo "╔══════════════════════════════════════════════╗"
echo "║    Video Content System Setup for macOS      ║"
echo "║    動画→ブログ自動化システムセットアップ     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Python3チェック
echo "📋 Python3チェック..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3が見つかりません"
    echo "Homebrewでインストール: brew install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# ffmpegチェック
echo ""
echo "📋 ffmpegチェック..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpegが見つかりません"
    echo "インストール: brew install ffmpeg"
    exit 1
fi
echo "✅ ffmpeg インストール済み"

# 仮想環境作成
echo ""
echo "🔧 Python仮想環境を作成..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 仮想環境作成完了"
else
    echo "✅ 仮想環境は既に存在します"
fi

# 仮想環境有効化
echo ""
echo "🔧 仮想環境を有効化..."
source venv/bin/activate

# pip アップグレード
echo ""
echo "📦 pipをアップグレード..."
pip install --upgrade pip

# 依存関係インストール
echo ""
echo "📦 依存関係をインストール..."
pip install -r requirements.txt

# Whisperテスト
echo ""
echo "🎤 Whisperの動作確認..."
python3 -c "import whisper; print('✅ Whisper インポート成功')"

# ディレクトリ作成
echo ""
echo "📁 必要なディレクトリを作成..."
mkdir -p output logs templates _posts cache uploads
echo "✅ ディレクトリ作成完了"

# 実行スクリプト作成
echo ""
echo "📝 実行スクリプトを更新..."
cat > run_mac.sh << 'EOF'
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
EOF

chmod +x run_mac.sh

# 完了メッセージ
echo ""
echo "=================================="
echo "✨ セットアップ完了！"
echo "=================================="
echo ""
echo "📋 使い方:"
echo ""
echo "1. 単一動画を処理:"
echo "   ./run_mac.sh video.mp4 '動画タイトル'"
echo ""
echo "2. Whisperモデルを変更:"
echo "   source venv/bin/activate"
echo "   python3 main.py video.mp4 --model small"
echo ""
echo "3. バッチ処理:"
echo "   source venv/bin/activate"
echo "   python3 main.py ./videos/ --batch"
echo ""
echo "💡 注意:"
echo "- 初回実行時はWhisperモデルのダウンロードに時間がかかります"
echo "- メモリ不足の場合は 'tiny' や 'base' モデルを使用してください"
echo ""