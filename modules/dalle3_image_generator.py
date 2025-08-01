#!/usr/bin/env python3
"""
DALL-E 2/3 画像生成モジュール
サムネイル: DALL-E 3（高品質）、ブログ画像: DALL-E 2（コスト効率）
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import aiohttp
import requests
from openai import AsyncOpenAI, OpenAI
import base64
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class DALLE3ImageGenerator:
    """DALL-E 2/3を使用した画像生成クラス（タイプ別プロバイダー対応）"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # DALL-E 3設定
        self.dalle3_config = config.get('dalle3', {})
        self.dalle3_api_key = self.dalle3_config.get('api_key')
        
        # DALL-E 2設定
        self.dalle2_config = config.get('dalle2', {})
        self.dalle2_api_key = self.dalle2_config.get('api_key') or self.dalle3_api_key
        
        if not self.dalle3_api_key:
            raise ValueError("OpenAI APIキーが設定されていません")
        
        # OpenAIクライアント初期化
        self.client = OpenAI(api_key=self.dalle3_api_key)
        self.async_client = AsyncOpenAI(api_key=self.dalle3_api_key)
        
        # DALL-E 3設定
        self.dalle3_size = self.dalle3_config.get('default_size', '1792x1024')
        self.dalle3_quality = self.dalle3_config.get('quality', 'hd')
        self.dalle3_style = self.dalle3_config.get('style', 'natural')
        
        # DALL-E 2設定
        self.dalle2_size = self.dalle2_config.get('default_size', '1024x1024')
        
        logger.info("DALL-E 2/3 画像生成器を初期化しました")
        logger.info(f"サムネイル: DALL-E 3 ({self.dalle3_quality}品質)")
        logger.info(f"ブログ画像: DALL-E 2 (コスト効率)")
    
    async def generate_youtube_thumbnails(self, title: str, transcript_data: Dict, 
                                        output_dir: Path) -> List[Dict]:
        """YouTubeサムネイル3戦略生成"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 3つの戦略でプロンプト生成
        strategies = [
            {
                'strategy': 'impact',
                'name': 'インパクト型',
                'prompt': self._create_impact_thumbnail_prompt(title, transcript_data)
            },
            {
                'strategy': 'curiosity',
                'name': '好奇心型',
                'prompt': self._create_curiosity_thumbnail_prompt(title, transcript_data)
            },
            {
                'strategy': 'authority',
                'name': '権威型',
                'prompt': self._create_authority_thumbnail_prompt(title, transcript_data)
            }
        ]
        
        thumbnails = []
        
        for i, strategy in enumerate(strategies, 1):
            try:
                logger.info(f"YouTubeサムネイル生成中 ({strategy['name']}) - DALL-E 3使用")
                
                # DALL-E 3で高品質生成
                response = await self.async_client.images.generate(
                    model="dall-e-3",
                    prompt=strategy['prompt'],
                    size=self.dalle3_size,  # 1792x1024
                    quality=self.dalle3_quality,  # hd
                    style=self.dalle3_style,  # natural
                    n=1
                )
                
                # 画像をダウンロードして保存
                image_url = response.data[0].url
                file_path = output_dir / f"youtube_thumbnail_{strategy['strategy']}_{i}.png"
                
                await self._download_and_save_image(image_url, file_path)
                
                # リサイズしてYouTube用に最適化
                self._resize_for_youtube(file_path)
                
                thumbnails.append({
                    'strategy': strategy['strategy'],
                    'name': strategy['name'],
                    'path': str(file_path),
                    'prompt': strategy['prompt']
                })
                
                logger.info(f"✓ {strategy['name']}サムネイル生成完了")
                
            except Exception as e:
                logger.error(f"サムネイル生成エラー ({strategy['name']}): {e}")
        
        return thumbnails
    
    async def generate_blog_images(self, title: str, content: Dict, 
                                 output_dir: Path) -> Dict[str, str]:
        """ブログ画像生成（アイキャッチ + セクション画像2枚）"""
        output_dir.mkdir(parents=True, exist_ok=True)
        images = {}
        
        try:
            # アイキャッチ画像 - DALL-E 3で高品質生成
            logger.info("ブログアイキャッチ画像生成中... - DALL-E 3使用")
            featured_prompt = self._create_blog_featured_prompt(title, content)
            
            response = await self.async_client.images.generate(
                model="dall-e-3",
                prompt=featured_prompt,
                size=self.dalle3_size,  # 1792x1024
                quality=self.dalle3_quality,  # hd
                style=self.dalle3_style,  # natural
                n=1
            )
            
            featured_path = output_dir / "blog_featured.png"
            await self._download_and_save_image(response.data[0].url, featured_path)
            self._resize_for_blog(featured_path)
            images['featured'] = str(featured_path)
            
            logger.info("✓ アイキャッチ画像生成完了 (DALL-E 3)")
            
            # セクション画像（最大2枚）- DALL-E 2でコスト効率重視
            sections = content.get('sections', [])[:2]
            for i, section in enumerate(sections, 1):
                logger.info(f"セクション画像 {i} 生成中... - DALL-E 2使用（コスト効率）")
                
                section_prompt = self._create_section_image_prompt(section)
                
                # DALL-E 2でコスト効率的に生成
                response = await self.async_client.images.generate(
                    model="dall-e-2",
                    prompt=section_prompt,
                    size=self.dalle2_size,  # 1024x1024
                    n=1
                )
                
                section_path = output_dir / f"blog_section_{i}.png"
                await self._download_and_save_image(response.data[0].url, section_path)
                images[f'section_{i}'] = str(section_path)
                
                logger.info(f"✓ セクション画像 {i} 生成完了 (DALL-E 2)")
                
        except Exception as e:
            logger.error(f"ブログ画像生成エラー: {e}")
        
        return images
    
    def _create_impact_thumbnail_prompt(self, title: str, transcript_data: Dict) -> str:
        """インパクト型サムネイルプロンプト生成"""
        return f"""
        YouTubeサムネイル用画像を作成してください。

        要件：
        - 左側に大きな日本語テキスト「{title}」を配置
        - 右側に「動画→AI→自動化」の流れを示すビジュアル
        - 背景は暗めのグラデーション
        - 黄色とオレンジのアクセントカラー
        - 日本語フォントは太いゴシック体
        - プロフェッショナルで目を引くデザイン
        - 16:9の横長構図
        
        スタイル：モダン、インパクトのある、YouTube向け
        """
    
    def _create_curiosity_thumbnail_prompt(self, title: str, transcript_data: Dict) -> str:
        """好奇心型サムネイルプロンプト生成"""
        return f"""
        YouTubeサムネイル用画像を作成してください。

        要件：
        - 中央に「？」マークと共に「{title[:10]}...」のテキスト
        - 周りに動画、ブログ、SNSのアイコンが浮遊
        - 神秘的な紫とブルーのグラデーション背景
        - 「秘密のAIツール」という小さなサブテキスト
        - ミステリアスで興味を引く雰囲気
        - 16:9の横長構図
        
        スタイル：神秘的、好奇心を刺激する、プロフェッショナル
        """
    
    def _create_authority_thumbnail_prompt(self, title: str, transcript_data: Dict) -> str:
        """権威型サムネイルプロンプト生成"""
        return f"""
        YouTubeサムネイル用画像を作成してください。

        要件：
        - クリーンな白背景
        - 中央に整理されたワークフロー図
        - 「{title}」のテキストを上部に配置
        - 「プロが教える」のサブテキスト
        - ブルーとグレーの信頼感のある配色
        - ビジネス向けの洗練されたデザイン
        - 16:9の横長構図
        
        スタイル：プロフェッショナル、信頼感、教育的
        """
    
    def _create_blog_featured_prompt(self, title: str, content: Dict) -> str:
        """ブログアイキャッチ画像プロンプト生成"""
        keywords = content.get('keywords', [])
        return f"""
        ブログ記事のアイキャッチ画像を作成してください。

        記事タイトル：{title}
        キーワード：{', '.join(keywords[:3])}
        
        要件：
        - モダンでクリーンなデザイン
        - AI自動化をテーマにした抽象的なビジュアル
        - パープルとブルーのグラデーション
        - テキストは含めない（後で追加するため）
        - 横長の構図（16:9）
        
        スタイル：モダン、テクノロジー、プロフェッショナル
        """
    
    def _create_section_image_prompt(self, section: Dict) -> str:
        """セクション画像プロンプト生成"""
        return f"""
        ブログ記事のセクション画像を作成してください。

        セクションテーマ：{section.get('title', '')}
        
        要件：
        - シンプルでわかりやすいイラスト
        - セクションの内容を視覚的に表現
        - 明るく親しみやすい色調
        - 正方形の構図（1:1）
        
        スタイル：フラットデザイン、わかりやすい、親しみやすい
        """
    
    async def _download_and_save_image(self, image_url: str, file_path: Path):
        """画像をダウンロードして保存"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                else:
                    raise Exception(f"画像ダウンロード失敗: {response.status}")
    
    def _resize_for_youtube(self, image_path: Path):
        """YouTube用に1280x720にリサイズ"""
        img = Image.open(image_path)
        if img.size != (1280, 720):
            img_resized = img.resize((1280, 720), Image.Resampling.LANCZOS)
            img_resized.save(image_path)
            logger.info(f"YouTube用にリサイズ: {image_path}")
    
    def _resize_for_blog(self, image_path: Path):
        """ブログ用に1200x630にリサイズ"""
        img = Image.open(image_path)
        if img.size != (1200, 630):
            img_resized = img.resize((1200, 630), Image.Resampling.LANCZOS)
            img_resized.save(image_path)
            logger.info(f"ブログ用にリサイズ: {image_path}")
    
    def test_connection(self) -> Dict[str, Any]:
        """API接続テスト"""
        try:
            # シンプルなテスト生成
            response = self.client.images.generate(
                model="dall-e-3",
                prompt="A simple test image with the text 'API Connected'",
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return {
                    'success': True,
                    'message': 'DALL-E 3 API接続成功',
                    'test_url': response.data[0].url
                }
            else:
                return {
                    'success': False,
                    'error': '画像生成に失敗しました'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API接続エラー: {str(e)}'
            }


class DALLE3Setup:
    """DALL-E 3セットアップヘルパー"""
    
    @staticmethod
    def check_environment() -> Dict[str, bool]:
        """環境チェック"""
        return {
            'openai_installed': True,  # requirements.txtに追加済み
            'api_key_set': bool(os.environ.get('OPENAI_API_KEY')),
            'pil_installed': True,
            'aiohttp_installed': True
        }
    
    @staticmethod
    def estimate_cost(num_youtube: int = 3, num_blog: int = 3) -> Dict[str, float]:
        """DALL-E 2/3混合コスト見積もり"""
        # DALL-E 料金（2024年時点）
        dalle3_hd_1792x1024 = 0.080      # DALL-E 3 HD品質
        dalle2_1024x1024 = 0.020         # DALL-E 2 標準品質
        
        # YouTube サムネイル: DALL-E 3 HD
        youtube_cost = num_youtube * dalle3_hd_1792x1024
        
        # ブログ画像: アイキャッチ1枚（DALL-E 3）+ セクション画像（DALL-E 2）
        blog_featured_cost = 1 * dalle3_hd_1792x1024  # アイキャッチ
        blog_section_cost = (num_blog - 1) * dalle2_1024x1024  # セクション画像
        blog_cost = blog_featured_cost + blog_section_cost
        
        # 従来のDALL-E 3のみのコスト（比較用）
        dalle3_only_cost = (num_youtube + num_blog) * dalle3_hd_1792x1024
        savings = dalle3_only_cost - (youtube_cost + blog_cost)
        
        return {
            'youtube_thumbnails': youtube_cost,
            'blog_images': blog_cost,
            'blog_featured': blog_featured_cost,
            'blog_sections': blog_section_cost,
            'total': youtube_cost + blog_cost,
            'total_jpy': (youtube_cost + blog_cost) * 150,  # 1ドル150円
            'dalle3_only_cost': dalle3_only_cost,
            'savings': savings,
            'savings_percentage': (savings / dalle3_only_cost) * 100 if dalle3_only_cost > 0 else 0
        }