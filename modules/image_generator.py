"""
ブログ用画像生成モジュール
アイキャッチ画像とセクション画像を自動生成
"""

import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
import textwrap
import os

logger = logging.getLogger(__name__)


class BlogImageGenerator:
    """ブログ用画像生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.default_size = (1200, 630)  # OGP標準サイズ
        self.section_size = (800, 400)   # セクション画像サイズ
        self.colors = {
            'primary': config.get('primary_color', '#2c3e50'),
            'secondary': config.get('secondary_color', '#3498db'),
            'accent': config.get('accent_color', '#e74c3c'),
            'text': config.get('text_color', '#ffffff'),
            'background': config.get('background_color', '#1a1a2e'),
            'overlay': config.get('overlay_color', 'rgba(0,0,0,0.6)')
        }
        
    def generate_featured_image(self, title: str, subtitle: str, output_path: Path) -> Path:
        """アイキャッチ画像を生成"""
        
        logger.info("アイキャッチ画像生成開始...")
        
        # 画像作成
        img = Image.new('RGB', self.default_size, self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # グラデーション背景
        self._add_gradient_background(img, draw)
        
        # デザイン要素を追加
        self._add_design_elements(img, draw)
        
        # タイトルを描画
        self._draw_centered_text(
            draw, 
            title, 
            (self.default_size[0] // 2, self.default_size[1] // 2 - 50),
            font_size=60,
            max_width=int(self.default_size[0] * 0.8)
        )
        
        # サブタイトルを描画
        if subtitle:
            self._draw_centered_text(
                draw,
                subtitle,
                (self.default_size[0] // 2, self.default_size[1] // 2 + 80),
                font_size=30,
                color=self.colors['secondary'],
                max_width=int(self.default_size[0] * 0.7)
            )
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, quality=95, optimize=True)
        logger.info(f"✓ アイキャッチ画像生成: {output_path}")
        
        return output_path
    
    def generate_section_images(self, sections: List[Dict], output_dir: Path) -> Dict[str, Path]:
        """各セクション用の画像を生成"""
        
        logger.info("セクション画像生成開始...")
        
        section_images = {}
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # セクションタイプに応じたビジュアルテーマ
        theme_map = {
            'problem': {
                'icon': '⚠️',
                'gradient': ['#e74c3c', '#c0392b'],
                'title': '課題'
            },
            'solution': {
                'icon': '💡',
                'gradient': ['#3498db', '#2980b9'],
                'title': '解決策'
            },
            'benefits': {
                'icon': '✨',
                'gradient': ['#2ecc71', '#27ae60'],
                'title': 'メリット'
            },
            'how_to': {
                'icon': '📝',
                'gradient': ['#f39c12', '#e67e22'],
                'title': '使い方'
            },
            'results': {
                'icon': '📊',
                'gradient': ['#9b59b6', '#8e44ad'],
                'title': '成果'
            }
        }
        
        for i, section in enumerate(sections):
            section_type = section.get('type', 'default')
            theme = theme_map.get(section_type, {
                'icon': '📌',
                'gradient': [self.colors['primary'], self.colors['secondary']],
                'title': 'セクション'
            })
            
            # 画像生成
            img = self._create_section_image(
                section['title'],
                theme['icon'],
                theme['gradient'],
                theme['title']
            )
            
            # 保存
            filename = f"section_{i+1}_{section_type}.png"
            img_path = output_dir / filename
            img.save(img_path, quality=90, optimize=True)
            
            section_images[section['title']] = img_path
            logger.info(f"✓ セクション画像生成: {filename}")
        
        return section_images
    
    def _create_section_image(self, title: str, icon: str, gradient: List[str], label: str) -> Image:
        """セクション画像を作成"""
        
        img = Image.new('RGB', self.section_size, self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # グラデーション背景（カスタムカラー）
        self._add_gradient_background(img, draw, gradient)
        
        # 半透明オーバーレイ
        overlay = Image.new('RGBA', self.section_size, (0, 0, 0, 100))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # アイコンを描画（大きく）
        self._draw_centered_text(
            draw,
            icon,
            (self.section_size[0] // 2, self.section_size[1] // 2 - 80),
            font_size=80
        )
        
        # ラベル
        self._draw_centered_text(
            draw,
            label,
            (self.section_size[0] // 2, self.section_size[1] // 2 - 20),
            font_size=24,
            color='#ffffff'
        )
        
        # タイトル
        self._draw_centered_text(
            draw,
            title,
            (self.section_size[0] // 2, self.section_size[1] // 2 + 40),
            font_size=36,
            max_width=int(self.section_size[0] * 0.8)
        )
        
        return img
    
    def _add_gradient_background(self, img: Image, draw: ImageDraw, colors: Optional[List[str]] = None):
        """グラデーション背景を追加"""
        
        if colors is None:
            colors = [self.colors['background'], self.colors['primary']]
        
        # 垂直グラデーション
        for i in range(img.height):
            ratio = i / img.height
            r1, g1, b1 = self._hex_to_rgb(colors[0])
            r2, g2, b2 = self._hex_to_rgb(colors[1])
            
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            
            draw.line([(0, i), (img.width, i)], fill=(r, g, b))
    
    def _add_design_elements(self, img: Image, draw: ImageDraw):
        """デザイン要素を追加"""
        
        # 装飾的な円
        for i in range(3):
            x = img.width * (0.2 + i * 0.3)
            y = img.height * (0.2 + i * 0.2)
            radius = 50 + i * 20
            color = (*self._hex_to_rgb(self.colors['accent']), 50)  # 半透明
            
            # 円を描画
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill=color
            )
    
    def _draw_centered_text(self, draw: ImageDraw, text: str, position: Tuple[int, int], 
                          font_size: int = 40, color: Optional[str] = None, 
                          max_width: Optional[int] = None):
        """中央揃えでテキストを描画"""
        
        if color is None:
            color = self.colors['text']
        
        # フォント設定
        try:
            # 日本語フォントを試す
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ]
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # テキストを折り返し
        if max_width:
            # 簡易的な折り返し処理
            lines = []
            words = text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > max_width:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)
                else:
                    current_line = test_line
            
            if current_line:
                lines.append(current_line)
        else:
            lines = [text]
        
        # 各行を描画
        y_offset = position[1] - (len(lines) - 1) * font_size // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = position[0] - text_width // 2
            text_y = y_offset + i * font_size
            
            # 影を追加
            shadow_offset = 2
            draw.text(
                (text_x + shadow_offset, text_y + shadow_offset), 
                line, 
                font=font, 
                fill=(0, 0, 0, 128)
            )
            
            # テキストを描画
            draw.text((text_x, text_y), line, font=font, fill=color)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """16進数カラーをRGBに変換"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class ImageOptimizer:
    """画像最適化クラス"""
    
    @staticmethod
    def optimize_for_web(image_path: Path, max_width: int = 1200) -> Path:
        """Web用に画像を最適化"""
        
        img = Image.open(image_path)
        
        # リサイズ（必要な場合）
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # 最適化して保存
        img.save(image_path, quality=85, optimize=True)
        
        return image_path