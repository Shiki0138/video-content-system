"""
文字起こしデータから各種コンテンツを生成するモジュール
"""

import re
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ContentGenerator:
    """コンテンツ生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.blog_config = config.get('blog', {})
        self.youtube_config = config.get('youtube', {})
        self.twitter_config = config.get('twitter', {})
    
    def generate_all(self, transcript_data: Dict, title: str, video_info: Dict) -> Dict:
        """すべてのコンテンツを生成"""
        
        logger.info("コンテンツ生成開始...")
        
        # テキストをクリーンアップ
        clean_text = self._clean_text(transcript_data['text'])
        
        # ブログコンテンツを生成（画像生成も含む）
        blog_content = self._generate_blog_content(transcript_data, title, video_info)
        
        # 画像生成（設定で有効な場合）
        if self.blog_config.get('generate_images', True):
            from .image_generator import BlogImageGenerator
            img_generator = BlogImageGenerator(self.blog_config.get('image_settings', {}))
            
            # アイキャッチ画像
            if self.blog_config.get('generate_featured_image', True):
                featured_path = Path('output/images') / f"featured_{title.replace(' ', '_')}.png"
                featured_path.parent.mkdir(parents=True, exist_ok=True)
                img_generator.generate_featured_image(
                    title,
                    blog_content.get('meta_description', '')[:100],
                    featured_path
                )
                blog_content['featured_image'] = featured_path
                blog_content['featured_image_html'] = f'<div class="featured-image"><img src="/assets/images/{featured_path.name}" alt="{title}" loading="eager"></div>'
            
            # セクション画像
            if self.blog_config.get('generate_section_images', True) and blog_content.get('sections'):
                section_images = img_generator.generate_section_images(
                    blog_content['sections'],
                    Path('output/images/sections')
                )
                blog_content['section_images'] = section_images
        
        # 各種コンテンツ生成
        content = {
            'blog': blog_content,
            'youtube': self._generate_youtube_description(transcript_data, title, video_info),
            'twitter': self._generate_twitter_post(title, clean_text),
            'thumbnail': self._generate_thumbnail_text(title, clean_text)
        }
        
        return content
    
    def _clean_text(self, text: str) -> str:
        """テキストをクリーンアップ"""
        # 余分な空白を削除
        text = re.sub(r'\s+', ' ', text)
        # 句読点の修正
        text = re.sub(r'\s+。', '。', text)
        text = re.sub(r'\s+、', '、', text)
        text = re.sub(r'\s+！', '！', text)
        text = re.sub(r'\s+？', '？', text)
        return text.strip()
    
    def _generate_blog_content(self, transcript_data: Dict, title: str, video_info: Dict) -> Dict:
        """ブログ記事コンテンツを生成"""
        
        # BlogOptimizerを使用して高品質なブログコンテンツを生成
        from .blog_optimizer import BlogOptimizer
        
        optimizer = BlogOptimizer(self.blog_config)
        optimized_content = optimizer.optimize_for_blog(transcript_data, title, video_info)
        
        return optimized_content
    
    def _generate_youtube_description(self, transcript_data: Dict, title: str, video_info: Dict) -> str:
        """YouTube説明文を生成"""
        
        text = transcript_data['text']
        chapters = transcript_data.get('chapters', [])
        
        # 要約
        summary = self._generate_summary(text, max_length=200)
        
        # 説明文構築
        description_parts = [
            f"【{title}】",
            "",
            summary,
            ""
        ]
        
        # チャプター追加
        if self.youtube_config.get('add_chapters', True) and chapters:
            description_parts.extend([
                "▼ チャプター ▼",
                "0:00 オープニング"
            ])
            for chapter in chapters:
                description_parts.append(f"{chapter['time']} {chapter['title']}")
            description_parts.append("")
        
        # キーワード
        keywords = self._extract_keywords(text, num=5)
        if keywords:
            description_parts.extend([
                "▼ キーワード ▼",
                ", ".join(keywords),
                ""
            ])
        
        # デフォルトタグ
        tags = self.youtube_config.get('default_tags', [])
        if tags:
            description_parts.extend([
                "▼ タグ ▼",
                " ".join([f"#{tag}" for tag in tags]),
                ""
            ])
        
        # リンク
        description_parts.extend([
            "▼ 関連リンク ▼",
            "ブログ: [ブログURL]",
            "Twitter: [TwitterURL]",
            ""
        ])
        
        description = "\n".join(description_parts)
        
        # 文字数制限
        max_length = self.youtube_config.get('max_description_length', 5000)
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
        
        return description
    
    def _generate_twitter_post(self, title: str, text: str) -> str:
        """X(Twitter)投稿文を生成"""
        
        # 要約
        summary = self._generate_summary(text, max_length=100)
        
        # 基本投稿文
        post = f"【{title}】\n{summary}"
        
        # ハッシュタグ追加
        if self.twitter_config.get('add_hashtags', True):
            keywords = self._extract_keywords(text, num=self.twitter_config.get('max_hashtags', 3))
            hashtags = " ".join([f"#{kw}" for kw in keywords[:3]])
            post += f"\n\n{hashtags}"
        
        # 文字数制限
        max_length = self.twitter_config.get('max_length', 140)
        if len(post) > max_length:
            # ハッシュタグを維持しつつ短縮
            base_length = max_length - len(hashtags) - 10
            post = f"【{title}】\n{summary[:base_length]}...\n\n{hashtags}"
        
        return post
    
    def _generate_thumbnail_text(self, title: str, text: str) -> Dict:
        """サムネイル用テキストを生成"""
        
        # キーワード抽出
        keywords = self._extract_keywords(text, num=3)
        
        # メインタイトル（短縮版）
        main_title = title
        if len(main_title) > 15:
            main_title = main_title[:15] + "..."
        
        # サブタイトル生成
        if keywords:
            subtitle = f"{keywords[0]}について解説"
        else:
            subtitle = "詳細は動画で！"
        
        return {
            'title': main_title,
            'subtitle': subtitle,
            'keywords': keywords
        }
    
    def _split_into_sections(self, text: str, min_length: int = 200, max_length: int = 500) -> List[Dict]:
        """テキストをセクションに分割"""
        
        sentences = re.split(r'[。！？\n]+', text)
        sections = []
        current_section = ""
        section_count = 1
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_section) + len(sentence) > max_length and len(current_section) >= min_length:
                sections.append({
                    'number': section_count,
                    'title': f"セクション {section_count}",
                    'content': current_section.strip(),
                    'word_count': len(current_section)
                })
                section_count += 1
                current_section = sentence + "。"
            else:
                current_section += sentence + "。"
        
        # 最後のセクション
        if current_section and len(current_section) >= min_length // 2:
            sections.append({
                'number': section_count,
                'title': f"セクション {section_count}",
                'content': current_section.strip(),
                'word_count': len(current_section)
            })
        
        return sections
    
    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """テキストの要約を生成（簡易版）"""
        
        sentences = re.split(r'[。！？]+', text)
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 重要そうな文を優先
            importance_score = 0
            if any(keyword in sentence for keyword in ['です', 'ます', 'について', 'とは', 'ため']):
                importance_score += 1
            if len(sentence) > 20 and len(sentence) < 100:
                importance_score += 1
            
            if importance_score > 0 and current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
            
            if len(summary_sentences) >= 3:
                break
        
        return "。".join(summary_sentences) + "。" if summary_sentences else text[:max_length] + "..."
    
    def _extract_keywords(self, text: str, num: int = 5) -> List[str]:
        """キーワードを抽出（簡易版）"""
        
        # ストップワード
        stopwords = {
            'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 
            'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 
            'や', 'など', 'なっ', 'ない', 'この', 'ため', 'その', 'あっ', 'よう', 
            'また', 'もの', 'という', 'あり', 'まで', 'られ', 'なる', 'へ', 'か', 
            'だ', 'これ', 'によって', 'により', 'おり', 'より', 'による', 'ず', 
            'なり', 'られる', 'において', 'ば', 'なかっ', 'なく', 'しかし', 
            'について', 'だけ', 'だっ', 'その他', 'それ', 'ところ'
        }
        
        # 単語分割（簡易版）
        words = re.findall(r'[一-龥ぁ-んァ-ンー\w]{2,}', text)
        
        # 単語カウント
        word_count = {}
        for word in words:
            if word not in stopwords and len(word) >= 2:
                word_count[word] = word_count.get(word, 0) + 1
        
        # 頻出順にソート
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # 上位N個を返す
        return [word[0] for word in sorted_words[:num]]
    
    def _generate_toc(self, sections: List[Dict]) -> List[str]:
        """目次を生成"""
        toc = []
        for section in sections:
            toc.append(f"- {section['title']} ({section['word_count']}文字)")
        return toc