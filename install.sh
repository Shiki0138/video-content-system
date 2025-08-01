#!/bin/bash
# VideoAI Studio ワンライナーインストールスクリプト

echo "🚀 VideoAI Studio インストーラー"
echo "================================"

# OSを検出
OS="Unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
fi

echo "📍 検出されたOS: $OS"

# 必要なツールのチェック
check_requirements() {
    local missing=()
    
    # Python3チェック
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi
    
    # Gitチェック
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    # ffmpegチェック
    if ! command -v ffmpeg &> /dev/null; then
        missing+=("ffmpeg")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo "❌ 以下のツールがインストールされていません:"
        printf '%s\n' "${missing[@]}"
        
        if [[ "$OS" == "Mac" ]]; then
            echo ""
            echo "📦 Homebrewを使ってインストールできます:"
            echo "brew install ${missing[@]}"
        elif [[ "$OS" == "Linux" ]]; then
            echo ""
            echo "📦 apt-getを使ってインストールできます:"
            echo "sudo apt-get update && sudo apt-get install -y ${missing[@]}"
        fi
        
        echo ""
        read -p "続行しますか？ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "✅ 必要なツールは全てインストール済みです"
    fi
}

# インストール先の選択
select_install_dir() {
    echo ""
    echo "📁 インストール先を選択してください:"
    echo "1) デスクトップ (推奨)"
    echo "2) ホームディレクトリ"
    echo "3) 現在のディレクトリ"
    echo "4) カスタムパス"
    
    read -p "選択 (1-4): " choice
    
    case $choice in
        1)
            INSTALL_DIR="$HOME/Desktop/video-content-system"
            ;;
        2)
            INSTALL_DIR="$HOME/video-content-system"
            ;;
        3)
            INSTALL_DIR="$(pwd)/video-content-system"
            ;;
        4)
            read -p "インストールパスを入力: " custom_path
            INSTALL_DIR="$custom_path/video-content-system"
            ;;
        *)
            echo "無効な選択です。デスクトップにインストールします。"
            INSTALL_DIR="$HOME/Desktop/video-content-system"
            ;;
    esac
    
    echo "📍 インストール先: $INSTALL_DIR"
}

# メインインストール処理
install_videoai_studio() {
    # 既存のディレクトリチェック
    if [ -d "$INSTALL_DIR" ]; then
        echo "⚠️  既存のインストールが見つかりました: $INSTALL_DIR"
        read -p "上書きしますか？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🗑️  既存のディレクトリを削除中..."
            rm -rf "$INSTALL_DIR"
        else
            echo "インストールを中止しました。"
            exit 0
        fi
    fi
    
    # リポジトリをクローン
    echo ""
    echo "📥 VideoAI Studioをダウンロード中..."
    git clone https://github.com/Shiki0138/video-content-system.git "$INSTALL_DIR"
    
    if [ $? -ne 0 ]; then
        echo "❌ ダウンロードに失敗しました"
        exit 1
    fi
    
    # ディレクトリに移動
    cd "$INSTALL_DIR"
    
    # 仮想環境のセットアップ
    echo ""
    echo "🔧 環境をセットアップ中..."
    python3 -m venv venv
    
    # 仮想環境をアクティベート
    source venv/bin/activate
    
    # 依存関係のインストール
    echo "📦 必要なパッケージをインストール中..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # ショートカットの作成
    create_shortcuts
    
    echo ""
    echo "✅ インストール完了！"
    echo ""
    echo "🚀 起動方法:"
    echo "   cd $INSTALL_DIR"
    echo "   ./quick_start.sh"
    echo ""
    echo "または、デスクトップの VideoAI Studio アイコンをダブルクリック"
}

# ショートカット作成
create_shortcuts() {
    # デスクトップショートカット（Mac）
    if [[ "$OS" == "Mac" ]] && [[ "$INSTALL_DIR" != "$HOME/Desktop/video-content-system" ]]; then
        echo "🔗 デスクトップにショートカットを作成中..."
        ln -sf "$INSTALL_DIR/quick_start.sh" "$HOME/Desktop/VideoAI Studio"
        chmod +x "$HOME/Desktop/VideoAI Studio"
    fi
    
    # 実行権限を付与
    chmod +x "$INSTALL_DIR/quick_start.sh"
}

# メイン処理
main() {
    echo ""
    check_requirements
    select_install_dir
    install_videoai_studio
    
    # 起動するか確認
    echo ""
    read -p "今すぐVideoAI Studioを起動しますか？ (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "🚀 VideoAI Studioを起動中..."
        cd "$INSTALL_DIR"
        ./quick_start.sh
    fi
}

# 実行
main