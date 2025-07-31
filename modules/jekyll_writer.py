"""
Jekyll用ブログ記事生成モジュール
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


class JekyllWriter:
    """Jekyll記事生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.layout = config.get('layout', 'post')
        self.categories = config.get('categories', ['video', 'blog'])
        self.author = config.get('author', 'Video Bot')
        self.permalink_format = config.get('permalink_format', '/:year/:month/:day/:title/')
    
    def create_post(self, title: str, content: Dict, transcript: Dict, output_dir: Path, 
                   featured_image: Optional[Path] = None, section_images: Optional[Dict[str, Path]] = None) -> Path:
        """Jekyll用のブログ記事を生成"""
        
        # 出力ディレクトリ作成
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名生成
        date = datetime.now()
        slug = self._create_slug(title)
        filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
        post_path = output_dir / filename
        
        # Front Matter生成（アイキャッチ画像を含む）
        front_matter = self._generate_front_matter(title, content, date, featured_image)
        
        # 記事本文生成（セクション画像を含む）
        post_content = self._generate_post_content(title, content, transcript, section_images)
        
        # ファイルに書き込み
        full_content = f"{front_matter}\n{post_content}"
        post_path.write_text(full_content, encoding='utf-8')
        
        logger.info(f"✓ Jekyll記事生成: {post_path}")
        return post_path
    
    def _create_slug(self, title: str) -> str:
        """タイトルからURLスラッグを生成"""
        # 日本語を含むタイトルをローマ字変換（簡易版）
        slug = title.lower()
        
        # 特殊文字を削除
        slug = re.sub(r'[^\w\s-]', '', slug)
        # 空白をハイフンに
        slug = re.sub(r'[-\s]+', '-', slug)
        # 前後のハイフンを削除
        slug = slug.strip('-')
        
        # 日本語が含まれる場合は日付ベースのスラッグに
        if re.search(r'[^\x00-\x7F]', title):
            slug = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return slug[:50]  # 最大50文字
    
    def _generate_front_matter(self, title: str, content: Dict, date: datetime, 
                             featured_image: Optional[Path] = None) -> str:
        """Jekyll Front Matterを生成"""
        
        front_matter_data = {
            'layout': self.layout,
            'title': title,
            'date': date.strftime('%Y-%m-%d %H:%M:%S %z'),
            'categories': self.categories,
            'tags': content.get('keywords', [])[:10],  # 最大10個
            'author': self.author,
            'excerpt': content.get('summary', '')[:160],
            'published': True,
            'comments': True,
            # カスタムフィールド
            'video_source': True,
            'word_count': content.get('word_count', 0),
            'reading_time': content.get('reading_time', 1),
        }
        
        # アイキャッチ画像を追加
        if featured_image:
            # 相対パスに変換
            front_matter_data['image'] = f"/assets/images/{featured_image.name}"
            front_matter_data['thumbnail'] = f"/assets/images/thumb_{featured_image.name}"
        
        # YAMLとして出力
        front_matter = "---\n"
        front_matter += yaml.dump(
            front_matter_data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        front_matter += "---"
        
        return front_matter
    
    def _generate_post_content(self, title: str, content: Dict, transcript: Dict, 
                             section_images: Optional[Dict[str, Path]] = None) -> str:
        """記事本文を生成（HTML形式）"""
        
        sections = []
        
        # アイキャッチ画像（記事冒頭に大きく表示）
        if content.get('featured_image_html'):
            sections.append(content['featured_image_html'])
            sections.append("")
        
        # 魅力的な導入文（段落タグで囲む）
        if content.get('introduction'):
            intro_paragraphs = content['introduction'].split('\n\n')
            for para in intro_paragraphs:
                if para.strip():
                    sections.append(f"<p>{para.strip()}</p>")
            sections.append("")
        
        # 目次（HTMLリスト形式）
        if content.get('sections') and len(content['sections']) > 2:
            sections.append('<div class="toc">')
            sections.append('<h2>目次</h2>')
            sections.append('<ul>')
            for section in content['sections']:
                sections.append(f'  <li><a href="#{self._create_anchor(section["title"])}">{section["title"]}</a></li>')
            sections.append('</ul>')
            sections.append('</div>')
            sections.append("")
        
        # 本文セクション（HTML形式）
        for section in content.get('sections', []):
            anchor = self._create_anchor(section['title'])
            
            # H2タグを先に出力
            sections.append(f'<h2 id="{anchor}">{section["title"]}</h2>')
            
            # セクション画像を挿入（H2タグの直下）
            if section_images and section['title'] in section_images:
                img_path = section_images[section['title']]
                sections.append(f'<div class="section-image">')
                sections.append(f'  <img src="/assets/images/{img_path.name}" alt="{section["title"]}" loading="lazy">')
                sections.append(f'</div>')
                sections.append("")  # 画像とコンテンツの間に空行
            
            # セクション内容を段落ごとに処理
            content_parts = section['content'].split('\n\n')
            for part in content_parts:
                part = part.strip()
                if not part:
                    continue
                
                # リスト項目の処理
                if part.startswith('1. ') or part.startswith('- '):
                    lines = part.split('\n')
                    if part.startswith('1. '):
                        sections.append('<ol>')
                        for line in lines:
                            if line.strip().startswith(tuple(f'{i}. ' for i in range(1, 10))):
                                item_text = line.split('. ', 1)[1] if '. ' in line else line
                                sections.append(f'  <li>{self._process_inline_formatting(item_text)}</li>')
                        sections.append('</ol>')
                    else:
                        sections.append('<ul>')
                        for line in lines:
                            if line.strip().startswith('- '):
                                item_text = line[2:].strip()
                                sections.append(f'  <li>{self._process_inline_formatting(item_text)}</li>')
                        sections.append('</ul>')
                # 通常の段落
                else:
                    sections.append(f'<p>{self._process_inline_formatting(part)}</p>')
            sections.append("")
        
        # 結論（HTML形式）
        if content.get('conclusion'):
            conclusion_parts = content['conclusion'].split('\n\n')
            for part in conclusion_parts:
                part = part.strip()
                if part.startswith('## '):
                    sections.append(f'<h2>{part[3:]}</h2>')
                elif part.startswith('1. '):
                    lines = part.split('\n')
                    sections.append('<ol>')
                    for line in lines:
                        if line.strip():
                            item_text = line.split('. ', 1)[1] if '. ' in line else line
                            sections.append(f'  <li>{item_text}</li>')
                    sections.append('</ol>')
                elif part:
                    sections.append(f'<p>{part}</p>')
        
        # メタ情報フッター（HTMLフォーマット）
        sections.append('<hr class="section-divider">')
        sections.append('<div class="article-footer">')
        sections.append('<h3>この記事について</h3>')
        sections.append('<dl class="article-meta">')
        
        # ターゲット読者
        if content.get('target_audience'):
            audience_map = {
                'クリエイター': '動画クリエイター・YouTuber',
                'エンジニア': 'エンジニア・開発者',
                'ビジネスパーソン': 'ビジネスパーソン・マーケター',
                '一般ユーザー': '動画制作に興味がある方'
            }
            audience = audience_map.get(content['target_audience']['primary'], content['target_audience']['primary'])
            sections.append(f'  <dt>対象読者</dt>')
            sections.append(f'  <dd>{audience}</dd>')
        
        sections.append(f'  <dt>読了時間</dt>')
        sections.append(f'  <dd>約{content.get("reading_time", 1)}分</dd>')
        sections.append(f'  <dt>更新日</dt>')
        sections.append(f'  <dd>{datetime.now().strftime("%Y年%m月%d日")}</dd>')
        sections.append('</dl>')
        
        # 主要ポイント（HTML形式）
        if content.get('main_points'):
            sections.append('<div class="key-points">')
            sections.append('<h3>この記事の要点</h3>')
            sections.append('<ul>')
            for point in content['main_points'][:3]:
                clean_text = self._clean_point_text(point['text'])
                sections.append(f'  <li>{clean_text}</li>')
            sections.append('</ul>')
            sections.append('</div>')
        
        sections.append('</div>')
        
        return "\n".join(sections)
    
    def add_video_link_section(self, post_path: Path, video_url: str):
        """既存記事に動画リンクセクションを追加"""
        
        content = post_path.read_text(encoding='utf-8')
        
        video_section = self._generate_video_link_section(video_url)
        
        # 記事フッターの直前に挿入
        if '<div class="article-footer">' in content:
            content = content.replace('<div class="article-footer">', f'{video_section}\n\n<div class="article-footer">')
        else:
            # フッターがない場合は最後に追加
            content += f'\n\n{video_section}'
        
        post_path.write_text(content, encoding='utf-8')
        logger.info(f"✓ 動画リンクセクション追加: {post_path}")
    
    def _generate_video_link_section(self, video_url: str) -> str:
        """動画リンクセクションのHTMLを生成"""
        
        return f"""<div class="video-link-section">
<h3>📺 この記事の動画版</h3>
<p>この記事の内容をより詳しく動画で解説しています。</p>
<div class="video-embed">
  <a href="{video_url}" target="_blank" class="video-link-button">
    <span class="video-icon">▶️</span>
    <span class="video-text">YouTubeで視聴する</span>
  </a>
</div>
<p class="video-note">動画では記事で触れていない詳細な実装方法や、実際のデモンストレーションもご覧いただけます。</p>
</div>"""
    
    def _create_anchor(self, title: str) -> str:
        """見出しからアンカーIDを生成"""
        # 日本語を含むタイトルをURLセーフな形式に変換
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        
        # 日本語の場合はハッシュ化
        if not anchor or anchor == '-':
            import hashlib
            anchor = f"section-{hashlib.md5(title.encode()).hexdigest()[:8]}"
        
        return anchor
    
    def _process_inline_formatting(self, text: str) -> str:
        """インライン書式を処理（太字、強調など）"""
        # **text** を <strong>text</strong> に変換
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # *text* を <em>text</em> に変換
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # 絵文字の前後にスペースを追加（読みやすさのため）
        text = re.sub(r'([^\s])([\u2600-\u27BF\U0001F300-\U0001F9FF])', r'\1 \2', text)
        text = re.sub(r'([\u2600-\u27BF\U0001F300-\U0001F9FF])([^\s])', r'\1 \2', text)
        return text
    
    def _clean_point_text(self, text: str) -> str:
        """ポイントテキストをクリーンアップ"""
        # 不自然な文末や繰り返しを削除
        text = re.sub(r'、このシステムを活用して、.*?で$', '', text)
        text = re.sub(r'っていう.*?です$', 'ということ', text)
        text = re.sub(r'じゃないかな', 'ではないか', text)
        
        # より自然な日本語に
        if len(text) > 50:
            # 長すぎる場合は要約
            if '自動' in text:
                text = "動画から各種コンテンツを自動生成するシステム"
            elif '時間' in text:
                text = "作業時間を大幅に短縮できる"
            elif 'アイディア' in text or 'アイデア' in text:
                text = "革新的なコンテンツ自動化のアイデア"
        
        return text
    
    def create_index_page(self, posts: List[Dict], output_path: Path) -> Path:
        """インデックスページを生成"""
        
        index_content = """---
layout: page
title: 動画ブログ一覧
permalink: /videos/
---

# 動画ブログ一覧

{% for post in site.categories.video %}
<article class="post-preview">
  <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
  <p class="post-meta">
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y年%m月%d日" }}</time>
    • {{ post.reading_time }}分で読了
  </p>
  <p>{{ post.excerpt }}</p>
  <p class="post-tags">
    {% for tag in post.tags %}
    <span class="tag">{{ tag }}</span>
    {% endfor %}
  </p>
</article>
{% endfor %}
"""
        
        output_path.write_text(index_content, encoding='utf-8')
        return output_path


class JekyllConfig:
    """Jekyll設定管理クラス"""
    
    @staticmethod
    def generate_config(site_title: str, site_url: str, output_path: Path) -> Path:
        """_config.ymlを生成"""
        
        config = {
            'title': site_title,
            'description': 'Whisperで文字起こしした動画ブログ',
            'url': site_url,
            'baseurl': '',
            
            # ビルド設定
            'markdown': 'kramdown',
            'theme': 'minima',
            'plugins': [
                'jekyll-feed',
                'jekyll-seo-tag',
                'jekyll-sitemap',
                'jekyll-paginate'
            ],
            
            # パーマリンク
            'permalink': '/:year/:month/:day/:title/',
            
            # ページネーション
            'paginate': 10,
            'paginate_path': '/page:num/',
            
            # デフォルト設定
            'defaults': [
                {
                    'scope': {
                        'path': '',
                        'type': 'posts'
                    },
                    'values': {
                        'layout': 'post',
                        'comments': True
                    }
                }
            ],
            
            # カテゴリ設定
            'category_archive': {
                'type': 'liquid',
                'path': '/categories/'
            },
            
            # タグ設定
            'tag_archive': {
                'type': 'liquid',
                'path': '/tags/'
            }
        }
        
        config_yaml = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        output_path.write_text(config_yaml, encoding='utf-8')
        
        return output_path