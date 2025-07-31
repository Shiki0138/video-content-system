#!/usr/bin/env python3
"""
Video Content System セットアップスクリプト
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


def check_python_version():
    """Pythonバージョンチェック"""
    print("📋 Pythonバージョンチェック...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8以上が必要です")
        print(f"   現在のバージョン: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
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


def install_dependencies():
    """依存関係インストール"""
    print("\n📦 依存関係をインストール...")
    
    # pip アップグレード
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    
    # requirements.txt からインストール
    if Path('requirements.txt').exists():
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ 依存関係インストール完了")
    else:
        print("❌ requirements.txt が見つかりません")
        return False
    
    return True


def test_whisper():
    """Whisperの動作テスト"""
    print("\n🎤 Whisperテスト...")
    try:
        import whisper
        print("  モデルをロード中（初回は時間がかかります）...")
        model = whisper.load_model("tiny")
        print("✅ Whisper動作確認OK")
        return True
    except Exception as e:
        print(f"❌ Whisperエラー: {e}")
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
        'uploads'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    print("✅ ディレクトリ作成完了")


def create_sample_config():
    """サンプル設定ファイル作成"""
    print("\n⚙️ サンプル設定ファイル作成...")
    
    # .env.example
    env_example = """# Video Content System 環境変数

# Whisper設定
WHISPER_MODEL=base

# 出力設定
OUTPUT_DIR=./output
JEKYLL_POSTS_DIR=./_posts

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=./logs/video-content.log
"""
    
    Path('.env.example').write_text(env_example)
    print("  ✓ .env.example")
    
    # テンプレートファイル
    template_dir = Path('templates')
    
    # ブログ記事テンプレート
    blog_template = """# {{ title }}

{{ summary }}

## 目次
{% for section in sections %}
- {{ section.title }}
{% endfor %}

---

{% for section in sections %}
## {{ section.title }}

{{ section.content }}

{% endfor %}

---

この記事は動画の内容を文字起こし・編集したものです。

- 文字数: {{ word_count }}文字
- 作成日: {{ date }}
"""
    
    (template_dir / 'blog_post.j2').write_text(blog_template)
    print("  ✓ templates/blog_post.j2")
    
    print("✅ サンプルファイル作成完了")


def print_next_steps():
    """次のステップを表示"""
    print("\n" + "="*50)
    print("✨ セットアップ完了！")
    print("="*50)
    
    print("\n📋 使い方:")
    print("  1. 単一動画を処理:")
    print("     python main.py video.mp4 --title '動画タイトル'")
    print()
    print("  2. 複数動画を一括処理:")
    print("     python main.py ./videos/ --batch")
    print()
    print("  3. Whisperモデルを指定:")
    print("     python main.py video.mp4 --model small")
    print()
    print("📚 Whisperモデル一覧:")
    print("  - tiny   : 最速、精度低")
    print("  - base   : バランス型（推奨）")
    print("  - small  : 高精度")
    print("  - medium : より高精度")
    print("  - large  : 最高精度")
    print()
    print("💡 ヒント:")
    print("  - 初回実行時はモデルのダウンロードに時間がかかります")
    print("  - メモリ不足の場合は小さいモデルを使用してください")
    print("  - Jekyll記事は _posts/ に生成されます")


def main():
    """メインセットアップ処理"""
    print_banner()
    
    # チェック項目
    checks = [
        ("Python バージョン", check_python_version),
        ("ffmpeg", check_ffmpeg),
    ]
    
    all_ok = True
    for name, check_func in checks:
        if not check_func():
            all_ok = False
    
    if not all_ok:
        print("\n❌ 必要な要件が満たされていません")
        print("上記の問題を解決してから再度実行してください")
        return 1
    
    # インストール処理
    try:
        if not install_dependencies():
            return 1
        
        if not test_whisper():
            print("\n⚠️ Whisperのテストに失敗しましたが、セットアップを続行します")
        
        create_directories()
        create_sample_config()
        
        print_next_steps()
        return 0
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())