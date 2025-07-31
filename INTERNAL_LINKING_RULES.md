# 内部リンク自動化ルール

このドキュメントは、新規投稿と既存投稿の双方向内部リンク機能のルールと仕様を定めます。

## 基本仕様

### 1. 双方向リンク機能

**新規投稿時の処理フロー**
1. 新規記事の内容を解析
2. 既存記事から関連記事を検索
3. 新規記事に関連記事リンクを追加
4. 関連する既存記事に新規記事への逆リンクを追加
5. リンクデータベースを更新

### 2. 関連記事判定基準

**類似度計算方式**
- キーワード一致度（重み: 0.5）
- タイトル類似度（重み: 0.3）
- カテゴリ一致度（重み: 0.2）

**閾値設定**
```yaml
similarity_threshold: 0.6  # 60%以上の類似度で関連記事判定
max_related_posts: 3       # 最大3記事まで関連付け
```

### 3. リンク挿入位置

**新規記事への関連記事リンク**
- 記事の最後、article-footerの直前に挿入
- HTMLクラス: `related-posts-section`

**既存記事への逆リンク**
- 既存の関連記事セクションがある場合: そこに追加
- ない場合: 新しく関連記事セクションを作成
- 記事フッターの直前に配置

## HTML構造

### 関連記事セクション

```html
<div class="related-posts-section">
  <h3>🔗 関連記事</h3>
  <div class="related-posts-grid">
    <div class="related-post-card">
      <div class="related-post-thumbnail">
        <img src="/assets/images/thumbnail.png" alt="記事タイトル" loading="lazy">
      </div>
      <div class="related-post-content">
        <h4><a href="/2025/07/31/post-slug/">記事タイトル</a></h4>
        <p class="related-post-excerpt">記事の概要...</p>
        <div class="related-post-tags">
          <span class="tag-small">キーワード1</span>
          <span class="tag-small">キーワード2</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 新着記事の表示

逆リンクで追加される新規記事には特別なタグを付与：
```html
<div class="related-post-tags">
  <span class="tag-small">新着</span>
</div>
```

## データベース管理

### リンクデータベース構造

**ファイル**: `internal_links.json`

```json
{
  "posts": {
    "/path/to/post.md": {
      "title": "記事タイトル",
      "keywords": ["keyword1", "keyword2"],
      "created_at": "2025-07-31T15:30:00",
      "url": "/2025/07/31/post-slug/"
    }
  },
  "links": [
    {
      "from": "/path/to/new-post.md",
      "to": "/path/to/existing-post.md",
      "similarity": 0.75,
      "created_at": "2025-07-31T15:30:00",
      "type": "related"
    }
  ]
}
```

## 逆リンク処理ルール

### 1. 逆リンク対象の選定

- 関連度上位2記事のみに逆リンクを追加
- 過度なリンク追加を避けるための制限

### 2. 既存記事の更新方針

**既存の関連記事セクションがある場合**
- 新規記事カードを既存グリッドに追加
- 最大表示件数制限（3-4記事）を考慮

**関連記事セクションがない場合**
- 新しく関連記事セクションを作成
- 記事フッターの直前に配置

### 3. 更新の優先度

```yaml
enable_backlinks: true       # 逆リンク機能の有効化
update_existing_posts: true  # 既存記事更新の許可
```

## CSS スタイル要件

### 必要なCSSクラス

```css
.related-posts-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.related-posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.related-post-card {
  display: flex;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.related-post-thumbnail {
  width: 100px;
  height: 80px;
  flex-shrink: 0;
}

.related-post-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-post-content {
  padding: 0.75rem;
  flex: 1;
}

.related-post-content h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  line-height: 1.3;
}

.related-post-excerpt {
  font-size: 0.8rem;
  color: #666;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.related-post-tags {
  margin-top: 0.5rem;
}

.tag-small {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-size: 0.7rem;
  margin-right: 0.3rem;
}
```

## エラーハンドリング

### 1. ファイル読み書きエラー

```python
try:
    content = post_file.read_text(encoding='utf-8')
except Exception as e:
    logger.warning(f"記事読み込みエラー {post_file}: {e}")
    continue
```

### 2. YAML解析エラー

```python
try:
    front_matter = yaml.safe_load(front_matter_match.group(1))
except yaml.YAMLError as e:
    logger.warning(f"YAML解析エラー {post_file}: {e}")
    return {}
```

### 3. 逆リンク追加エラー

```python
try:
    self._append_to_existing_related_section(existing_file, ...)
    logger.info(f"✓ 逆リンク追加: {existing_file} → {new_post_path}")
except Exception as e:
    logger.warning(f"逆リンク追加エラー {existing_file}: {e}")
```

## 運用ルール

### 1. リンク品質管理

- 類似度0.6以上の記事のみリンク
- 関連性の低いリンクは自動で除外
- 手動での微調整も可能

### 2. パフォーマンス最適化

- リンクデータベースによる高速検索
- 記事数増加に対応した効率的なアルゴリズム
- 大量記事でも処理時間を短縮

### 3. メンテナンス

- 定期的なリンクデータベースの最適化
- 削除された記事のリンク清掃
- 関連度の再計算機能

## 今後の拡張予定

### 1. 高度な関連性分析

- コンテンツ内容の意味解析
- トピッククラスタリング
- 読者行動に基づく関連度調整

### 2. リンク効果測定

- クリック率の追跡
- 関連記事の効果分析
- リンク配置の最適化

### 3. 自動最適化

- A/Bテストによるリンク配置改善
- 機械学習による関連度予測
- 動的なリンク更新

---

**このルールに従って実装することで、SEO効果とユーザビリティを向上させる効果的な内部リンク構造を構築します。**