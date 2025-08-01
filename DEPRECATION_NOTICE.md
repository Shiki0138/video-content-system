# 🚨 廃止通知 - Stable Diffusion機能の削除

## 概要

VideoAI Studioは、画像の自動生成から**画像プロンプト生成**方式に移行しました。これに伴い、以下のStable Diffusion関連の機能は廃止されました。

## 廃止された機能

### 1. ファイル
- `STABLE_DIFFUSION_SETUP.md` - 廃止通知を追加済み
- `STABLE_DIFFUSION_API_SETUP.md` - 廃止通知を追加済み
- `modules/stable_diffusion_thumbnail.py` - 廃止通知を追加済み、使用非推奨

### 2. Web APIエンドポイント
- `/api/settings/stable-diffusion` - 廃止エラーを返すように変更
- 関連する設定管理機能 - 廃止通知を追加

### 3. 設定ページ
- `/settings` (settings.html) - 廃止通知を表示

## 新しいワークフロー

### 従来の方式
```
動画アップロード → 文字起こし → コンテンツ生成 → 画像自動生成 → 完了
```

### 新しい方式
```
動画アップロード → 文字起こし → コンテンツ生成 → 画像プロンプト生成 → 手動画像アップロード → 完了
```

## 移行ガイド

### 1. 画像プロンプト生成の使用
```python
from modules.image_prompt_generator import ImagePromptGenerator

# プロンプト生成
generator = ImagePromptGenerator(config)
prompts = generator.generate_all_prompts(
    title=title,
    transcript_data=transcript_data,
    blog_content=blog_content
)
```

### 2. 生成されたプロンプトの活用
- DALL-E 3（推奨）
- ChatGPT Plus
- その他の画像生成サービス

### 3. 手動画像アップロード
Web UIの画像アップロード機能を使用して、生成した画像をシステムに追加

## メリット

- ✅ **コスト削減**: 必要な画像のみ生成
- ✅ **品質向上**: 手動での品質確認が可能
- ✅ **柔軟性**: 任意の画像生成サービスを使用可能
- ✅ **簡素化**: API設定の複雑さを排除

## 関連ドキュメント

- [IMAGE_PROMPT_GENERATION.md](IMAGE_PROMPT_GENERATION.md) - 新しい画像プロンプト生成機能の詳細
- [README.md](README.md) - システム全体の概要

## 更新日

2025年8月1日