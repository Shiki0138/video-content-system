# 🚀 クイックスタートガイド

## 最もシンプルな起動方法

### 1️⃣ ワンコマンドで起動

```bash
./quick_start.sh
```

これだけです！🎉

初回実行時は自動的に：
- ✅ 仮想環境を作成
- ✅ 必要なパッケージをインストール
- ✅ Webアプリを起動

### 2️⃣ ブラウザでアクセス

http://localhost:8003

### 3️⃣ 動画をアップロードして処理開始！

---

## トラブルシューティング

### もし `permission denied` エラーが出た場合：

```bash
chmod +x quick_start.sh
./quick_start.sh
```

### もし `ffmpeg` がない場合：

```bash
brew install ffmpeg
```

---

## 従来の方法（手動）

```bash
# 1. 仮想環境を作成
python3 -m venv venv

# 2. アクティベート
source venv/bin/activate

# 3. パッケージインストール
pip install -r requirements.txt

# 4. 起動
python web_app.py
```

でも、`./quick_start.sh` の方が簡単です！ 😊