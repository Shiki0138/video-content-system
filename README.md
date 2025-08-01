# 🎬 VideoAI Studio

動画から自動的にブログ記事、YouTube説明文、SNS投稿を生成するAIシステム

📖 **パートナー向けガイド**: [PARTNER_GUIDE.md](PARTNER_GUIDE.md)をご覧ください

## ✨ 特徴

- **⏱️ 時間短縮**: 4-6時間の作業を13-18分に短縮（95%削減）
- **🤖 AI自動化**: 文字起こしからコンテンツ生成まで完全自動
- **📝 オールインワン**: ブログ、YouTube、SNSコンテンツを一括生成
- **🌐 日本語特化**: 日本語の文字起こし精度と自然な文章生成
- **🆓 無料で利用可能**: オープンソースで提供

## 📋 必要要件

- Python 3.8以上
- ffmpeg（動画処理用）
- 4GB以上のメモリ（推奨: 8GB）

**注意**: 
- macOSでは`python`コマンドの代わりに`python3`を使用してください
- macOS 12以降では仮想環境の使用が必須です

## 🚀 5分で始められるクイックスタート

### Mac/Linux の場合
```bash
# 以下を1行でコピー&ペースト（改行しないでください）
cd ~/Desktop && git clone https://github.com/Shiki0138/video-content-system.git && cd video-content-system && ./quick_start.sh
```

または、1つずつ実行：
```bash
cd ~/Desktop
git clone https://github.com/Shiki0138/video-content-system.git
cd video-content-system
./quick_start.sh
```

### Windows の場合
```cmd
cd Desktop
git clone https://github.com/Shiki0138/video-content-system.git
cd video-content-system
quick_start_windows.bat
```

→ ブラウザで **http://localhost:8003** を開くだけ！

### 1. インストール

```bash
# デスクトップに移動
cd ~/Desktop

# リポジトリをクローン
git clone https://github.com/Shiki0138/video-content-system.git

# プロジェクトディレクトリに移動
cd video-content-system

# セットアップ実行
# macOSの新しいバージョンの場合（推奨）
python3 setup_venv.py

# または従来の方法
python3 setup.py

# Windowsの場合
python setup_venv.py  # または python setup.py
```

### 2. 基本的な使い方

#### Web UIを使用（推奨）
```bash
# 仮想環境を使用した場合
./start.sh    # macOS/Linux
start.bat     # Windows

# または手動で起動
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
python3 web_app.py

# ブラウザで http://localhost:8003 にアクセス
```

#### コマンドライン使用
```bash
# 単一動画を処理
python3 main.py video.mp4 --title "AIツールの使い方"

# Whisperモデルを指定
python3 main.py video.mp4 --model small

# バッチ処理（フォルダ内の全動画）
python3 main.py ./videos/ --batch
```

### 3. 出力確認

```
output/
├── 20240131_123456_video/
│   ├── transcript.json        # 文字起こし全データ
│   ├── youtube_description.txt # YouTube説明文
│   ├── twitter_post.txt       # X投稿文
│   └── image_prompts.json     # 画像生成プロンプト
│
_posts/
└── 2024-01-31-ai-tools.md    # Jekyll記事
```

## 🎯 新ワークフロー

1. **動画アップロード**: 動画ファイルをシステムにアップロード
2. **キャプション作成**: Whisperを使用して高精度の文字起こし
3. **ブログ作成**: SEO最適化されたJekyll記事を自動生成
4. **画像プロンプト生成**: DALL-E 3/ChatGPT用の高品質プロンプトを作成
5. **手動画像アップロード**: 生成した画像をシステムにアップロード
6. **ツイート作成**: 最適化されたX投稿文を生成

### 🎨 画像プロンプト例

**YouTubeサムネイル用**:
```
Create a professional YouTube thumbnail with bold Japanese text "AIツールの使い方", 
bright orange/yellow gradient background, 3D mockup visualization, high contrast for mobile viewing
```

**ブログアイキャッチ用**:
```
Create a modern blog featured image with abstract tech visualization, professional gradient background, 
clean design suitable for blog header, no text needed
```

## 🎯 Whisperモデル選択ガイド

| モデル | サイズ | 必要メモリ | 速度 | 精度 | おすすめ用途 |
|--------|--------|------------|------|------|--------------|
| tiny   | 39MB   | ~1GB       | 最速 | 低   | テスト、下書き |
| **base** | 74MB   | ~1GB       | 速い | 中   | **日常使い** |
| small  | 244MB  | ~2GB       | 普通 | 高   | 品質重視 |
| medium | 769MB  | ~5GB       | 遅い | 高   | プロ用途 |
| large  | 1550MB | ~10GB      | 最遅 | 最高 | 最高品質 |

## 📁 プロジェクト構造

```
video-content-system/
├── main.py                    # メインスクリプト
├── config.yaml               # 設定ファイル
├── requirements.txt          # 依存関係
├── setup.py                  # セットアップスクリプト
│
├── modules/                  # コアモジュール
│   ├── transcriber.py       # Whisper文字起こし
│   ├── content_generator.py # コンテンツ生成
│   ├── image_prompt_generator.py # 画像プロンプト生成
│   ├── jekyll_writer.py     # Jekyll記事生成
│   └── utils.py            # ユーティリティ
│
├── templates/               # テンプレートファイル
├── output/                  # 出力ディレクトリ
└── _posts/                  # Jekyll記事出力先
```

## ⚙️ 設定カスタマイズ

`config.yaml`で詳細設定が可能：

```yaml
# Whisper設定
whisper:
  model: base              # モデル選択
  language: ja             # 言語指定

# コンテンツ生成設定
content:
  blog:
    min_section_length: 200    # セクション最小文字数
    max_section_length: 500    # セクション最大文字数
    
# 画像プロンプト設定
image_prompt:
  styles: ["professional", "tech", "business"]  # 生成するスタイル
  blog_sections: true                             # セクション画像プロンプトも生成
```

## 💡 使用例

### 例1: プレゼン動画をブログ化

```bash
python3 main.py presentation.mp4 --title "2024年のAIトレンド解説"
```

### 例2: チュートリアル動画をドキュメント化

```bash
python3 main.py tutorial.mp4 --title "Python入門講座 第1回"
```

### 例3: 複数動画を一括処理

```bash
# videosフォルダ内の全動画を処理
python3 main.py ./videos/ --batch
```

## 🔧 トラブルシューティング

### メモリ不足エラー

```bash
# より小さいモデルを使用
python3 main.py video.mp4 --model tiny
```

### ffmpegが見つからない

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロード
```

### 文字起こし精度が低い

```bash
# より大きいモデルを使用
python3 main.py video.mp4 --model medium
```

## 📊 処理時間の目安

| 動画長さ | tinyモデル | baseモデル | smallモデル |
|----------|------------|------------|-------------|
| 5分      | 30秒       | 1分        | 2分         |
| 10分     | 1分        | 2分        | 4分         |
| 30分     | 3分        | 6分        | 12分        |

## 🚀 高度な使い方

### カスタムテンプレート

`templates/`フォルダにJinja2テンプレートを配置して、出力をカスタマイズ可能。

### APIとの連携

生成されたコンテンツを自動的にブログやSNSに投稿する拡張も可能。

### Docker対応

```dockerfile
# 準備中
```

## 🤝 コントリビューション

Issue報告やPull Requestを歓迎します！

## 📝 ライセンス

MIT License

## 🙏 謝辞

- [OpenAI Whisper](https://github.com/openai/whisper) - 音声認識
- [Jekyll](https://jekyllrb.com/) - 静的サイトジェネレーター
- [Pillow](https://pillow.readthedocs.io/) - 画像処理