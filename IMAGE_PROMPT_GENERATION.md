# 🎨 画像プロンプト生成機能ガイド

VideoAI Studioの画像プロンプト生成機能を使用して、DALL-E 3やChatGPTで高品質な画像を作成するためのガイドです。

## 📋 概要

VideoAI Studioは、動画コンテンツから自動的に以下の画像プロンプトを生成します：

- **YouTubeサムネイル用プロンプト**（3種類のスタイル）
- **ブログアイキャッチ画像用プロンプト**
- **ブログセクション画像用プロンプト**（最大3枚）

## 🎯 生成されるプロンプトの種類

### 1. YouTubeサムネイル用プロンプト

#### プロフェッショナルスタイル
```
Create a professional YouTube thumbnail that looks like it was made by a top YouTuber's design team.

MAIN ELEMENTS:
- Bold Japanese text "AIツールの使い方" with 3D effect and glowing outline
- Subtitle showing the main benefit or topic in smaller text
- Visual workflow or concept illustration related to the content
- Color scheme: bright orange/yellow gradient background with electric blue accents
- Professional lighting effects and shadows

COMPOSITION:
- Left side: Large bold text taking 40% of space
- Right side: 3D mockup or visual representation of the concept
- High contrast for mobile viewing optimization
- Clean, modern design that screams "professional tutorial"

STYLE: High-end YouTube thumbnail, bright and engaging, professional quality
```

#### テック系スタイル
```
Design a tech influencer style YouTube thumbnail with maximum visual impact.

CORE DESIGN:
- Center: Glowing "最新AI技術" text with neon effect
- Background: Dark tech pattern with circuit board elements
- Futuristic UI elements showing the technology or process
- Holographic displays or floating screens
- Color palette: electric blue, neon green, white on dark background
- Digital particles and glowing effects

TECHNICAL SPECS:
- 16:9 ratio optimized for YouTube
- High contrast for mobile viewing
- Modern tech aesthetic with premium feel
- Japanese text clearly readable at thumbnail size

STYLE: Tech influencer, futuristic, high-tech, premium quality
```

#### ビジネス系スタイル
```
Create a business professional YouTube thumbnail with corporate appeal.

BUSINESS ELEMENTS:
- Top: "ビジネス効率化の秘訣" in bold corporate font
- Center: Clean infographic or process visualization
- Professional icons representing key concepts
- Background: Professional gradient from white to light blue
- Color scheme: corporate blue, white, subtle gold accents
- Clean lines and professional spacing

LAYOUT:
- Organized, grid-based composition
- Professional typography hierarchy
- Trustworthy and authoritative appearance
- Perfect for business/productivity audience

STYLE: Corporate professional, clean, trustworthy, business-grade quality
```

### 2. ブログアイキャッチ画像用プロンプト

```
Create a professional blog featured image with modern design aesthetics.

MAIN ELEMENTS:
- Topic: "AI技術の活用方法"
- Visual theme representing: technology, innovation, automation
- Abstract or conceptual visualization (no text needed)
- Professional gradient background with subtle patterns
- Color scheme: Modern tech colors (blues, purples, or corporate colors)
- High-quality, eye-catching composition

COMPOSITION:
- Center-focused main visual element
- Balanced negative space
- Professional lighting and shadows
- Suitable for blog header (16:9 or similar ratio)

STYLE: Modern, professional, tech-oriented, clean design suitable for blog featured image
```

### 3. ブログセクション画像用プロンプト

```
Create a simple, clean illustration for a blog section.

SECTION THEME: "課題の特定"
CONTENT CONTEXT: Illustrating the concept of identifying problems and challenges

REQUIREMENTS:
- Simple, minimalist illustration
- Flat design or light 3D style
- Clear visual metaphor for the section topic
- Soft, friendly color palette
- No text or words in the image
- Square format (1:1 ratio)

STYLE: Minimal, friendly, professional illustration suitable for blog content
```

## 🚀 使い方

### 1. Web UIでの使用

1. VideoAI Studio（http://localhost:8003）にアクセス
2. 動画をアップロードして処理を開始
3. 「画像プロンプト生成」ステップで自動的にプロンプトが作成されます
4. 生成されたプロンプトをコピーして、お好みの画像生成サービスで使用

### 2. プログラムでの使用

```python
from modules.image_prompt_generator import ImagePromptGenerator

# 初期化
generator = ImagePromptGenerator(config)

# YouTubeサムネイル用プロンプト生成
thumbnail_prompt = generator.generate_youtube_thumbnail_prompt(
    title="AIツールの使い方",
    transcript_data=transcript_data,
    style="professional"  # "professional", "tech", "business"から選択
)

# ブログ画像用プロンプト生成
blog_prompts = generator.generate_all_prompts(
    title=title,
    transcript_data=transcript_data,
    blog_content=blog_content
)
```

## 💡 プロンプトカスタマイズのコツ

### 1. 日本語テキストの調整
- タイトルが長い場合は、プロンプト内の日本語テキスト部分を短縮
- キャッチーなフレーズに変更して訴求力を向上

### 2. カラースキームの変更
- ターゲット層に合わせて色を調整
- ブランドカラーがある場合は指定

### 3. スタイルの微調整
- より具体的な指示を追加（例：「minimalist」「vintage」「modern」）
- 参考にしたいYouTuberやブランドのスタイルを指定

## 🎨 推奨画像生成サービス

### 1. DALL-E 3（OpenAI）
- **特徴**: 高品質、プロンプト理解力が高い
- **価格**: $0.04-0.17/枚
- **使い方**: ChatGPT PlusまたはAPI経由

### 2. ChatGPT（無料）
- **特徴**: ChatGPT Plusユーザーは追加料金なし
- **制限**: 1時間あたりの生成数に制限あり
- **使い方**: チャット内で直接プロンプトを使用

### 3. その他のサービス
- Midjourney（Discord経由）
- Stable Diffusion（ローカルまたはAPI）
- Leonardo AI
- Ideogram AI

## 📊 ベストプラクティス

### 1. A/Bテストの実施
- 複数のスタイルでサムネイルを生成
- YouTubeアナリティクスでCTRを比較
- 最も効果的なスタイルを特定

### 2. 一貫性の維持
- チャンネル全体で統一感のあるデザイン
- ブランドガイドラインに従う
- 視聴者が認識しやすいスタイルを確立

### 3. モバイル最適化
- 小さい画面でも読みやすいテキストサイズ
- 高コントラストで視認性を確保
- シンプルで分かりやすいデザイン

## 🔧 トラブルシューティング

### Q: プロンプトが長すぎてエラーになる
A: プロンプトの詳細部分を削除して、コア要素のみ残してください。

### Q: 生成された画像にテキストが含まれない
A: プロンプトに具体的なテキスト指示を追加してください。例：`with text "あなたのタイトル"`

### Q: 期待したスタイルと異なる
A: スタイルキーワードを追加または調整してください。例：`anime style`、`photorealistic`、`3D render`

## 📝 まとめ

VideoAI Studioの画像プロンプト生成機能により：

- ✅ **時間短縮**: プロンプト作成の手間を削減
- ✅ **品質向上**: 最適化されたプロンプトで高品質な画像を生成
- ✅ **柔軟性**: お好みの画像生成サービスを自由に選択
- ✅ **コスト最適化**: 必要な画像のみ生成してコストを削減

プロンプトを活用して、魅力的なビジュアルコンテンツを作成しましょう！