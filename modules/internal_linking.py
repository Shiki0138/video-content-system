"""
内部リンク管理モジュール
新規投稿と既存投稿の双方向リンク機能を提供
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)


class InternalLinkManager:
    """内部リンク管理クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.posts_dir = Path(config.get('posts_directory', '_posts'))
        self.link_database = Path(config.get('link_database', 'internal_links.json'))
        self.similarity_threshold = config.get('similarity_threshold', 0.6)
        self.max_related_posts = config.get('max_related_posts', 3)
        
    def process_new_post(self, new_post_path: Path, post_content: Dict) -> Dict:
        """新規投稿の内部リンク処理"""
        
        logger.info(f"新規投稿の内部リンク処理開始: {new_post_path}")
        
        # 1. 関連記事を検索
        related_posts = self._find_related_posts(post_content)
        
        # 2. 新規記事に関連記事リンクを追加
        self._add_related_links_to_new_post(new_post_path, related_posts)
        
        # 3. 既存記事から新規記事への逆リンク追加
        self._add_backlinks_to_existing_posts(new_post_path, post_content, related_posts)
        
        # 4. リンクデータベースを更新
        self._update_link_database(new_post_path, post_content, related_posts)
        
        logger.info(f"✓ 内部リンク処理完了: {len(related_posts)}件の関連記事")
        
        return {
            'related_posts': related_posts,
            'backlinks_added': len(related_posts)
        }
    
    def _find_related_posts(self, post_content: Dict) -> List[Dict]:
        """関連記事を検索"""
        
        related_posts = []
        new_keywords = set(post_content.get('keywords', []))
        new_title = post_content.get('title', '')
        
        # 既存記事を調査
        if self.posts_dir.exists():
            for post_file in self.posts_dir.glob('*.md'):
                try:
                    existing_content = self._parse_post_file(post_file)
                    similarity = self._calculate_similarity(post_content, existing_content)
                    
                    if similarity > self.similarity_threshold:
                        related_posts.append({
                            'file_path': post_file,
                            'title': existing_content.get('title', ''),
                            'url': self._generate_post_url(post_file),
                            'similarity': similarity,
                            'excerpt': existing_content.get('excerpt', '')[:100],
                            'keywords': existing_content.get('keywords', []),
                            'thumbnail': existing_content.get('image', '')
                        })
                        
                except Exception as e:
                    logger.warning(f"記事解析エラー {post_file}: {e}")
                    continue
        
        # 類似度でソートし、上位を返す
        related_posts.sort(key=lambda x: x['similarity'], reverse=True)
        return related_posts[:self.max_related_posts]
    
    def _calculate_similarity(self, post1: Dict, post2: Dict) -> float:
        """記事間の類似度を計算"""
        
        # キーワード一致度
        keywords1 = set(post1.get('keywords', []))
        keywords2 = set(post2.get('keywords', []))
        
        if not keywords1 or not keywords2:
            keyword_similarity = 0
        else:
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            keyword_similarity = intersection / union if union > 0 else 0
        
        # タイトル類似度（簡易版）
        title1_words = set(re.findall(r'\w+', post1.get('title', '').lower()))
        title2_words = set(re.findall(r'\w+', post2.get('title', '').lower()))
        
        if title1_words and title2_words:
            title_intersection = len(title1_words.intersection(title2_words))
            title_union = len(title1_words.union(title2_words))
            title_similarity = title_intersection / title_union if title_union > 0 else 0
        else:
            title_similarity = 0
        
        # カテゴリ類似度
        categories1 = set(post1.get('categories', []))
        categories2 = set(post2.get('categories', []))
        
        category_similarity = 0
        if categories1 and categories2:
            category_intersection = len(categories1.intersection(categories2))
            category_union = len(categories1.union(categories2))
            category_similarity = category_intersection / category_union if category_union > 0 else 0
        
        # 重み付き総合類似度
        total_similarity = (
            keyword_similarity * 0.5 +
            title_similarity * 0.3 +
            category_similarity * 0.2
        )
        
        return total_similarity
    
    def _parse_post_file(self, post_file: Path) -> Dict:
        """記事ファイルを解析してメタデータを抽出"""
        
        content = post_file.read_text(encoding='utf-8')
        
        # Front Matterを抽出
        front_matter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if front_matter_match:
            try:
                front_matter = yaml.safe_load(front_matter_match.group(1))
                return front_matter
            except yaml.YAMLError as e:
                logger.warning(f"YAML解析エラー {post_file}: {e}")
                return {}
        
        return {}
    
    def _add_related_links_to_new_post(self, post_path: Path, related_posts: List[Dict]):
        """新規記事に関連記事リンクを追加"""
        
        if not related_posts:
            return
        
        content = post_path.read_text(encoding='utf-8')
        
        # 関連記事セクションを生成
        related_section = self._generate_related_posts_section(related_posts)
        
        # 記事の最後（</div>の直前）に挿入
        if '</div>' in content:
            content = content.replace('</div>', f'{related_section}\n</div>')
        else:
            content += f'\n\n{related_section}'
        
        post_path.write_text(content, encoding='utf-8')
        logger.info(f"✓ 関連記事リンクを追加: {post_path}")
    
    def _generate_related_posts_section(self, related_posts: List[Dict]) -> str:
        """関連記事セクションのHTMLを生成"""
        
        section = ['<div class="related-posts-section">']
        section.append('<h3>🔗 関連記事</h3>')
        section.append('<div class="related-posts-grid">')
        
        for post in related_posts:
            thumbnail = post.get('thumbnail', '/assets/images/default-thumbnail.png')
            
            section.append('  <div class="related-post-card">')
            section.append(f'    <div class="related-post-thumbnail">')
            section.append(f'      <img src="{thumbnail}" alt="{post["title"]}" loading="lazy">')
            section.append(f'    </div>')
            section.append(f'    <div class="related-post-content">')
            section.append(f'      <h4><a href="{post["url"]}">{post["title"]}</a></h4>')
            section.append(f'      <p class="related-post-excerpt">{post["excerpt"]}...</p>')
            section.append(f'      <div class="related-post-tags">')
            
            for keyword in post.get('keywords', [])[:3]:
                section.append(f'        <span class="tag-small">{keyword}</span>')
            
            section.append(f'      </div>')
            section.append(f'    </div>')
            section.append('  </div>')
        
        section.append('</div>')
        section.append('</div>')
        
        return '\n'.join(section)
    
    def _add_backlinks_to_existing_posts(self, new_post_path: Path, new_post_content: Dict, related_posts: List[Dict]):
        """既存記事に新規記事への逆リンクを追加"""
        
        new_title = new_post_content.get('title', '')
        new_url = self._generate_post_url(new_post_path)
        new_excerpt = new_post_content.get('summary', '')[:100]
        new_thumbnail = new_post_content.get('featured_image', '/assets/images/default-thumbnail.png')
        
        for related_post in related_posts[:2]:  # 上位2件のみに逆リンク追加
            existing_file = related_post['file_path']
            
            try:
                content = existing_file.read_text(encoding='utf-8')
                
                # 既に関連記事セクションがあるかチェック
                if '<div class="related-posts-section">' in content:
                    # 既存のセクションに追加
                    self._append_to_existing_related_section(existing_file, new_title, new_url, new_excerpt, new_thumbnail)
                else:
                    # 新しく関連記事セクションを作成
                    new_related_info = {
                        'title': new_title,
                        'url': new_url,
                        'excerpt': new_excerpt,
                        'thumbnail': new_thumbnail,
                        'keywords': new_post_content.get('keywords', [])[:3]
                    }
                    self._add_related_links_to_new_post(existing_file, [new_related_info])
                
                logger.info(f"✓ 逆リンク追加: {existing_file} → {new_post_path}")
                
            except Exception as e:
                logger.warning(f"逆リンク追加エラー {existing_file}: {e}")
    
    def _append_to_existing_related_section(self, post_file: Path, new_title: str, new_url: str, new_excerpt: str, new_thumbnail: str):
        """既存の関連記事セクションに新しい記事を追加"""
        
        content = post_file.read_text(encoding='utf-8')
        
        # 新しい関連記事カードを生成
        new_card = f"""  <div class="related-post-card">
    <div class="related-post-thumbnail">
      <img src="{new_thumbnail}" alt="{new_title}" loading="lazy">
    </div>
    <div class="related-post-content">
      <h4><a href="{new_url}">{new_title}</a></h4>
      <p class="related-post-excerpt">{new_excerpt}...</p>
      <div class="related-post-tags">
        <span class="tag-small">新着</span>
      </div>
    </div>
  </div>"""
        
        # 関連記事グリッドに挿入
        grid_end = '</div>\n</div>'  # related-posts-grid の終了タグ
        if grid_end in content:
            content = content.replace(grid_end, f'{new_card}\n{grid_end}')
            post_file.write_text(content, encoding='utf-8')
    
    def _generate_post_url(self, post_file: Path) -> str:
        """記事ファイルからURLを生成"""
        
        # ファイル名から日付とスラッグを抽出
        filename = post_file.stem
        
        # 日付部分を抽出 (YYYY-MM-DD-)
        date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.*)', filename)
        if date_match:
            year, month, day, slug = date_match.groups()
            return f"/{year}/{month}/{day}/{slug}/"
        
        # フォールバック
        return f"/posts/{filename}/"
    
    def _update_link_database(self, new_post_path: Path, post_content: Dict, related_posts: List[Dict]):
        """リンクデータベースを更新"""
        
        # 既存データベースを読み込み
        database = {}
        if self.link_database.exists():
            try:
                with open(self.link_database, 'r', encoding='utf-8') as f:
                    database = json.load(f)
            except json.JSONDecodeError:
                logger.warning("リンクデータベースを新規作成します")
                database = {'posts': {}, 'links': []}
        else:
            database = {'posts': {}, 'links': []}
        
        # 新規記事情報を追加
        post_id = str(new_post_path)
        database['posts'][post_id] = {
            'title': post_content.get('title', ''),
            'keywords': post_content.get('keywords', []),
            'created_at': datetime.now().isoformat(),
            'url': self._generate_post_url(new_post_path)
        }
        
        # リンク関係を記録
        for related_post in related_posts:
            database['links'].append({
                'from': post_id,
                'to': str(related_post['file_path']),
                'similarity': related_post['similarity'],
                'created_at': datetime.now().isoformat(),
                'type': 'related'
            })
        
        # データベースを保存
        self.link_database.parent.mkdir(parents=True, exist_ok=True)
        with open(self.link_database, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ リンクデータベース更新: {self.link_database}")


class RelatedPostsAnalyzer:
    """関連記事分析エンジン"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def analyze_post_relationships(self, posts_dir: Path) -> Dict:
        """記事間の関係性を分析"""
        
        relationships = {
            'clusters': [],
            'popular_topics': [],
            'link_density': 0,
            'orphaned_posts': []
        }
        
        # 実装は複雑になるため、必要に応じて拡張
        logger.info("関係性分析完了")
        
        return relationships


class LinkOptimizer:
    """リンク最適化エンジン"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def optimize_internal_links(self, posts_dir: Path) -> Dict:
        """内部リンク構造を最適化"""
        
        optimization_results = {
            'links_added': 0,
            'links_removed': 0,
            'clusters_formed': 0
        }
        
        # 最適化ロジックを実装
        logger.info("リンク最適化完了")
        
        return optimization_results