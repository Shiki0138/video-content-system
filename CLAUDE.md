# Claude向けプロジェクト仕様書

このドキュメントは、Claudeが本プロジェクトを理解し、適切にサポートするための重要な情報を含んでいます。

## プロジェクト概要

### 目的
動画ファイルから自動的に以下のコンテンツを生成するシステム：
- 高品質なブログ記事（HTML形式）
- YouTube説明文
- X（Twitter）投稿文
- 画像生成プロンプト（DALL-E 3/ChatGPT用）

### 技術スタック
- Python 3.13
- OpenAI Whisper（音声認識）
- Jekyll（静的サイトジェネレーター）
- Pillow（画像処理）

## 重要な処理ルール

### 1. ブログ生成の鉄則
**絶対に文字起こしテキストをそのまま使用しない**

正しい処理フロー：
1. Whisperで文字起こし
2. 発言の意図・目的・ターゲットを分析
3. 読者にとって価値のある内容にリライト
4. HTML形式で出力

### 2. 必須の品質基準
- プロフェッショナルな日本語文章
- 論理的な記事構成
- SEO最適化
- 読者価値の提供

### 3. 出力形式
**必ずHTML形式で出力する**（マークダウンは使用禁止）

```html
<h2 id="section-id">見出し</h2>
<p>段落テキスト</p>
<ul>
  <li>リスト項目</li>
</ul>
```

## ファイル構成

```
video-content-system/
├── main.py                    # メインエントリーポイント
├── config.yaml               # 設定ファイル（重要）
├── modules/
│   ├── blog_optimizer.py     # ブログ最適化の中核モジュール
│   ├── content_generator.py  # コンテンツ生成制御
│   ├── jekyll_writer.py      # Jekyll/HTML記事生成
│   ├── transcriber.py        # Whisper音声認識
│   └── image_prompt_generator.py # 画像プロンプト生成
├── BLOG_GENERATION_RULES.md  # ブログ生成ルール（必読）
└── BLOG_OPTIMIZATION_PHILOSOPHY.md # 最適化の哲学
```

## 重要な設定（config.yaml）

```yaml
content:
  blog:
    optimize_content: true     # 必須：BlogOptimizerを使用
    target_quality: high       # 高品質なコンテンツ生成
    output_format: html        # HTML形式で出力
    natural_japanese: true     # 自然な日本語に変換
```

## よくある音声認識エラーと修正

| 誤認識 | 正しい表記 |
|--------|-----------|
| ケーシャル | カジュアル |
| テイア | アイデア |
| シジュー | 実装 |
| 先生AI | 生成AI |
| 会いた | 空いた |

## コマンド例

```bash
# 動画処理
python main.py video.mp4 --title "タイトル"

# 開発サーバー起動
cd output/jekyll_site && bundle exec jekyll serve
```

## トラブルシューティング

### 日本語が不自然な場合
1. `modules/blog_optimizer.py`の`_convert_to_written_style`メソッドを確認
2. 変換ルールを追加・修正

### HTML出力されない場合
1. `config.yaml`の`output_format: html`を確認
2. `modules/jekyll_writer.py`の`_generate_post_content`メソッドを確認

## 開発時の注意事項

1. **BlogOptimizerモジュールが最重要** - ここで品質が決まる
2. **テストは実際の動画で** - テストデータでは不十分
3. **ユーザーフィードバックを即反映** - 品質向上の鍵

## 参考ドキュメント

- `BLOG_GENERATION_RULES.md` - 詳細なルール仕様
- `BLOG_OPTIMIZATION_PHILOSOPHY.md` - 設計思想
- `README.md` - 基本的な使い方

---

**Claudeへ：このシステムの目的は「クリエイターの時間を解放すること」です。**
**品質を犠牲にすることなく、作業を自動化することが最重要です。**