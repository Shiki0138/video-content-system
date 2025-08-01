"""
[DEPRECATED] このモジュールは廃止されました

現在のシステムでは画像の自動生成は行わず、
DALL-E 3やChatGPT用のプロンプトを生成する方式に変更されました。

代わりに modules/image_prompt_generator.py を使用してください。

---

バイラルサムネイル生成モジュール（旧バージョン）
参考のために残していますが、使用は推奨されません。
"""

import logging
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import colorsys
import math

logger = logging.getLogger(__name__)


class ViralThumbnailCreator:
    """バイラルサムネイル生成クラス - YouTubeでクリックされやすいサムネイルを生成"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.width = 1280
        self.height = 720
        
        # YouTube最適化された心理的カラーパレット
        self.psychology_colors = {
            'urgency': ['#FF0000', '#FF4444', '#CC0000'],      # 緊急性・重要性
            'curiosity': ['#FFD700', '#FFA500', '#FF6B35'],    # 好奇心・驚き
            'trust': ['#4285F4', '#1976D2', '#0D47A1'],        # 信頼・専門性
            'energy': ['#FF3B30', '#FF2D92', '#AF52DE'],       # エネルギー・行動
            'success': ['#34C759', '#00C896', '#32D74B'],      # 成功・達成
            'premium': ['#6366F1', '#8B5CF6', '#A855F7'],      # プレミアム・高級
        }
        
        # 心理的キーワード検出
        self.emotional_triggers = {
            'urgency': ['緊急', '今すぐ', '急げ', '限定', '最後', '終了', '警告'],
            'curiosity': ['秘密', '裏技', '真実', '驚愕', 'ヤバい', '衝撃', '謎'],
            'tutorial': ['方法', '手順', '解説', 'やり方', 'コツ', 'テクニック'],
            'success': ['成功', '達成', '勝利', '儲かる', '稼ぐ', '効果'],
            'problem': ['失敗', '間違い', '危険', '注意', '問題', 'トラブル'],
            'comparison': ['比較', 'VS', '対決', 'どっち', '違い', 'ランキング']
        }
        
    def create_viral_options(self, title: str, transcript_data: Dict, output_dir: Path) -> List[Dict]:
        """3つの戦略的バリエーションを生成"""
        
        logger.info("🎨 バイラルサムネイル生成開始...")
        
        # 動画内容を分析
        content_analysis = self._analyze_content(title, transcript_data)
        
        # 3つの戦略を動的に生成
        strategies = self._generate_strategies(content_analysis)
        
        results = []
        for i, strategy in enumerate(strategies, 1):
            try:
                thumbnail_path = output_dir / f"thumbnail_variant_{i}.png"
                self._create_strategic_thumbnail(strategy, thumbnail_path)
                
                results.append({
                    'variant': i,
                    'strategy': strategy['name'],
                    'description': strategy['description'],
                    'path': str(thumbnail_path),
                    'psychological_appeal': strategy['psychology'],
                    'target_emotion': strategy['emotion']
                })
                
                logger.info(f"✓ バリエーション{i}: {strategy['name']} 生成完了")
                
            except Exception as e:
                logger.error(f"サムネイル生成エラー (バリエーション{i}): {e}")
                continue
        
        return results
    
    def _analyze_content(self, title: str, transcript_data: Dict) -> Dict:
        """動画内容の心理的分析"""
        
        text = f"{title} {transcript_data.get('text', '')}"
        
        analysis = {
            'title': title,
            'key_emotions': [],
            'main_topic': self._extract_main_topic(text),
            'emotional_intensity': self._calculate_intensity(text),
            'content_type': self._detect_content_type(text),
            'target_demographic': self._analyze_demographic(text),
            'urgency_level': self._detect_urgency(text),
            'keywords': self._extract_key_phrases(text)
        }
        
        # 感情的トリガーを検出
        for emotion, triggers in self.emotional_triggers.items():
            if any(trigger in text for trigger in triggers):
                analysis['key_emotions'].append(emotion)
        
        return analysis
    
    def _generate_strategies(self, analysis: Dict) -> List[Dict]:
        """コンテンツ分析に基づいて3つの戦略を動的生成"""
        
        # 基本的な3つのアプローチ
        base_strategies = [
            {
                'approach': 'emotional_hook',
                'focus': 'インパクト重視',
                'psychology': '感情的反応を誘発'
            },
            {
                'approach': 'curiosity_gap',
                'focus': '好奇心誘発',
                'psychology': '情報ギャップを利用'
            },
            {
                'approach': 'social_proof',
                'focus': '権威性・信頼',
                'psychology': '社会的証明を活用'
            }
        ]
        
        strategies = []
        
        for i, base in enumerate(base_strategies):
            strategy = self._customize_strategy(base, analysis, i)
            strategies.append(strategy)
        
        return strategies
    
    def _customize_strategy(self, base_strategy: Dict, analysis: Dict, index: int) -> Dict:
        """分析結果に基づいて戦略をカスタマイズ"""
        
        title = analysis['title']
        emotions = analysis['key_emotions']
        content_type = analysis['content_type']
        
        if index == 0:  # 感情的インパクト重視
            return {
                'name': 'インパクト・ショック型',
                'description': '視覚的インパクトで注意を引く',
                'psychology': '瞬間的な感情反応',
                'emotion': 'shock',
                'colors': self._select_colors(['urgency', 'energy']),
                'title_text': self._create_impact_title(title),
                'subtitle': '⚡今すぐ確認⚡',
                'layout': 'dramatic',
                'effects': ['glow', 'shadow', 'gradient'],
                'font_style': 'bold_condensed',
                'emoji_intensity': 'high'
            }
            
        elif index == 1:  # 好奇心ギャップ型
            return {
                'name': 'ミステリー・好奇心型',
                'description': '秘密や謎を示唆して好奇心を刺激',
                'psychology': '情報欲求を刺激',
                'emotion': 'curiosity',
                'colors': self._select_colors(['curiosity', 'premium']),
                'title_text': self._create_curiosity_title(title),
                'subtitle': '驚きの真実が明らかに...',
                'layout': 'mystery',
                'effects': ['blur_reveal', 'highlight', 'frame'],
                'font_style': 'elegant',
                'emoji_intensity': 'medium'
            }
            
        else:  # 権威性・信頼型
            return {
                'name': 'エキスパート・権威型',
                'description': '専門性と信頼性を前面に',
                'psychology': '権威への信頼',
                'emotion': 'trust',
                'colors': self._select_colors(['trust', 'success']),
                'title_text': self._create_authority_title(title),
                'subtitle': '専門家が詳しく解説',
                'layout': 'professional',
                'effects': ['clean_shadow', 'border', 'badge'],
                'font_style': 'professional',
                'emoji_intensity': 'low'
            }
    
    def _create_strategic_thumbnail(self, strategy: Dict, output_path: Path):
        """戦略に基づいてサムネイルを生成"""
        
        # ベース画像作成
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 背景生成
        self._create_strategic_background(img, draw, strategy)
        
        # テキスト配置
        self._add_strategic_text(img, draw, strategy)
        
        # 戦略的エフェクト追加
        img = self._apply_strategic_effects(img, strategy)
        
        # 最終調整
        img = self._final_optimization(img, strategy)
        
        # 保存
        img.save(output_path, 'PNG', quality=95, optimize=True)
    
    def _create_strategic_background(self, img: Image.Image, draw: ImageDraw.Draw, strategy: Dict):
        """戦略に応じた背景を生成"""
        
        colors = strategy['colors']
        layout = strategy['layout']
        
        if layout == 'dramatic':
            # 劇的なグラデーション
            self._create_dramatic_gradient(draw, colors)
            # 光線エフェクト
            self._add_light_rays(draw, colors[0])
            
        elif layout == 'mystery':
            # ミステリアスなグラデーション
            self._create_mystery_background(draw, colors)
            # 粒子エフェクト
            self._add_particle_effects(draw, colors[1])
            
        else:  # professional
            # プロフェッショナルなグラデーション
            self._create_clean_gradient(draw, colors)
            # シンプルなパターン
            self._add_subtle_pattern(draw, colors[0])
    
    def _add_strategic_text(self, img: Image.Image, draw: ImageDraw.Draw, strategy: Dict):
        """戦略的テキスト配置"""
        
        title_text = strategy['title_text']
        subtitle = strategy['subtitle']
        font_style = strategy['font_style']
        
        # フォントサイズを動的調整
        title_font_size = self._calculate_optimal_font_size(title_text, font_style)
        
        # フォント取得
        title_font = self._get_strategic_font(title_font_size, font_style, bold=True)
        subtitle_font = self._get_strategic_font(32, font_style, bold=False)
        
        # テキスト位置計算
        title_pos = self._calculate_text_position(draw, title_text, title_font, 'title', strategy)
        subtitle_pos = self._calculate_text_position(draw, subtitle, subtitle_font, 'subtitle', strategy)
        
        # アウトライン・影効果
        self._draw_text_with_effects(draw, title_text, title_pos, title_font, strategy, 'title')
        self._draw_text_with_effects(draw, subtitle, subtitle_pos, subtitle_font, strategy, 'subtitle')
    
    def _apply_strategic_effects(self, img: Image.Image, strategy: Dict) -> Image.Image:
        """戦略的エフェクトを適用"""
        
        effects = strategy['effects']
        
        for effect in effects:
            if effect == 'glow':
                img = self._apply_glow_effect(img, strategy['colors'][0])
            elif effect == 'shadow':
                img = self._apply_drop_shadow(img)
            elif effect == 'blur_reveal':
                img = self._apply_blur_reveal(img)
            elif effect == 'highlight':
                img = self._apply_highlight_effect(img, strategy['colors'][1])
            elif effect == 'border':
                img = self._apply_premium_border(img, strategy['colors'][0])
        
        return img
    
    def _final_optimization(self, img: Image.Image, strategy: Dict) -> Image.Image:
        """YouTubeアルゴリズム最適化"""
        
        # コントラスト強化
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # 彩度調整
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        
        # シャープネス
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        return img
    
    # ===== ヘルパーメソッド =====
    
    def _select_colors(self, color_types: List[str]) -> List[str]:
        """心理的カラーパレットから選択"""
        colors = []
        for color_type in color_types:
            if color_type in self.psychology_colors:
                colors.extend(self.psychology_colors[color_type])
        return random.sample(colors, min(3, len(colors))) if colors else ['#FF0000', '#00FF00', '#0000FF']
    
    def _create_impact_title(self, original_title: str) -> str:
        """インパクトのあるタイトルに変換"""
        impact_prefixes = ['衝撃!', '緊急!', '警告:', '⚠️', '🔥']
        impact_suffixes = ['【必見】', '【緊急】', '【重要】', '!?', '!!!']
        
        prefix = random.choice(impact_prefixes)
        suffix = random.choice(impact_suffixes)
        
        return f"{prefix} {original_title} {suffix}"
    
    def _create_curiosity_title(self, original_title: str) -> str:
        """好奇心を刺激するタイトルに変換"""
        curiosity_prefixes = ['秘密の', '驚愕の', '謎の', '🤔', '💡']
        curiosity_suffixes = ['の真実', 'の裏側', 'とは?', '【衝撃】', '【謎】']
        
        prefix = random.choice(curiosity_prefixes)
        suffix = random.choice(curiosity_suffixes)
        
        return f"{prefix}{original_title}{suffix}"
    
    def _create_authority_title(self, original_title: str) -> str:
        """権威性のあるタイトルに変換"""
        authority_prefixes = ['プロが教える', '専門家解説', '完全解説:', '📚', '🎓']
        authority_suffixes = ['【完全版】', '【詳細解説】', '【プロ監修】', 'ガイド', 'マスター']
        
        prefix = random.choice(authority_prefixes)
        suffix = random.choice(authority_suffixes)
        
        return f"{prefix} {original_title} {suffix}"
    
    def _extract_main_topic(self, text: str) -> str:
        """メイントピックを抽出"""
        # 簡易的な実装 - より高度なNLP処理も可能
        words = text.split()
        return ' '.join(words[:5])  # 最初の5単語
    
    def _calculate_intensity(self, text: str) -> float:
        """感情的強度を計算"""
        intense_words = ['すごい', 'ヤバい', '衝撃', '驚愕', '緊急', '重要', '必見']
        count = sum(1 for word in intense_words if word in text)
        return min(1.0, count / 3.0)  # 0-1の範囲で正規化
    
    def _detect_content_type(self, text: str) -> str:
        """コンテンツタイプを検出"""
        if any(word in text for word in ['解説', '方法', 'やり方', 'コツ']):
            return 'tutorial'
        elif any(word in text for word in ['レビュー', '評価', '比較']):
            return 'review'
        elif any(word in text for word in ['速報', 'ニュース', '最新']):
            return 'news'
        else:
            return 'general'
    
    def _analyze_demographic(self, text: str) -> str:
        """ターゲット層を分析"""
        # 簡易的な実装
        return 'general'
    
    def _detect_urgency(self, text: str) -> float:
        """緊急性レベルを検出"""
        urgent_words = ['今すぐ', '急げ', '限定', '終了', '最後']
        count = sum(1 for word in urgent_words if word in text)
        return min(1.0, count / 2.0)
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """キーフレーズを抽出"""
        # 簡易的な実装
        words = text.split()
        return words[:10]  # 最初の10単語
    
    def _get_strategic_font(self, size: int, style: str, bold: bool = False) -> ImageFont.FreeTypeFont:
        """戦略的フォントを取得"""
        
        font_paths = {
            'bold_condensed': [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "C:/Windows/Fonts/msgothic.ttc"
            ],
            'elegant': [
                "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
                "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
                "C:/Windows/Fonts/msmincho.ttc"
            ],
            'professional': [
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "C:/Windows/Fonts/meiryo.ttc"
            ]
        }
        
        target_paths = font_paths.get(style, font_paths['professional'])
        
        for font_path in target_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        return ImageFont.load_default()
    
    def _calculate_optimal_font_size(self, text: str, style: str) -> int:
        """最適なフォントサイズを計算"""
        base_size = 72
        text_length = len(text)
        
        if text_length > 30:
            return max(48, base_size - (text_length - 30) * 2)
        elif text_length < 15:
            return min(96, base_size + (15 - text_length) * 2)
        
        return base_size
    
    def _calculate_text_position(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
                                text_type: str, strategy: Dict) -> Tuple[int, int]:
        """テキスト位置を計算"""
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if text_type == 'title':
            # タイトルは上部中央寄り
            x = (self.width - text_width) // 2
            y = self.height // 3
        else:  # subtitle
            # サブタイトルは下部
            x = (self.width - text_width) // 2
            y = self.height - 150
        
        return (x, y)
    
    def _draw_text_with_effects(self, draw: ImageDraw.Draw, text: str, pos: Tuple[int, int], 
                               font: ImageFont.FreeTypeFont, strategy: Dict, text_type: str):
        """エフェクト付きテキストを描画"""
        
        x, y = pos
        colors = strategy['colors']
        
        # 影効果
        shadow_offset = 4 if text_type == 'title' else 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill='#000000')
        
        # アウトライン
        outline_width = 2 if text_type == 'title' else 1
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill='#000000')
        
        # メインテキスト
        main_color = colors[0] if text_type == 'title' else '#FFFFFF'
        draw.text((x, y), text, font=font, fill=main_color)
    
    def _create_dramatic_gradient(self, draw: ImageDraw.Draw, colors: List[str]):
        """劇的なグラデーション背景"""
        for y in range(self.height):
            ratio = y / self.height
            if ratio < 0.3:
                color = colors[0]
            elif ratio < 0.7:
                color = colors[1]
            else:
                color = colors[2]
            draw.line([(0, y), (self.width, y)], fill=color)
    
    def _create_mystery_background(self, draw: ImageDraw.Draw, colors: List[str]):
        """ミステリアスな背景"""
        # 放射状グラデーション風
        center_x, center_y = self.width // 2, self.height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.height):
            for x in range(0, self.width, 4):  # 4ピクセルごとに処理して高速化
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = distance / max_radius
                
                if ratio < 0.3:
                    color = colors[0]
                elif ratio < 0.7:
                    color = colors[1]
                else:
                    color = colors[2]
                    
                draw.line([(x, y), (x + 3, y)], fill=color)
    
    def _create_clean_gradient(self, draw: ImageDraw.Draw, colors: List[str]):
        """クリーンなグラデーション"""
        for y in range(self.height):
            ratio = y / self.height
            # 滑らかなグラデーション
            if ratio < 0.5:
                color = colors[0]
            else:
                color = colors[1]
            draw.line([(0, y), (self.width, y)], fill=color)
    
    def _add_light_rays(self, draw: ImageDraw.Draw, color: str):
        """光線エフェクト"""
        center_x, center_y = self.width // 2, 100
        for angle in range(0, 360, 45):
            end_x = center_x + 1000 * math.cos(math.radians(angle))
            end_y = center_y + 1000 * math.sin(math.radians(angle))
            draw.line([(center_x, center_y), (end_x, end_y)], fill=color, width=2)
    
    def _add_particle_effects(self, draw: ImageDraw.Draw, color: str):
        """パーティクルエフェクト"""
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 6)
            draw.ellipse([(x, y), (x + size, y + size)], fill=color)
    
    def _add_subtle_pattern(self, draw: ImageDraw.Draw, color: str):
        """サブトルなパターン"""
        for x in range(0, self.width, 100):
            for y in range(0, self.height, 100):
                draw.rectangle([(x, y), (x + 2, y + 2)], fill=color)
    
    def _apply_glow_effect(self, img: Image.Image, color: str) -> Image.Image:
        """グロー効果"""
        # 簡易的なグロー効果
        blurred = img.filter(ImageFilter.GaussianBlur(radius=5))
        return Image.blend(img, blurred, 0.3)
    
    def _apply_drop_shadow(self, img: Image.Image) -> Image.Image:
        """ドロップシャドウ"""
        return img  # 簡易実装
    
    def _apply_blur_reveal(self, img: Image.Image) -> Image.Image:
        """ブラー・リビール効果"""
        return img  # 簡易実装
    
    def _apply_highlight_effect(self, img: Image.Image, color: str) -> Image.Image:
        """ハイライト効果"""
        return img  # 簡易実装
    
    def _apply_premium_border(self, img: Image.Image, color: str) -> Image.Image:
        """プレミアムボーダー"""
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (self.width - 1, self.height - 1)], outline=color, width=8)
        return img