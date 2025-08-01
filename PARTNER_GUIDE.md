# 🎬 VideoAI Studio パートナー向けガイド

## 📌 はじめに

VideoAI Studioをお試しいただき、ありがとうございます！
このツールは、動画から自動的にブログ記事、YouTube説明文、SNS投稿を生成する革新的なシステムです。

### できること
- 🎤 動画の音声を自動文字起こし
- 📝 SEO最適化されたブログ記事の自動生成
- 🎨 画像生成用プロンプトの作成
- 📱 X（Twitter）投稿文の生成
- 📺 YouTube説明文の作成

## 🚀 クイックスタート（5分で始められます）

### 1. 必要なソフトウェアのインストール

#### Mac の場合
```bash
# Homebrewがない場合は先にインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 必要なツールをインストール
brew install python3 git ffmpeg
```

#### Windows の場合
1. [Python 3.8以上](https://www.python.org/downloads/) をダウンロード・インストール
2. [Git](https://git-scm.com/download/win) をダウンロード・インストール  
3. [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) をダウンロード・PATH設定

### 2. VideoAI Studio のインストール

```bash
# デスクトップに移動
cd ~/Desktop    # Macの場合
cd Desktop      # Windowsの場合

# ダウンロード
git clone https://github.com/Shiki0138/video-content-system.git

# フォルダに移動
cd video-content-system

# 起動（初回は自動セットアップされます）
./quick_start.sh    # Macの場合
python quick_start.sh   # Windowsの場合
```

### 3. ブラウザでアクセス

自動的にWebアプリが起動します。
ブラウザで以下のURLを開いてください：

🌐 **http://localhost:8003**

## 📹 使い方（とても簡単です）

### Step 1: 動画をアップロード
- 「動画を選択」ボタンをクリック
- MP4、MOV、AVI などの動画ファイルを選択
- タイトルを入力（例：「AIツールの使い方解説」）

### Step 2: 処理を開始
- 「処理開始」ボタンをクリック
- 自動的に以下が生成されます：
  - 文字起こし
  - ブログ記事（HTML形式でコピペ可能）
  - SEOメタデータ（タイトル、説明、キーワード）
  - タグ・カテゴリ提案
  - YouTube説明文
  - X（Twitter）投稿文
  - 画像生成プロンプト

### Step 3: 結果を活用
- **ブログ記事**: HTMLをそのままWordPressやCMSに貼り付け
- **SEOメタ**: Yoast SEOなどのプラグインに入力
- **タグ・カテゴリ**: 推奨されたものを選択して設定
- 全ファイルは自動的に保存されます

## 💡 活用例

### YouTuber の方
1. 動画をアップロード後、自動生成されたコンテンツを取得
2. YouTube説明文をそのまま使用
3. ブログ記事を自分のサイトに投稿
4. X投稿で動画を宣伝

### 企業の方
1. セミナー動画から自動的に記事を作成
2. 社内wiki用のドキュメント生成
3. SNSマーケティング用コンテンツ作成

### 教育関係の方
1. 授業動画から教材を自動生成
2. 講義内容の文字起こし
3. 学習用ブログ記事の作成

## ⚡ パフォーマンス

- 10分の動画 → 約2-3分で処理完了
- 30分の動画 → 約5-8分で処理完了
- 60分の動画 → 約10-15分で処理完了

※ お使いのPCスペックにより変動します

## 🔧 トラブルシューティング

### Q: 「モジュールが見つかりません」エラー
A: 以下のコマンドを実行してください：
```bash
cd ~/Desktop/video-content-system
source venv/bin/activate  # Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Q: 処理が遅い
A: より小さいWhisperモデルを使用できます：
- 設定画面で「Whisperモデル」を「tiny」または「base」に変更

### Q: 文字起こしの精度が低い
A: より大きいWhisperモデルを使用してください：
- 設定画面で「Whisperモデル」を「small」または「medium」に変更

## 📊 フィードバックのお願い

お試しいただいた感想をぜひお聞かせください：

1. **使いやすさ**: 操作は簡単でしたか？
2. **処理速度**: 満足できる速度でしたか？
3. **出力品質**: 生成されたコンテンツの品質はいかがでしたか？
4. **改善要望**: どんな機能があれば便利ですか？
5. **価格感度**: 月額いくらなら利用したいですか？

フィードバックは以下までお願いします：
- メール: [あなたのメールアドレス]
- または直接お伝えください

## 🎁 特典

早期にお試しいただいたパートナー様には、正式版リリース時に：
- 永続割引（20% OFF）
- 新機能への優先アクセス
- 専用サポート

を提供予定です。

## 💬 サポート

ご不明な点がありましたら、お気軽にお問い合わせください。
- 技術的な質問
- 使い方のご相談
- 機能のリクエスト

すべて歓迎です！

---

**VideoAI Studio** - 動画コンテンツを最大限に活用する新しい方法

バージョン: 1.0.0（パートナーテスト版）