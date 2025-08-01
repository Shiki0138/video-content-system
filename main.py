#!/usr/bin/env python3
"""
Video Content System - メインスクリプト
動画から自動的にブログ、YouTube、X投稿を生成
"""

import os
import sys
import json
import yaml
import click
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ローカルモジュール
from modules.transcriber import VideoTranscriber
from modules.content_generator import ContentGenerator
from modules.thumbnail_creator import ThumbnailCreator
from modules.jekyll_writer import JekyllWriter
from modules.social_media_manager import XPostGenerator, SocialMediaScheduler
from modules.internal_linking import InternalLinkManager
from modules.utils import setup_logging, format_duration, clean_text

# 設定ファイル読み込み
with open('config.yaml', 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f)

# ロギング設定
logger = setup_logging()


class VideoContentProcessor:
    """動画コンテンツ処理メインクラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.transcriber = VideoTranscriber(config['whisper'])
        self.generator = ContentGenerator(config['content'])
        self.thumbnail_creator = ThumbnailCreator(config['thumbnail'])
        self.jekyll_writer = JekyllWriter(config['jekyll'])
        self.x_post_generator = XPostGenerator(config.get('social_media', {}).get('x', {}))
        self.social_scheduler = SocialMediaScheduler(config.get('social_media', {}))
        self.link_manager = InternalLinkManager(config.get('internal_linking', {}))
        
        # 出力ディレクトリ作成
        self.output_base = Path(config['output']['base_dir'])
        self.output_base.mkdir(exist_ok=True)
        
    def process_video(self, video_path: str, title: Optional[str] = None) -> Dict:
        """動画を処理してコンテンツを生成"""
        
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
        
        # タイトル生成
        if not title:
            title = video_path.stem.replace('_', ' ').replace('-', ' ').title()
        
        # タイムスタンプ付き出力ディレクトリ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.output_base / f"{timestamp}_{video_path.stem}"
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"🎬 処理開始: {video_path.name}")
        logger.info(f"📝 タイトル: {title}")
        
        try:
            # Step 1: 文字起こし
            logger.info("🎤 文字起こし中...")
            transcript_data = self.transcriber.transcribe(video_path, output_dir)
            
            # Step 2: コンテンツ生成
            logger.info("✍️ コンテンツ生成中...")
            content = self.generator.generate_all(
                transcript_data=transcript_data,
                title=title,
                video_info=self._get_video_info(video_path)
            )
            
            # Step 3: サムネイル生成（ブログで再利用する可能性があるため先に生成）
            logger.info("🎨 サムネイル生成中...")
            thumbnail_path = None
            if self.config.get('thumbnail', {}).get('image_provider') == 'runware':
                # Runware APIでのサムネイル生成は後で行う
                logger.info("Runwareサムネイル生成は後で実行")
            else:
                thumbnail_path = self.thumbnail_creator.create(
                    title=content['thumbnail']['title'],
                    subtitle=content['thumbnail']['subtitle'],
                    output_path=output_dir / "thumbnail.png"
                )
            
            # Step 4: WordPress/CMSブログコンテンツ作成
            logger.info("📄 ブログコンテンツ作成中...")
            
            # WordPress/CMS用のコンテンツ生成
            from modules.wordpress_content_generator import WordPressContentGenerator
            wp_generator = WordPressContentGenerator(self.config)
            wp_outputs = wp_generator.create_content(
                title=title,
                content=content['blog'],
                transcript=transcript_data,
                output_dir=output_dir
            )
            
            logger.info(f"📝 ブログコンテンツ: {wp_outputs['blog']}")
            logger.info(f"🔍 SEOメタデータ: {wp_outputs['meta']}")
            logger.info(f"🏷️ タグ・カテゴリ: {wp_outputs['taxonomy']}")
            
            # 互換性のため変数名を維持
            jekyll_path = wp_outputs['blog']
            
            # Step 4: YouTube説明文保存
            youtube_path = output_dir / "youtube_description.txt"
            youtube_path.write_text(content['youtube'], encoding='utf-8')
            logger.info(f"📺 YouTube説明文: {youtube_path}")
            
            # Step 5: X投稿バリエーション生成
            logger.info("🐦 X投稿バリエーション生成中...")
            video_info = self._get_video_info(video_path)
            x_variations = self.x_post_generator.generate_post_variations(
                blog_content=content['blog'],
                video_info=video_info
            )
            
            # X投稿文を保存
            twitter_path = output_dir / "x_posts.json"
            twitter_path.write_text(
                json.dumps(x_variations, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            # レガシー形式も保存（互換性のため）
            legacy_twitter_path = output_dir / "twitter_post.txt"
            legacy_twitter_path.write_text(content['twitter'], encoding='utf-8')
            
            logger.info(f"🐦 X投稿バリエーション: {twitter_path}")
            logger.info(f"🐦 従来形式X投稿: {legacy_twitter_path}")
            
            # Step 6: Runwareサムネイル生成（まだ生成していない場合）
            if self.config.get('thumbnail', {}).get('image_provider') == 'runware' and not thumbnail_path:
                logger.info("🎨 Runwareでサムネイル生成中...")
                # TODO: ここでRunware APIを使用したサムネイル生成を実装
                # 現時点では従来のサムネイル生成を使用
                thumbnail_path = self.thumbnail_creator.create(
                    title=content['thumbnail']['title'],
                    subtitle=content['thumbnail']['subtitle'],
                    output_path=output_dir / "thumbnail.png"
                )
            
            # Step 7: 内部リンク処理
            logger.info("🔗 内部リンク処理中...")
            link_results = self.link_manager.process_new_post(
                new_post_path=jekyll_path,
                post_content=content['blog']
            )
            
            # 動画リンクを記事に追加（YouTube URLがある場合）
            if video_info.get('youtube_url'):
                self.jekyll_writer.add_video_link_section(jekyll_path, video_info['youtube_url'])
            
            # Step 8: メタデータ保存
            metadata = {
                'title': title,
                'video_path': str(video_path),
                'processed_at': datetime.now().isoformat(),
                'output_dir': str(output_dir),
                'files': {
                    'jekyll': str(jekyll_path),
                    'youtube': str(youtube_path),
                    'x_posts': str(twitter_path),
                    'twitter_legacy': str(legacy_twitter_path),
                    'thumbnail': str(thumbnail_path),
                    'transcript': str(output_dir / "transcript.json")
                },
                'stats': {
                    'duration': transcript_data.get('duration', 0),
                    'word_count': len(transcript_data.get('text', '').split()),
                    'sections': len(content['blog'].get('sections', [])),
                    'related_posts_found': len(link_results.get('related_posts', [])),
                    'x_variations_generated': len(x_variations)
                },
                'social_media': {
                    'x_variations': list(x_variations.keys()),
                    'internal_links': link_results
                }
            }
            
            metadata_path = output_dir / "metadata.json"
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            logger.info("✅ 処理完了！")
            self._print_summary(metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ エラーが発生しました: {e}")
            raise
    
    def _get_video_info(self, video_path: Path) -> Dict:
        """動画情報を取得"""
        try:
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(video_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data['format'].get('duration', 0))
                return {
                    'duration': duration,
                    'duration_str': format_duration(duration),
                    'size': int(data['format'].get('size', 0)),
                    'format': data['format'].get('format_name', 'unknown')
                }
        except:
            pass
        
        return {'duration': 0, 'duration_str': '0:00', 'size': 0, 'format': 'unknown'}
    
    def _print_summary(self, metadata: Dict):
        """処理結果のサマリーを表示"""
        print("\n" + "="*50)
        print("📊 処理結果サマリー")
        print("="*50)
        print(f"📹 タイトル: {metadata['title']}")
        print(f"⏱️ 動画時間: {format_duration(metadata['stats']['duration'])}")
        print(f"📝 文字数: {metadata['stats']['word_count']:,}文字")
        print(f"📑 セクション数: {metadata['stats']['sections']}")
        print(f"\n📁 出力ファイル:")
        for file_type, file_path in metadata['files'].items():
            print(f"  - {file_type}: {Path(file_path).name}")
        print("\n💡 次のステップ:")
        print("  1. Jekyll記事を確認: " + metadata['files']['jekyll'])
        print("  2. サムネイルを確認: " + metadata['files']['thumbnail'])
        print("  3. jekyll serve でプレビュー")
        print("="*50)


@click.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--title', '-t', help='動画タイトル')
@click.option('--model', '-m', default='base', help='Whisperモデル (tiny/base/small/medium/large)')
@click.option('--batch', '-b', is_flag=True, help='バッチ処理モード')
def main(video_path: str, title: Optional[str], model: str, batch: bool):
    """動画からブログ・YouTube・X投稿を自動生成"""
    
    # モデル設定を上書き
    if model:
        CONFIG['whisper']['model'] = model
    
    # プロセッサー初期化
    processor = VideoContentProcessor(CONFIG)
    
    if batch and os.path.isdir(video_path):
        # バッチ処理
        video_files = list(Path(video_path).glob("*.mp4"))
        video_files.extend(Path(video_path).glob("*.mov"))
        video_files.extend(Path(video_path).glob("*.avi"))
        
        logger.info(f"🎬 {len(video_files)}個の動画を処理します")
        
        for video_file in video_files:
            try:
                processor.process_video(str(video_file))
            except Exception as e:
                logger.error(f"❌ {video_file.name} の処理に失敗: {e}")
                continue
    else:
        # 単一ファイル処理
        processor.process_video(video_path, title)


if __name__ == "__main__":
    main()