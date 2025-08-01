"""
WordPress/CMS用コンテンツ生成モジュール
HTMLタグ付きでコピー&ペースト可能な形式で出力
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class WordPressContentGenerator:
    """WordPress/CMS用コンテンツ生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def create_content(self, title: str, content: Dict, transcript: Dict, 
                      output_dir: Path) -> Dict[str, Path]:
        """WordPress/CMS用のコンテンツを生成"""
        
        # 出力ディレクトリ作成
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名生成
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug = self._create_slug(title)
        
        # 生成するコンテンツ
        outputs = {}
        
        # 1. メインブログコンテンツ（HTML形式）
        blog_content = self._generate_blog_content(title, content, transcript)
        blog_path = output_dir / f"{date_str}-{slug}-blog.html"
        blog_path.write_text(blog_content, encoding='utf-8')
        outputs['blog'] = blog_path
        
        # 2. SEO用メタデータ
        meta_content = self._generate_meta_content(title, content)
        meta_path = output_dir / f"{date_str}-{slug}-meta.txt"
        meta_path.write_text(meta_content, encoding='utf-8')
        outputs['meta'] = meta_path
        
        # 3. タグ・カテゴリリスト
        taxonomy_content = self._generate_taxonomy_content(content)
        taxonomy_path = output_dir / f"{date_str}-{slug}-taxonomy.txt"
        taxonomy_path.write_text(taxonomy_content, encoding='utf-8')
        outputs['taxonomy'] = taxonomy_path
        
        logger.info(f"✓ WordPress/CMSコンテンツ生成完了: {output_dir}")
        return outputs
    
    def _create_slug(self, title: str) -> str:
        """タイトルからURLスラッグを生成"""
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
    
    def _generate_blog_content(self, title: str, content: Dict, transcript: Dict) -> str:
        """ブログコンテンツ本文を生成（HTMLタグ付き）"""
        
        sections = []
        
        # タイトル
        sections.append(f'<!-- ブログタイトル -->')
        sections.append(f'<h1>{title}</h1>')
        sections.append('')
        
        # アイキャッチ画像プレースホルダー
        sections.append('<!-- アイキャッチ画像 -->')
        sections.append('<!-- ここにアイキャッチ画像を挿入してください -->')
        sections.append('')
        
        # 導入文
        if content.get('introduction'):
            sections.append('<!-- 導入文 -->')
            intro_paragraphs = content['introduction'].split('\n\n')
            for para in intro_paragraphs:
                if para.strip():
                    sections.append(f'<p>{self._process_inline_formatting(para.strip())}</p>')
            sections.append('')
        
        # 目次（自動生成される場合はコメントアウト可）
        if content.get('sections') and len(content['sections']) > 2:
            sections.append('<!-- 目次 -->')
            sections.append('<div class="toc">')
            sections.append('<h2>目次</h2>')
            sections.append('<ul>')
            for i, section in enumerate(content['sections'], 1):
                sections.append(f'  <li><a href="#section{i}">{section["title"]}</a></li>')
            sections.append('</ul>')
            sections.append('</div>')
            sections.append('')
        
        # メインコンテンツ
        sections.append('<!-- メインコンテンツ -->')
        for i, section in enumerate(content.get('sections', []), 1):
            # 見出し
            sections.append(f'<h2 id="section{i}">{section["title"]}</h2>')
            
            # セクション画像プレースホルダー
            sections.append(f'<!-- セクション{i}の画像（オプション） -->')
            sections.append('')
            
            # セクション内容
            content_parts = section['content'].split('\n\n')
            for part in content_parts:
                part = part.strip()
                if not part:
                    continue
                
                # リスト項目の処理
                if self._is_ordered_list(part):
                    sections.append('<ol>')
                    for line in part.split('\n'):
                        if re.match(r'^\d+\.\s', line):
                            item_text = re.sub(r'^\d+\.\s+', '', line)
                            sections.append(f'  <li>{self._process_inline_formatting(item_text)}</li>')
                    sections.append('</ol>')
                elif self._is_unordered_list(part):
                    sections.append('<ul>')
                    for line in part.split('\n'):
                        if line.strip().startswith('- '):
                            item_text = line[2:].strip()
                            sections.append(f'  <li>{self._process_inline_formatting(item_text)}</li>')
                    sections.append('</ul>')
                # 通常の段落
                else:
                    sections.append(f'<p>{self._process_inline_formatting(part)}</p>')
            
            sections.append('')
        
        # まとめ/結論
        if content.get('conclusion'):
            sections.append('<!-- まとめ -->')
            sections.append('<h2>まとめ</h2>')
            conclusion_parts = content['conclusion'].split('\n\n')
            for part in conclusion_parts:
                part = part.strip()
                if part and not part.startswith('## '):
                    sections.append(f'<p>{self._process_inline_formatting(part)}</p>')
            sections.append('')
        
        # CTA（Call to Action）
        sections.append('<!-- CTA（Call to Action） -->')
        sections.append('<div class="cta-section">')
        sections.append('<h3>この記事が役に立ったら</h3>')
        sections.append('<p>ぜひシェアやコメントをお願いします！質問やご意見もお待ちしています。</p>')
        sections.append('</div>')
        
        return '\n'.join(sections)
    
    def _generate_meta_content(self, title: str, content: Dict) -> str:
        """SEO用メタデータを生成"""
        
        meta_sections = []
        
        # タイトル
        meta_sections.append('【SEOタイトル】')
        meta_sections.append(title)
        meta_sections.append('')
        
        # メタディスクリプション
        meta_sections.append('【メタディスクリプション（150文字程度）】')
        if content.get('summary'):
            meta_desc = content['summary'][:150] + '...' if len(content['summary']) > 150 else content['summary']
            meta_sections.append(meta_desc)
        meta_sections.append('')
        
        # フォーカスキーワード
        meta_sections.append('【フォーカスキーワード】')
        if content.get('keywords'):
            primary_keywords = content['keywords'][:5]
            meta_sections.append(', '.join(primary_keywords))
        meta_sections.append('')
        
        # URLスラッグ
        meta_sections.append('【URLスラッグ（推奨）】')
        meta_sections.append(self._create_slug(title))
        meta_sections.append('')
        
        # 抜粋文
        meta_sections.append('【抜粋文】')
        if content.get('introduction'):
            excerpt = content['introduction'].split('\n\n')[0][:200]
            meta_sections.append(excerpt)
        
        return '\n'.join(meta_sections)
    
    def _generate_taxonomy_content(self, content: Dict) -> str:
        """タグ・カテゴリ情報を生成"""
        
        taxonomy_sections = []
        
        # カテゴリ（推奨）
        taxonomy_sections.append('【推奨カテゴリ】')
        if content.get('target_audience'):
            audience = content['target_audience'].get('primary', '')
            category_map = {
                'クリエイター': 'クリエイター向け',
                'エンジニア': '技術・開発',
                'ビジネスパーソン': 'ビジネス',
                '一般ユーザー': '一般・入門'
            }
            category = category_map.get(audience, '一般')
            taxonomy_sections.append(category)
        taxonomy_sections.append('')
        
        # タグ
        taxonomy_sections.append('【タグ（10個まで）】')
        if content.get('keywords'):
            tags = content['keywords'][:10]
            for tag in tags:
                taxonomy_sections.append(f'- {tag}')
        taxonomy_sections.append('')
        
        # 関連キーワード
        taxonomy_sections.append('【関連キーワード（内部リンク用）】')
        if content.get('main_points'):
            for point in content['main_points'][:3]:
                keyword = self._extract_keyword(point['text'])
                if keyword:
                    taxonomy_sections.append(f'- {keyword}')
        
        return '\n'.join(taxonomy_sections)
    
    def _process_inline_formatting(self, text: str) -> str:
        """インライン書式を処理（太字、強調など）"""
        # **text** を <strong>text</strong> に変換
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # *text* を <em>text</em> に変換
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # 改行をbrタグに変換（必要に応じて）
        # text = text.replace('\n', '<br>')
        return text
    
    def _is_ordered_list(self, text: str) -> bool:
        """番号付きリストかどうかを判定"""
        lines = text.split('\n')
        return any(re.match(r'^\d+\.\s', line) for line in lines)
    
    def _is_unordered_list(self, text: str) -> bool:
        """箇条書きリストかどうかを判定"""
        lines = text.split('\n')
        return any(line.strip().startswith('- ') for line in lines)
    
    def _extract_keyword(self, text: str) -> Optional[str]:
        """テキストから主要キーワードを抽出"""
        # シンプルな実装：最初の名詞句を抽出
        if '自動' in text:
            return '自動化'
        elif 'AI' in text or '人工知能' in text:
            return 'AI活用'
        elif '時間' in text or '効率' in text:
            return '時間短縮'
        elif 'ブログ' in text:
            return 'ブログ作成'
        elif '動画' in text:
            return '動画活用'
        return None