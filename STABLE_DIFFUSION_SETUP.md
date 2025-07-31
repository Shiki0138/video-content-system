# 🎨 Stable Diffusion サムネイル生成セットアップガイド

このガイドでは、YouTubeサムネイルを無料で高品質に生成するためのStable Diffusion設定方法を説明します。

## 📋 セットアップオプション

### オプション1: Replicate（最も簡単・従量課金）

**メリット**: セットアップ簡単、GPU不要、高速
**料金**: 約$0.002/画像（1000枚で$2程度）

1. **アカウント作成**
   - https://replicate.com にアクセス
   - GitHubアカウントでサインイン

2. **APIトークン取得**
   - ダッシュボード → API tokens
   - 新しいトークンを作成

3. **環境変数設定**
   ```bash
   export REPLICATE_API_TOKEN="r8_xxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

4. **config.yaml設定**
   ```yaml
   thumbnail:
     use_stable_diffusion: true
     sd_provider: replicate
   ```

### オプション2: Hugging Face（無料枠あり）

**メリット**: 無料枠あり、多様なモデル
**制限**: レート制限あり

1. **アカウント作成**
   - https://huggingface.co/join

2. **APIトークン取得**
   - Settings → Access Tokens
   - New token → Read権限

3. **環境変数設定**
   ```bash
   export HUGGINGFACE_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

4. **config.yaml設定**
   ```yaml
   thumbnail:
     use_stable_diffusion: true
     sd_provider: huggingface
   ```

### オプション3: ローカル実行（完全無料・要GPU）

**メリット**: 完全無料、制限なし、カスタマイズ自由
**要件**: NVIDIA GPU（VRAM 6GB以上推奨）

1. **Stable Diffusion WebUIインストール**
   ```bash
   # macOS/Linux
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
   cd stable-diffusion-webui
   ./webui.sh --api
   
   # Windows
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
   cd stable-diffusion-webui
   webui-user.bat
   ```

2. **起動オプション追加**
   `webui-user.sh` または `webui-user.bat` を編集:
   ```bash
   export COMMANDLINE_ARGS="--api --listen"
   ```

3. **config.yaml設定**
   ```yaml
   thumbnail:
     use_stable_diffusion: true
     sd_provider: local
   ```

## 🚀 使い方

### 1. 環境チェック

```python
from modules.stable_diffusion_thumbnail import StableDiffusionSetup

# 環境状態確認
env_check = StableDiffusionSetup.check_environment()
print(env_check)
```

### 2. テスト実行

```bash
python test_sd_thumbnail.py
```

### 3. Web UIで使用

```bash
python web_app.py
```
ブラウザで http://localhost:8003 を開く

## 🎯 推奨モデル（ローカル実行時）

YouTubeサムネイル向けの推奨モデル：

1. **SDXL Base**
   - 高品質、汎用性高い
   - https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

2. **DreamShaper XL**
   - リアルな人物表現
   - https://civitai.com/models/112902

3. **Juggernaut XL**
   - 写実的な表現
   - https://civitai.com/models/133005

## 📊 コスト比較

| プロバイダー | 月1000枚生成 | 速度 | 品質 |
|------------|-------------|------|------|
| Replicate | 約$2 | 高速（10秒） | 高 |
| Hugging Face | 無料〜$10 | 中速（20秒） | 高 |
| ローカル | $0（電気代のみ） | GPU依存 | 最高 |

## 🔧 トラブルシューティング

### APIキーエラー
```bash
# 環境変数確認
echo $REPLICATE_API_TOKEN
echo $HUGGINGFACE_API_TOKEN
```

### ローカル接続エラー
```bash
# WebUI起動確認
curl http://localhost:7860/
```

### GPU不足エラー
- `--lowvram` オプションを追加
- より小さいモデル（SD 1.5）を使用

## 💡 プロンプトのコツ

### 良いプロンプトの例
```
YouTube thumbnail design, professional photography, dramatic lighting, 
high contrast, vibrant colors, eye-catching composition, 4k quality
```

### 避けるべき要素（ネガティブプロンプト）
```
text, words, letters, watermark, blurry, low quality, distorted
```

## 📝 フォールバック設定

Stable Diffusionが利用できない場合、自動的にPillowベースの生成に切り替わります：

```yaml
thumbnail:
  use_stable_diffusion: false  # 手動で無効化する場合
```

---

質問や問題がある場合は、Issueを作成してください。