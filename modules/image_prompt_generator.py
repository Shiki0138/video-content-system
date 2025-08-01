#!/usr/bin/env python3
"""
画像プロンプト生成モジュール
DALL-E 3/ChatGPT用の高品質プロンプトを自動生成
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ImagePromptGenerator:
    """画像生成プロンプト作成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        logger.info("画像プロンプト生成器を初期化しました")
    
    def generate_youtube_thumbnail_prompt(self, title: str, transcript_data: Dict, 
                                        style: str = "professional") -> str:
        """YouTubeサムネイル用プロンプト生成"""
        
        # スタイル別プロンプトテンプレート
        styles = {
            "professional": self._generate_professional_thumbnail,
            "tech": self._generate_tech_thumbnail,
            "business": self._generate_business_thumbnail,
            "educational": self._generate_educational_thumbnail
        }
        
        generator = styles.get(style, self._generate_professional_thumbnail)
        return generator(title, transcript_data)
    
    def generate_blog_featured_prompt(self, title: str, content: Dict) -> str:
        """ブログアイキャッチ画像用プロンプト生成"""
        
        keywords = content.get('keywords', [])
        main_topic = content.get('main_topic', title)
        
        prompt = f"""Create a professional blog featured image with modern design aesthetics.

MAIN ELEMENTS:
- Topic: "{main_topic}"
- Visual theme representing: {', '.join(keywords[:3]) if keywords else 'technology and innovation'}
- Abstract or conceptual visualization (no text needed)
- Professional gradient background with subtle patterns
- Color scheme: Modern tech colors (blues, purples, or corporate colors)
- High-quality, eye-catching composition

COMPOSITION:
- Center-focused main visual element
- Balanced negative space
- Professional lighting and shadows
- Suitable for blog header (16:9 or similar ratio)

STYLE: Modern, professional, tech-oriented, clean design suitable for blog featured image"""
        
        return prompt
    
    def generate_blog_section_prompts(self, sections: List[Dict]) -> List[Dict]:
        """ブログセクション画像用プロンプト生成"""
        
        prompts = []
        
        for i, section in enumerate(sections[:3]):  # 最大3セクション
            section_title = section.get('title', f'Section {i+1}')
            section_content = section.get('content', '')
            
            prompt = f"""Create a simple, clean illustration for a blog section.

SECTION THEME: "{section_title}"
CONTENT CONTEXT: Illustrating the concept of {self._extract_concept(section_content)}

REQUIREMENTS:
- Simple, minimalist illustration
- Flat design or light 3D style
- Clear visual metaphor for the section topic
- Soft, friendly color palette
- No text or words in the image
- Square format (1:1 ratio)

STYLE: Minimal, friendly, professional illustration suitable for blog content"""
            
            prompts.append({
                'section': section_title,
                'prompt': prompt,
                'index': i + 1
            })
        
        return prompts
    
    def _generate_professional_thumbnail(self, title: str, transcript_data: Dict) -> str:
        """プロフェッショナルスタイルサムネイル"""
        return f"""Create a professional YouTube thumbnail that looks like it was made by a top YouTuber's design team.

MAIN ELEMENTS:
- Bold Japanese text "{title[:20]}..." with 3D effect and glowing outline
- Subtitle showing the main benefit or topic in smaller text
- Visual workflow or concept illustration related to the content
- Color scheme: bright orange/yellow gradient background with electric blue accents
- Professional lighting effects and shadows

COMPOSITION:
- Left side: Large bold text taking 40% of space
- Right side: 3D mockup or visual representation of the concept
- High contrast for mobile viewing optimization
- Clean, modern design that screams "professional tutorial"

STYLE: High-end YouTube thumbnail, bright and engaging, professional quality"""
    
    def _generate_tech_thumbnail(self, title: str, transcript_data: Dict) -> str:
        """テック系スタイルサムネイル"""
        return f"""Design a tech influencer style YouTube thumbnail with maximum visual impact.

CORE DESIGN:
- Center: Glowing "{title[:15]}..." text with neon effect
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

STYLE: Tech influencer, futuristic, high-tech, premium quality"""
    
    def _generate_business_thumbnail(self, title: str, transcript_data: Dict) -> str:
        """ビジネス系スタイルサムネイル"""
        return f"""Create a business professional YouTube thumbnail with corporate appeal.

BUSINESS ELEMENTS:
- Top: "{title[:25]}..." in bold corporate font
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

STYLE: Corporate professional, clean, trustworthy, business-grade quality"""
    
    def _generate_educational_thumbnail(self, title: str, transcript_data: Dict) -> str:
        """教育系スタイルサムネイル"""
        return f"""Design an educational YouTube thumbnail that encourages learning.

EDUCATIONAL ELEMENTS:
- Clear title: "{title[:20]}..." with readable font
- Visual metaphor for learning or understanding
- Step-by-step visual representation if applicable
- Bright, engaging colors (but not overwhelming)
- Icons or illustrations that support the topic
- "Before/After" or "Problem/Solution" visual if relevant

COMPOSITION:
- Clear visual hierarchy
- Easy to understand at a glance
- Whiteboard or classroom aesthetic elements
- Friendly and approachable design

STYLE: Educational, clear, friendly, encouraging, professional teaching quality"""
    
    def _extract_concept(self, content: str) -> str:
        """コンテンツから主要概念を抽出"""
        # 簡易的な概念抽出（実際にはより高度な処理が可能）
        if len(content) > 100:
            return content[:100] + "..."
        return content or "the main topic"
    
    def generate_all_prompts(self, title: str, transcript_data: Dict, 
                           blog_content: Dict) -> Dict[str, any]:
        """全ての画像プロンプトを一括生成"""
        
        result = {
            'youtube_thumbnail': {
                'professional': self.generate_youtube_thumbnail_prompt(title, transcript_data, 'professional'),
                'tech': self.generate_youtube_thumbnail_prompt(title, transcript_data, 'tech'),
                'business': self.generate_youtube_thumbnail_prompt(title, transcript_data, 'business')
            },
            'blog_featured': self.generate_blog_featured_prompt(title, blog_content),
            'blog_sections': self.generate_blog_section_prompts(blog_content.get('sections', []))
        }
        
        logger.info(f"全プロンプト生成完了: サムネイル3種、ブログ画像{len(result['blog_sections']) + 1}種")
        
        return result