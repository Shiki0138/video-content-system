#!/usr/bin/env python3
"""
Video Content System 仮想環境セットアップスクリプト
macOSの新しいバージョンに対応
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """バナー表示"""
    print("""
╔══════════════════════════════════════════════╗
║       Video Content System Setup             ║
║    動画→ブログ自動化システムセットアップ     ║
╚══════════════════════════════════════════════╝
    """)


def create_venv():
    """仮想環境を作成"""
    print("🔧 仮想環境を作成中...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ 仮想環境は既に存在します")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ 仮想環境を作成しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 仮想環境の作成に失敗しました: {e}")
        return False


def get_venv_python():
    """仮想環境のPythonパスを取得"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")


def get_activation_command():
    """仮想環境のアクティベーションコマンドを取得"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_in_venv():
    """仮想環境内に依存関係をインストール"""
    print("\n📦 仮想環境内に依存関係をインストール中...")
    
    venv_python = get_venv_python()
    
    # pipをアップグレード
    print("  📦 pipをアップグレード...")
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # requirements.txtからインストール
    if Path("requirements.txt").exists():
        print("  📦 requirements.txtから依存関係をインストール...")
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依存関係のインストール完了")
    else:
        print("❌ requirements.txtが見つかりません")
        return False
    
    return True


def check_ffmpeg():
    """ffmpegインストールチェック"""
    print("\n📋 ffmpegチェック...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ ffmpeg インストール済み: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ffmpegが見つかりません")
    print("\nインストール方法:")
    
    system = platform.system()
    if system == "Darwin":  # macOS
        print("  brew install ffmpeg")
    elif system == "Linux":
        print("  sudo apt update && sudo apt install ffmpeg")
    elif system == "Windows":
        print("  1. https://ffmpeg.org/download.html からダウンロード")
        print("  2. PATHに追加")
    
    return False


def create_directories():
    """必要なディレクトリ作成"""
    print("\n📁 ディレクトリ作成...")
    
    directories = [
        'output',
        'logs',
        'templates',
        '_posts',
        'cache',
        'uploads',
        'temp_sessions',
        'web_static',
        'web_templates',
        'fonts'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    print("✅ ディレクトリ作成完了")


def create_activation_script():
    """アクティベーションスクリプトを作成"""
    print("\n📝 起動スクリプトを作成中...")
    
    if platform.system() == "Windows":
        # Windows用バッチファイル
        script_content = """@echo off
call venv\\Scripts\\activate
python web_app.py
"""
        script_path = Path("start.bat")
        script_path.write_text(script_content)
        print("✅ start.bat を作成しました")
    else:
        # Unix系用シェルスクリプト
        script_content = """#!/bin/bash
source venv/bin/activate
python3 web_app.py
"""
        script_path = Path("start.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # 実行権限を付与
        print("✅ start.sh を作成しました")


def print_next_steps():
    """次のステップを表示"""
    print("\n" + "="*50)
    print("✨ セットアップ完了！")
    print("="*50)
    
    activation_cmd = get_activation_command()
    
    print("\n🚀 VideoAI Studioの起動方法:")
    print("\n【方法1】簡単起動スクリプト（推奨）:")
    if platform.system() == "Windows":
        print("  start.bat をダブルクリック")
    else:
        print("  ./start.sh")
    
    print("\n【方法2】手動起動:")
    print(f"  1. 仮想環境をアクティベート: {activation_cmd}")
    print("  2. Webアプリを起動: python web_app.py")
    print("  3. ブラウザで http://localhost:8003 を開く")
    
    print("\n📋 コマンドライン使用例:")
    print(f"  {activation_cmd}")
    print("  python main.py video.mp4 --title '動画タイトル'")
    
    print("\n💡 ヒント:")
    print("  - 初回実行時はWhisperモデルのダウンロードに時間がかかります")
    print("  - メモリ不足の場合は小さいモデル（tiny/base）を使用してください")
    print("  - 仮想環境を終了するには 'deactivate' と入力")


def main():
    """メインセットアップ処理"""
    print_banner()
    
    # 仮想環境を作成
    if not create_venv():
        return 1
    
    # ffmpegチェック
    if not check_ffmpeg():
        print("\n⚠️  ffmpegがインストールされていません")
        print("動画処理機能を使用するにはffmpegが必要です")
        response = input("\n続行しますか？ (y/N): ")
        if response.lower() != 'y':
            return 1
    
    # 仮想環境内にインストール
    if not install_in_venv():
        return 1
    
    # ディレクトリ作成
    create_directories()
    
    # 起動スクリプト作成
    create_activation_script()
    
    # 完了メッセージ
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())