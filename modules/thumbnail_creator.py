"""
サムネイル画像生成モジュール
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)


class ThumbnailCreator:
    """サムネイル生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.width = config.get('width', 1280)
        self.height = config.get('height', 720)
        self.bg_color = config.get('background_color', '#1a1a2e')
        self.text_color = config.get('text_color', '#ffffff')
        self.accent_color = config.get('accent_color', '#f39c12')
        self.font_size_title = config.get('font_size_title', 80)
        self.font_size_subtitle = config.get('font_size_subtitle', 40)
        
        # フォント設定
        self.title_font = self._load_font(self.font_size_title, bold=True)
        self.subtitle_font = self._load_font(self.font_size_subtitle, bold=False)
    
    def create(self, title: str, subtitle: str, output_path: Path) -> Path:
        """サムネイル画像を生成"""
        
        logger.info("サムネイル生成中...")
        
        # 画像作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # 背景デザイン追加
        self._add_background_design(draw)
        
        # テキスト配置
        self._add_text(draw, title, subtitle)
        
        # 装飾追加
        self._add_decorations(draw)
        
        # 保存
        img.save(output_path, quality=95)
        logger.info(f"✓ サムネイル保存: {output_path}")
        
        return output_path
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """フォントをロード"""
        
        # 日本語フォントパスのリスト
        font_paths = [
            # macOS
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # Windows
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/Arial.ttf",
        ]
        
        # 利用可能なフォントを探す
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # フォールバック
        logger.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")
        return ImageFont.load_default()
    
    def _add_background_design(self, draw: ImageDraw.Draw):
        """背景デザインを追加"""
        
        # グラデーション効果
        for i in range(self.height):
            # 上から下へのグラデーション
            ratio = i / self.height
            r = int(int(self.bg_color[1:3], 16) * (1 - ratio * 0.3))
            g = int(int(self.bg_color[3:5], 16) * (1 - ratio * 0.3))
            b = int(int(self.bg_color[5:7], 16) * (1 - ratio * 0.3))
            color = f'#{r:02x}{g:02x}{b:02x}'
            draw.line([(0, i), (self.width, i)], fill=color)
        
        # グリッドパターン（薄く）
        grid_color = self._adjust_brightness(self.bg_color, 1.2)
        for x in range(0, self.width, 50):
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)
        for y in range(0, self.height, 50):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)
    
    def _add_text(self, draw: ImageDraw.Draw, title: str, subtitle: str):
        """テキストを配置"""
        
        # タイトル位置計算
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (self.width - title_width) // 2
        title_y = (self.height - title_height) // 2 - 60
        
        # サブタイトル位置計算
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=self.subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.width - subtitle_width) // 2
        subtitle_y = title_y + title_height + 40
        
        # 影効果
        shadow_offset = 4
        shadow_color = '#000000'
        
        # タイトル描画（影）
        draw.text(
            (title_x + shadow_offset, title_y + shadow_offset),
            title,
            font=self.title_font,
            fill=shadow_color
        )
        
        # タイトル描画（本体）
        draw.text(
            (title_x, title_y),
            title,
            font=self.title_font,
            fill=self.text_color
        )
        
        # サブタイトル描画（影）
        draw.text(
            (subtitle_x + shadow_offset // 2, subtitle_y + shadow_offset // 2),
            subtitle,
            font=self.subtitle_font,
            fill=shadow_color
        )
        
        # サブタイトル描画（本体）
        draw.text(
            (subtitle_x, subtitle_y),
            subtitle,
            font=self.subtitle_font,
            fill=self.accent_color
        )
    
    def _add_decorations(self, draw: ImageDraw.Draw):
        """装飾要素を追加"""
        
        # 左右のアクセントバー
        bar_width = 8
        bar_margin = 50
        
        # 左バー
        draw.rectangle(
            [(bar_margin, 150), (bar_margin + bar_width, self.height - 150)],
            fill=self.accent_color
        )
        
        # 右バー
        draw.rectangle(
            [(self.width - bar_margin - bar_width, 150), (self.width - bar_margin, self.height - 150)],
            fill=self.accent_color
        )
        
        # 上下のライン
        line_height = 3
        draw.rectangle(
            [(100, 100), (self.width - 100, 100 + line_height)],
            fill=self._adjust_brightness(self.accent_color, 0.7)
        )
        draw.rectangle(
            [(100, self.height - 100 - line_height), (self.width - 100, self.height - 100)],
            fill=self._adjust_brightness(self.accent_color, 0.7)
        )
        
        # コーナー装飾
        corner_size = 50
        corner_width = 5
        
        # 左上
        draw.line([(0, corner_size), (0, 0), (corner_size, 0)], fill=self.accent_color, width=corner_width)
        
        # 右上
        draw.line([(self.width - corner_size, 0), (self.width, 0), (self.width, corner_size)], fill=self.accent_color, width=corner_width)
        
        # 左下
        draw.line([(0, self.height - corner_size), (0, self.height), (corner_size, self.height)], fill=self.accent_color, width=corner_width)
        
        # 右下
        draw.line([(self.width - corner_size, self.height), (self.width, self.height), (self.width, self.height - corner_size)], fill=self.accent_color, width=corner_width)
    
    def _adjust_brightness(self, hex_color: str, factor: float) -> str:
        """色の明度を調整"""
        # HEXをRGBに変換
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 明度調整
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        return f'#{r:02x}{g:02x}{b:02x}'


class ThumbnailTemplate:
    """サムネイルテンプレート管理クラス"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Path]:
        """利用可能なテンプレートをロード"""
        templates = {}
        if self.template_dir.exists():
            for template_file in self.template_dir.glob("*.png"):
                templates[template_file.stem] = template_file
        return templates
    
    def apply_template(self, template_name: str, title: str, subtitle: str, output_path: Path) -> Path:
        """テンプレートを適用してサムネイルを生成"""
        
        if template_name not in self.templates:
            raise ValueError(f"テンプレート '{template_name}' が見つかりません")
        
        # テンプレート画像を開く
        template_img = Image.open(self.templates[template_name])
        draw = ImageDraw.Draw(template_img)
        
        # テキストを追加（テンプレートに応じて位置調整）
        # TODO: テンプレートごとの設定ファイルから位置情報を読み込む
        
        template_img.save(output_path, quality=95)
        return output_path