"""
[DEPRECATED] このモジュールは廃止されました

現在のシステムでは画像の自動生成は行わず、
DALL-E 3やChatGPT用のプロンプトを生成する方式に変更されました。

代わりに modules/image_prompt_generator.py を使用してください。

---

Stable Diffusionを使用したYouTubeサムネイル生成モジュール（旧バージョン）
参考のために残していますが、使用は推奨されません。
"""

import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import os

logger = logging.getLogger(__name__)


class StableDiffusionThumbnailCreator:
    """Stable Diffusionを使用したサムネイル生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.width = 1280
        self.height = 720
        
        # Stable Diffusion API設定（複数のプロバイダーをサポート）
        self.api_providers = {
            'replicate': {
                'url': 'https://api.replicate.com/v1/predictions',
                'model': 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b',
                'requires_key': True
            },
            'huggingface': {
                'url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
                'requires_key': True
            },
            'local': {
                'url': 'http://localhost:7860/api/predict',  # Gradio API
                'requires_key': False
            }
        }
        
        # 使用するプロバイダー
        self.provider = config.get('sd_provider', 'replicate')
        self.api_key = config.get('sd_api_key', os.environ.get('STABLE_DIFFUSION_API_KEY'))
        
        # 日本語対応プロンプトテンプレート
        self.prompt_templates = {
            'impact': {
                'style': 'dramatic lighting, high contrast, vibrant colors, cinematic, professional photography',
                'elements': 'eye-catching, attention-grabbing, bold composition',
                'mood': 'urgent, exciting, dynamic'
            },
            'curiosity': {
                'style': 'mysterious atmosphere, soft lighting, depth of field, artistic',
                'elements': 'intriguing composition, hidden details, question marks',
                'mood': 'mysterious, thought-provoking, enigmatic'
            },
            'professional': {
                'style': 'clean design, modern, minimalist, professional studio lighting',
                'elements': 'trustworthy, expert, high quality',
                'mood': 'confident, reliable, authoritative'
            }
        }
    
    def create_viral_thumbnails(self, title: str, transcript_data: Dict, output_dir: Path) -> List[Dict]:
        """3つの戦略的サムネイルを生成"""
        
        logger.info("🎨 Stable Diffusion サムネイル生成開始...")
        
        # コンテンツ分析
        content_keywords = self._extract_keywords(title, transcript_data)
        
        # 3つの戦略
        strategies = [
            {
                'name': 'インパクト重視',
                'type': 'impact',
                'description': '視覚的インパクトで注目を集める'
            },
            {
                'name': '好奇心喚起',
                'type': 'curiosity',
                'description': '謎や秘密を示唆して興味を引く'
            },
            {
                'name': 'プロフェッショナル',
                'type': 'professional',
                'description': '信頼性と専門性をアピール'
            }
        ]
        
        results = []
        
        for i, strategy in enumerate(strategies, 1):
            try:
                # プロンプト生成
                prompt = self._generate_prompt(title, content_keywords, strategy['type'])
                
                # Stable Diffusionで画像生成
                base_image_path = self._generate_with_stable_diffusion(prompt, output_dir, f"base_{i}")
                
                if base_image_path:
                    # Pillowで日本語テキストとエフェクトを追加
                    final_path = output_dir / f"thumbnail_sd_{i}.png"
                    self._enhance_with_text(base_image_path, title, strategy, final_path)
                    
                    results.append({
                        'variant': i,
                        'strategy': strategy['name'],
                        'description': strategy['description'],
                        'path': str(final_path),
                        'base_image': str(base_image_path),
                        'prompt': prompt
                    })
                    
                    logger.info(f"✓ バリエーション{i} 生成完了: {strategy['name']}")
                
            except Exception as e:
                logger.error(f"サムネイル生成エラー (バリエーション{i}): {e}")
                # フォールバック：Pillowのみで生成
                fallback_path = self._create_fallback_thumbnail(title, strategy, output_dir, i)
                results.append({
                    'variant': i,
                    'strategy': strategy['name'],
                    'description': strategy['description'],
                    'path': str(fallback_path),
                    'fallback': True
                })
        
        return results
    
    def _extract_keywords(self, title: str, transcript_data: Dict) -> List[str]:
        """コンテンツからキーワードを抽出"""
        text = f"{title} {transcript_data.get('text', '')}"
        
        # 簡易的なキーワード抽出
        important_words = ['AI', 'YouTube', 'ブログ', 'SNS', '自動', '生成', '動画', 'システム']
        keywords = [word for word in important_words if word in text]
        
        return keywords[:5]  # 最大5個
    
    def _generate_prompt(self, title: str, keywords: List[str], strategy_type: str) -> str:
        """Stable Diffusion用のプロンプトを生成"""
        
        template = self.prompt_templates[strategy_type]
        
        # 基本的な要素
        base_prompt = f"YouTube thumbnail design, 16:9 aspect ratio, high quality, 4k"
        
        # トピックに基づくビジュアル要素
        topic_visuals = self._get_topic_visuals(title, keywords)
        
        # 戦略に基づくスタイル
        style_prompt = f"{template['style']}, {template['elements']}, {template['mood']}"
        
        # 完全なプロンプト
        full_prompt = f"{base_prompt}, {topic_visuals}, {style_prompt}"
        
        # ネガティブプロンプト（避けるべき要素）
        negative_prompt = "text, words, letters, watermark, signature, blurry, low quality, distorted"
        
        return full_prompt
    
    def _get_topic_visuals(self, title: str, keywords: List[str]) -> str:
        """トピックに基づくビジュアル要素を決定"""
        
        visuals = []
        
        # キーワードに基づくビジュアル要素
        visual_mapping = {
            'AI': 'futuristic technology, neural networks, digital brain',
            'YouTube': 'video player interface, play button, streaming',
            'ブログ': 'laptop computer, writing, content creation',
            'SNS': 'social media icons, network connections, smartphone',
            '自動': 'automation, gears, robotic process',
            '生成': 'creation process, magical sparkles, transformation',
            '動画': 'video camera, film reel, multimedia',
            'システム': 'flowchart, connected nodes, systematic design'
        }
        
        for keyword in keywords:
            if keyword in visual_mapping:
                visuals.append(visual_mapping[keyword])
        
        return ', '.join(visuals) if visuals else 'modern technology, digital innovation'
    
    def _generate_with_stable_diffusion(self, prompt: str, output_dir: Path, filename: str) -> Optional[Path]:
        """Stable Diffusionで画像を生成"""
        
        provider_info = self.api_providers[self.provider]
        
        try:
            if self.provider == 'replicate':
                return self._generate_replicate(prompt, output_dir, filename, provider_info)
            elif self.provider == 'huggingface':
                return self._generate_huggingface(prompt, output_dir, filename, provider_info)
            elif self.provider == 'local':
                return self._generate_local(prompt, output_dir, filename, provider_info)
            else:
                logger.error(f"未対応のプロバイダー: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Stable Diffusion生成エラー: {e}")
            return None
    
    def _generate_replicate(self, prompt: str, output_dir: Path, filename: str, provider_info: Dict) -> Optional[Path]:
        """Replicate APIを使用して生成"""
        
        if not self.api_key:
            logger.error("Replicate APIキーが設定されていません")
            return None
        
        headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'version': provider_info['model'],
            'input': {
                'prompt': prompt,
                'width': 1024,
                'height': 576,
                'num_outputs': 1,
                'scheduler': 'K_EULER',
                'guidance_scale': 7.5,
                'num_inference_steps': 50
            }
        }
        
        # 予測を作成
        response = requests.post(provider_info['url'], json=data, headers=headers)
        
        if response.status_code != 201:
            logger.error(f"Replicate API エラー: {response.text}")
            return None
        
        prediction = response.json()
        prediction_id = prediction['id']
        
        # 結果を待つ
        while True:
            response = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers=headers
            )
            prediction = response.json()
            
            if prediction['status'] == 'succeeded':
                image_url = prediction['output'][0]
                break
            elif prediction['status'] == 'failed':
                logger.error(f"生成失敗: {prediction.get('error')}")
                return None
            
            time.sleep(2)
        
        # 画像をダウンロード
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        
        # リサイズして保存
        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        output_path = output_dir / f"{filename}.png"
        image.save(output_path)
        
        return output_path
    
    def _generate_huggingface(self, prompt: str, output_dir: Path, filename: str, provider_info: Dict) -> Optional[Path]:
        """Hugging Face Inference APIを使用して生成"""
        
        if not self.api_key:
            logger.error("Hugging Face APIキーが設定されていません")
            return None
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        response = requests.post(
            provider_info['url'],
            headers=headers,
            json={'inputs': prompt}
        )
        
        if response.status_code != 200:
            logger.error(f"Hugging Face API エラー: {response.text}")
            return None
        
        image = Image.open(io.BytesIO(response.content))
        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        output_path = output_dir / f"{filename}.png"
        image.save(output_path)
        
        return output_path
    
    def _generate_local(self, prompt: str, output_dir: Path, filename: str, provider_info: Dict) -> Optional[Path]:
        """ローカルのStable Diffusion WebUIを使用"""
        
        # Gradio API経由でローカルのStable Diffusionにアクセス
        data = {
            'fn_index': 0,  # txt2imgのインデックス
            'data': [
                prompt,  # positive prompt
                "text, words, letters, watermark",  # negative prompt
                "DPM++ 2M Karras",  # sampler
                20,  # steps
                7.5,  # cfg scale
                self.width,  # width
                self.height,  # height
                -1,  # seed
                1,  # batch size
            ]
        }
        
        try:
            response = requests.post(provider_info['url'], json=data)
            result = response.json()
            
            # Base64エンコードされた画像をデコード
            import base64
            image_data = result['data'][0].split(',')[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            
            output_path = output_dir / f"{filename}.png"
            image.save(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"ローカルSD接続エラー: {e}")
            return None
    
    def _enhance_with_text(self, base_image_path: Path, title: str, strategy: Dict, output_path: Path):
        """生成された画像に日本語テキストとエフェクトを追加"""
        
        # ベース画像を開く
        img = Image.open(base_image_path)
        draw = ImageDraw.Draw(img)
        
        # 半透明オーバーレイ
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 戦略に基づくテキストスタイル
        if strategy['type'] == 'impact':
            # インパクト重視：大きく太いテキスト
            self._add_impact_text(overlay_draw, title, img.size)
        elif strategy['type'] == 'curiosity':
            # 好奇心喚起：ミステリアスなテキスト
            self._add_curiosity_text(overlay_draw, title, img.size)
        else:
            # プロフェッショナル：クリーンなテキスト
            self._add_professional_text(overlay_draw, title, img.size)
        
        # オーバーレイを合成
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        # エフェクト追加
        img = self._apply_final_effects(img, strategy['type'])
        
        # 保存
        img.convert('RGB').save(output_path, 'PNG', quality=95, optimize=True)
    
    def _add_impact_text(self, draw: ImageDraw.Draw, title: str, size: Tuple[int, int]):
        """インパクトのあるテキストを追加"""
        
        # フォント設定
        font_size = 80
        font = self._get_font(font_size, bold=True)
        
        # テキストの配置
        text_lines = self._wrap_text(title, font, size[0] - 100)
        
        y_offset = size[1] // 3
        
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            
            # アウトライン効果
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y_offset + dy), line, font=font, fill=(0, 0, 0, 200))
            
            # メインテキスト（白）
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
            
            y_offset += bbox[3] - bbox[1] + 20
        
        # 緊急性を示すバッジ
        badge_text = "【必見】"
        badge_font = self._get_font(40, bold=True)
        badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = badge_bbox[2] - badge_bbox[0]
        badge_height = badge_bbox[3] - badge_bbox[1]
        
        # 赤いバッジ背景
        badge_x = size[0] - badge_width - 50
        badge_y = 50
        draw.rectangle(
            [(badge_x - 20, badge_y - 10), (badge_x + badge_width + 20, badge_y + badge_height + 10)],
            fill=(255, 0, 0, 220)
        )
        draw.text((badge_x, badge_y), badge_text, font=badge_font, fill=(255, 255, 255, 255))
    
    def _add_curiosity_text(self, draw: ImageDraw.Draw, title: str, size: Tuple[int, int]):
        """好奇心を刺激するテキストを追加"""
        
        font_size = 60
        font = self._get_font(font_size, bold=False)
        
        # 謎めいたプレフィックス
        prefix = "知らないと損する..."
        prefix_font = self._get_font(40, bold=False)
        
        # プレフィックスを上部に
        prefix_bbox = draw.textbbox((0, 0), prefix, font=prefix_font)
        prefix_x = (size[0] - (prefix_bbox[2] - prefix_bbox[0])) // 2
        draw.text((prefix_x, 100), prefix, font=prefix_font, fill=(255, 255, 0, 200))
        
        # メインタイトル
        text_lines = self._wrap_text(title, font, size[0] - 100)
        y_offset = size[1] // 2 - len(text_lines) * 30
        
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            
            # グラデーション風の影
            for i in range(5):
                alpha = 150 - i * 30
                draw.text((x + i, y_offset + i), line, font=font, fill=(0, 0, 0, alpha))
            
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += bbox[3] - bbox[1] + 15
        
        # 疑問符アイコン
        question_font = self._get_font(100, bold=True)
        draw.text((50, size[1] - 150), "?", font=question_font, fill=(255, 255, 0, 180))
        draw.text((size[0] - 150, 50), "?", font=question_font, fill=(255, 255, 0, 180))
    
    def _add_professional_text(self, draw: ImageDraw.Draw, title: str, size: Tuple[int, int]):
        """プロフェッショナルなテキストを追加"""
        
        # クリーンなフォント
        font_size = 55
        font = self._get_font(font_size, bold=True)
        
        # 信頼性バッジ
        badge_text = "専門家解説"
        badge_font = self._get_font(35, bold=False)
        badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        
        # バッジ背景（半透明青）
        badge_x = 50
        badge_y = 50
        draw.rectangle(
            [(badge_x, badge_y), (badge_x + badge_bbox[2] - badge_bbox[0] + 40, badge_y + badge_bbox[3] - badge_bbox[1] + 20)],
            fill=(0, 100, 200, 180)
        )
        draw.text((badge_x + 20, badge_y + 10), badge_text, font=badge_font, fill=(255, 255, 255, 255))
        
        # メインタイトル（下部配置）
        text_lines = self._wrap_text(title, font, size[0] - 100)
        y_offset = size[1] - (len(text_lines) * 70) - 100
        
        # 半透明の背景ボックス
        text_bg_height = len(text_lines) * 70 + 40
        draw.rectangle(
            [(0, y_offset - 20), (size[0], y_offset + text_bg_height)],
            fill=(0, 0, 0, 150)
        )
        
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += 70
    
    def _apply_final_effects(self, img: Image.Image, strategy_type: str) -> Image.Image:
        """最終的なエフェクトを適用"""
        
        if strategy_type == 'impact':
            # コントラスト強化
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            
            # 彩度アップ
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            
        elif strategy_type == 'curiosity':
            # 軽いぼかし効果をエッジに
            # ビネット効果を追加
            img = self._add_vignette(img)
            
        else:  # professional
            # シャープネス強化
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
        
        return img
    
    def _add_vignette(self, img: Image.Image) -> Image.Image:
        """ビネット効果を追加"""
        # マスクを作成
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # 楕円グラデーション
        for i in range(min(img.size) // 2):
            alpha = int(255 * (1 - i / (min(img.size) // 2)))
            mask_draw.ellipse(
                [(i, i), (img.size[0] - i, img.size[1] - i)],
                fill=alpha
            )
        
        # ビネット適用
        vignette = Image.new('RGBA', img.size, (0, 0, 0, 0))
        vignette.paste((0, 0, 0, 100), mask=ImageOps.invert(mask))
        
        return Image.alpha_composite(img.convert('RGBA'), vignette)
    
    def _create_fallback_thumbnail(self, title: str, strategy: Dict, output_dir: Path, variant: int) -> Path:
        """Stable Diffusionが使えない場合のフォールバック"""
        
        # Pillowのみでサムネイル生成
        img = Image.new('RGB', (self.width, self.height), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # グラデーション背景
        if strategy['type'] == 'impact':
            colors = [(255, 0, 100), (255, 100, 0)]
        elif strategy['type'] == 'curiosity':
            colors = [(100, 0, 255), (255, 0, 255)]
        else:
            colors = [(0, 100, 255), (0, 255, 100)]
        
        # 縦グラデーション
        for y in range(self.height):
            ratio = y / self.height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # テキスト追加
        font = self._get_font(60, bold=True)
        text_lines = self._wrap_text(title, font, self.width - 100)
        
        y_offset = (self.height - len(text_lines) * 80) // 2
        
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # アウトライン
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y_offset + dy), line, font=font, fill=(0, 0, 0))
            
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255))
            y_offset += 80
        
        output_path = output_dir / f"thumbnail_fallback_{variant}.png"
        img.save(output_path)
        
        return output_path
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """フォントを取得"""
        font_paths = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if bold else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "C:/Windows/Fonts/msgothic.ttc"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """テキストを折り返し"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


class StableDiffusionSetup:
    """Stable Diffusion環境セットアップヘルパー"""
    
    @staticmethod
    def check_environment() -> Dict[str, bool]:
        """環境チェック"""
        checks = {
            'replicate_api': bool(os.environ.get('REPLICATE_API_TOKEN')),
            'huggingface_api': bool(os.environ.get('HUGGINGFACE_API_TOKEN')),
            'local_sd': StableDiffusionSetup._check_local_sd(),
            'gpu_available': StableDiffusionSetup._check_gpu()
        }
        return checks
    
    @staticmethod
    def _check_local_sd() -> bool:
        """ローカルのStable Diffusion WebUIをチェック"""
        try:
            response = requests.get('http://localhost:7860/api/v1/options', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def _check_gpu() -> bool:
        """GPU利用可能性をチェック"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    @staticmethod
    def setup_guide() -> str:
        """セットアップガイドを表示"""
        guide = """
# Stable Diffusion セットアップガイド

## オプション1: Replicate (推奨・簡単)
1. https://replicate.com でアカウント作成
2. APIトークンを取得
3. 環境変数を設定:
   export REPLICATE_API_TOKEN="your_token_here"

## オプション2: Hugging Face
1. https://huggingface.co でアカウント作成
2. APIトークンを取得
3. 環境変数を設定:
   export HUGGINGFACE_API_TOKEN="your_token_here"

## オプション3: ローカル実行（無料・要GPU）
1. Stable Diffusion WebUIをインストール:
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
2. 起動:
   python launch.py --api
3. http://localhost:7860 で確認

設定ファイル（config.yaml）に追加:
```yaml
thumbnail:
  sd_provider: replicate  # または huggingface, local
  sd_api_key: ${REPLICATE_API_TOKEN}
```
"""
        return guide