#!/usr/bin/env python3
"""
Runware API統合画像生成モジュール
YouTubeサムネイル、ブログアイキャッチ、セクション画像を統合的に生成
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
import websockets
import aiohttp
import requests
import logging
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class RunwareImageGenerator:
    """Runware APIを使用した高速・低コスト画像生成"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('runware', {}).get('api_key', '')
        self.ws_url = "wss://ws-api.runware.ai/v1"
        self.rest_url = "https://api.runware.ai/v1"
        self.logger = logging.getLogger(__name__)
        
        # YouTube最適化設定
        self.youtube_config = {
            'width': 1280,
            'height': 720,
            'models': {
                'impact': 'civitai:25694@143906',      # 高インパクトスタイル
                'curiosity': 'civitai:4384@128713',    # ミステリアススタイル  
                'authority': 'civitai:133005@148204'   # プロフェッショナルスタイル
            }
        }
        
        # ブログ画像設定
        self.blog_config = {
            'featured_width': 1200,
            'featured_height': 630,  # OGP最適化
            'section_width': 800,
            'section_height': 450,
            'models': {
                'featured': 'civitai:25694@143906',   # アイキャッチ用
                'section': 'civitai:4201@130072'      # セクション用
            }
        }
    
    async def authenticate_websocket(self, websocket):
        """WebSocket認証"""
        auth_message = [{
            "taskType": "authentication",
            "apiKey": self.api_key
        }]
        await websocket.send(json.dumps(auth_message))
        
        # 認証結果を待機
        response = await websocket.recv()
        result = json.loads(response)
        
        # 認証結果を確認
        if isinstance(result, list) and len(result) > 0:
            auth_data = result[0].get('data', [])
            if isinstance(auth_data, list) and len(auth_data) > 0:
                if auth_data[0].get('authenticated') == True:
                    self.logger.info("Runware API認証成功")
                    return
        
        raise Exception("Runware API認証失敗")
    
    async def generate_youtube_thumbnails(self, title: str, transcript_data: Dict, 
                                        output_dir: Path) -> List[Dict]:
        """YouTubeサムネイル3戦略生成"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 戦略別プロンプト生成
        strategies = self._create_thumbnail_strategies(title, transcript_data)
        thumbnails = []
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                await self.authenticate_websocket(websocket)
                
                # 3つの戦略を並行生成
                tasks = []
                for i, strategy in enumerate(strategies, 1):
                    task = self._generate_single_thumbnail(
                        websocket, strategy, i, output_dir
                    )
                    tasks.append(task)
                
                # 並行実行で高速化
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        self.logger.error(f"サムネイル生成エラー: {result}")
                    else:
                        thumbnails.append(result)
        
        except Exception as e:
            self.logger.error(f"Runware API接続エラー: {e}")
            # フォールバック: REST APIを使用
            thumbnails = await self._generate_thumbnails_rest_api(strategies, output_dir)
        
        return thumbnails
    
    async def generate_blog_images(self, title: str, content: Dict, 
                                 output_dir: Path) -> Dict[str, str]:
        """ブログ画像生成（アイキャッチ + セクション画像2枚）"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # アイキャッチはYouTubeサムネイルを再利用するか判定
        featured_image_path = await self._generate_or_reuse_featured_image(
            title, content, output_dir
        )
        
        # セクション画像を生成
        section_images = await self._generate_section_images(
            content, output_dir, max_images=2
        )
        
        return {
            'featured_image': featured_image_path,
            'section_images': section_images
        }
    
    def _create_thumbnail_strategies(self, title: str, transcript_data: Dict) -> List[Dict]:
        """3つのサムネイル戦略を作成"""
        # トランスクリプトから重要なキーワードを抽出
        text = transcript_data.get('text', '')
        keywords = self._extract_keywords(text)
        
        strategies = [
            {
                'name': 'インパクト・ショック型',
                'model': self.youtube_config['models']['impact'],
                'prompt': self._create_impact_prompt(title, keywords),
                'style': 'impact',
                'color_scheme': 'high_contrast'
            },
            {
                'name': 'ミステリー・好奇心型',
                'model': self.youtube_config['models']['curiosity'], 
                'prompt': self._create_curiosity_prompt(title, keywords),
                'style': 'curiosity',
                'color_scheme': 'mysterious'
            },
            {
                'name': 'エキスパート・権威型',
                'model': self.youtube_config['models']['authority'],
                'prompt': self._create_authority_prompt(title, keywords),
                'style': 'authority', 
                'color_scheme': 'professional'
            }
        ]
        
        return strategies
    
    def _create_impact_prompt(self, title: str, keywords: List[str]) -> str:
        """インパクト型プロンプト生成"""
        keyword_str = ', '.join(keywords[:3])
        
        return f"""
        YouTube thumbnail style, dramatic and shocking visual, 
        bold red and yellow colors, high contrast lighting,
        surprised expression, pointing gesture, large bold text overlay,
        professional photography, studio lighting, 4K quality,
        related to: {title}, keywords: {keyword_str},
        eye-catching, viral thumbnail design, clean composition
        """.strip()
    
    def _create_curiosity_prompt(self, title: str, keywords: List[str]) -> str:
        """好奇心型プロンプト生成"""
        keyword_str = ', '.join(keywords[:3])
        
        return f"""
        YouTube thumbnail style, mysterious and intriguing visual,
        orange and blue color scheme, question marks, hidden elements,
        curious expression, raised eyebrow, mysterious lighting,
        professional photography, soft shadows, 4K quality,
        related to: {title}, keywords: {keyword_str},
        creates curiosity, mysterious atmosphere, engaging design
        """.strip()
    
    def _create_authority_prompt(self, title: str, keywords: List[str]) -> str:
        """権威型プロンプト生成"""
        keyword_str = ', '.join(keywords[:3])
        
        return f"""
        YouTube thumbnail style, professional and trustworthy visual,
        blue and green corporate colors, clean background,
        confident expert pose, professional attire, clear lighting,
        business photography, modern design, 4K quality,
        related to: {title}, keywords: {keyword_str},
        authoritative, trustworthy, professional appearance
        """.strip()
    
    async def _generate_single_thumbnail(self, websocket, strategy: Dict, 
                                       variant_num: int, output_dir: Path) -> Dict:
        """単一サムネイル生成"""
        task_uuid = str(uuid.uuid4())
        
        # 生成リクエスト
        request = [{
            "taskType": "imageInference",
            "taskUUID": task_uuid,
            "positivePrompt": strategy['prompt'],
            "negativePrompt": "blurry, low quality, text, watermark, signature, distorted",
            "width": self.youtube_config['width'],
            "height": self.youtube_config['height'],
            "model": strategy['model'],
            "numberResults": 1,
            "steps": 25,
            "CFGScale": 7.0,
            "seed": -1
        }]
        
        await websocket.send(json.dumps(request))
        
        # 結果待機
        while True:
            response = await websocket.recv()
            result = json.loads(response)
            
            for task in result:
                if task.get('taskUUID') == task_uuid:
                    if task.get('taskType') == 'imageInference':
                        # 画像データを保存
                        image_data = task['data'][0]
                        image_url = image_data['imageURL']
                        
                        # 画像をダウンロードして保存
                        image_path = output_dir / f"thumbnail_variant_{variant_num}.png"
                        await self._download_and_save_image(image_url, image_path)
                        
                        # テキストオーバーレイを追加
                        self._add_text_overlay(image_path, strategy)
                        
                        return {
                            'variant': variant_num,
                            'strategy': strategy['name'],
                            'style': strategy['style'],
                            'path': str(image_path),
                            'color_scheme': strategy['color_scheme'],
                            'ai_generated': True,
                            'model_used': strategy['model']
                        }
    
    async def _generate_or_reuse_featured_image(self, title: str, content: Dict, 
                                              output_dir: Path) -> str:
        """アイキャッチ画像生成または再利用判定"""
        
        # YouTubeサムネイルが存在するかチェック
        youtube_thumbnail_path = output_dir.parent / "thumbnails" / "thumbnail_variant_1.png"
        
        if youtube_thumbnail_path.exists():
            # YouTubeサムネイルをブログ用にリサイズ・最適化
            featured_path = output_dir / "featured_image.png"
            self._optimize_thumbnail_for_blog(youtube_thumbnail_path, featured_path)
            self.logger.info("YouTubeサムネイルをブログアイキャッチに再利用")
            return str(featured_path)
        
        else:
            # 新規でアイキャッチ生成
            return await self._generate_new_featured_image(title, content, output_dir)
    
    async def _generate_section_images(self, content: Dict, output_dir: Path, 
                                     max_images: int = 2) -> List[str]:
        """セクション画像生成"""
        sections = content.get('sections', [])
        if not sections:
            return []
        
        # 最も重要な2セクションを選択
        important_sections = sections[:max_images]
        section_images = []
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                await self.authenticate_websocket(websocket)
                
                for i, section in enumerate(important_sections, 1):
                    section_title = section.get('title', f'Section {i}')
                    section_content = section.get('content', '')
                    
                    # セクション画像プロンプト生成
                    prompt = self._create_section_image_prompt(section_title, section_content)
                    
                    # 画像生成
                    image_path = await self._generate_section_image(
                        websocket, prompt, i, output_dir
                    )
                    
                    if image_path:
                        section_images.append(image_path)
        
        except Exception as e:
            self.logger.error(f"セクション画像生成エラー: {e}")
        
        return section_images
    
    async def _generate_thumbnails_rest_api(self, strategies: List[Dict], output_dir: Path) -> List[Dict]:
        """REST API経由でサムネイル生成（フォールバック）"""
        thumbnails = []
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            for i, strategy in enumerate(strategies, 1):
                payload = {
                    "input": [
                        {
                            "taskType": "imageInference",
                            "promptText": strategy['prompt'],
                            "height": 720,
                            "width": 1280,
                            "model": strategy['model'],
                            "numberResults": 1,
                            "outputFormat": "PNG",
                            "steps": 25,
                            "cfgScale": 7.0
                        }
                    ]
                }
                
                try:
                    async with session.post(
                        "https://api.runware.ai/v1/images",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result and 'data' in result and len(result['data']) > 0:
                                image_url = result['data'][0].get('imageURL')
                                if image_url:
                                    # 画像をダウンロード
                                    async with session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            image_data = await img_response.read()
                                            
                                            # 保存
                                            file_path = output_dir / f"youtube_thumbnail_{strategy['strategy']}_{i}.png"
                                            with open(file_path, 'wb') as f:
                                                f.write(image_data)
                                            
                                            thumbnails.append({
                                                'strategy': strategy['strategy'],
                                                'path': str(file_path),
                                                'prompt': strategy['prompt']
                                            })
                                            
                                            self.logger.info(f"✓ サムネイル生成完了: {strategy['strategy']}")
                        else:
                            self.logger.error(f"REST API エラー: {response.status}")
                            
                except Exception as e:
                    self.logger.error(f"サムネイル生成エラー ({strategy['strategy']}): {e}")
        
        return thumbnails
    
    def _optimize_thumbnail_for_blog(self, thumbnail_path: Path, output_path: Path):
        """YouTubeサムネイルをブログ用に最適化"""
        with Image.open(thumbnail_path) as img:
            # ブログアイキャッチ用にリサイズ
            blog_size = (self.blog_config['featured_width'], self.blog_config['featured_height'])
            
            # アスペクト比を保持してリサイズ
            img.thumbnail(blog_size, Image.Resampling.LANCZOS)
            
            # センタリング用の背景作成
            background = Image.new('RGB', blog_size, (255, 255, 255))
            
            # 中央配置
            x = (blog_size[0] - img.width) // 2
            y = (blog_size[1] - img.height) // 2
            background.paste(img, (x, y))
            
            # 保存
            background.save(output_path, 'PNG', optimize=True)
    
    def _add_text_overlay(self, image_path: Path, strategy: Dict):
        """サムネイルにテキストオーバーレイを追加"""
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            
            # フォント設定（システムフォントを使用）
            try:
                font_size = 60
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", font_size)
            except:
                font = ImageFont.load_default()
            
            # 戦略に応じたテキスト色
            color_schemes = {
                'impact': '#FFFFFF',
                'curiosity': '#FFD700', 
                'authority': '#1E3A8A'
            }
            
            text_color = color_schemes.get(strategy['style'], '#FFFFFF')
            
            # シンプルなバッジを追加
            badge_text = strategy['name'][:6]  # 最初の6文字
            
            # テキスト位置（右下）
            text_bbox = draw.textbbox((0, 0), badge_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = img.width - text_width - 20
            y = img.height - text_height - 20
            
            # 背景矩形
            draw.rectangle([x-10, y-5, x+text_width+10, y+text_height+5], 
                          fill=(0, 0, 0, 128))
            
            # テキスト描画
            draw.text((x, y), badge_text, fill=text_color, font=font)
            
            # 保存
            img.save(image_path, 'PNG')
    
    def _extract_keywords(self, text: str) -> List[str]:
        """重要キーワードを抽出"""
        # 簡易キーワード抽出（実装時はより高度な手法を使用）
        words = text.split()
        
        # 日本語の重要そうな語彙をフィルタ
        important_words = []
        for word in words:
            if len(word) > 2 and not word.isdigit():
                important_words.append(word)
        
        return important_words[:5]  # 上位5個を返す
    
    async def _download_and_save_image(self, image_url: str, save_path: Path):
        """画像URLから画像をダウンロードして保存"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
                
        except Exception as e:
            self.logger.error(f"画像ダウンロードエラー: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """API接続テスト"""
        try:
            # REST APIでシンプルなテスト
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # テスト用の簡単な生成リクエスト
            test_data = [{
                "taskType": "imageInference",
                "taskUUID": str(uuid.uuid4()),
                "positivePrompt": "simple test image",
                "width": 512,
                "height": 512,
                "numberResults": 1,
                "steps": 10
            }]
            
            response = requests.post(
                f"{self.rest_url}/inference",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Runware API接続成功'}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

class RunwareSetup:
    """Runware API環境設定とチェック"""
    
    @staticmethod
    def check_environment() -> Dict[str, bool]:
        """Runware API環境チェック"""
        import os
        
        checks = {
            'api_key_available': bool(os.getenv('RUNWARE_API_KEY')),
            'websockets_available': True,
            'requests_available': True,
            'pil_available': True
        }
        
        # 必要なライブラリの存在確認
        try:
            import websockets
        except ImportError:
            checks['websockets_available'] = False
        
        try:
            import requests
        except ImportError:
            checks['requests_available'] = False
            
        try:
            from PIL import Image
        except ImportError:
            checks['pil_available'] = False
        
        return checks
    
    @staticmethod
    def install_dependencies():
        """必要な依存関係をインストール"""
        import subprocess
        import sys
        
        dependencies = ['websockets', 'requests', 'Pillow']
        
        for dep in dependencies:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', dep, '--break-system-packages'
                ])
                print(f"✅ {dep} インストール完了")
            except subprocess.CalledProcessError as e:
                print(f"❌ {dep} インストール失敗: {e}")

if __name__ == "__main__":
    # テスト実行
    config = {
        'runware': {
            'api_key': 'your_api_key_here'
        }
    }
    
    generator = RunwareImageGenerator(config)
    
    # 接続テスト
    result = generator.test_connection()
    print(f"接続テスト結果: {result}")
    
    # 環境チェック
    env_check = RunwareSetup.check_environment()
    print(f"環境チェック: {env_check}")