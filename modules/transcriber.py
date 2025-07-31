"""
Whisperを使用した動画文字起こしモジュール
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import whisper
from tqdm import tqdm

logger = logging.getLogger(__name__)


class VideoTranscriber:
    """動画文字起こしクラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Whisperモデルをロード"""
        model_name = self.config.get('model', 'base')
        logger.info(f"Whisperモデル '{model_name}' をロード中...")
        
        try:
            self.model = whisper.load_model(
                model_name,
                device=self.config.get('device', 'cpu')
            )
            logger.info("✓ モデルロード完了")
        except Exception as e:
            logger.error(f"モデルロード失敗: {e}")
            raise
    
    def transcribe(self, video_path: Path, output_dir: Path) -> Dict:
        """動画を文字起こし"""
        
        if not self.model:
            raise RuntimeError("Whisperモデルがロードされていません")
        
        # 文字起こし実行
        logger.info(f"文字起こし開始: {video_path.name}")
        
        result = self.model.transcribe(
            str(video_path),
            language=self.config.get('language', 'ja'),
            verbose=self.config.get('verbose', False),
            task='transcribe'
        )
        
        # 結果を構造化
        transcript_data = self._structure_transcript(result)
        
        # ファイルに保存
        self._save_transcript(transcript_data, output_dir)
        
        return transcript_data
    
    def _structure_transcript(self, result: Dict) -> Dict:
        """文字起こし結果を構造化"""
        
        # セグメントを処理
        segments = []
        chapters = []
        last_chapter_time = 0
        
        for seg in result.get('segments', []):
            # セグメント情報
            segment = {
                'id': seg['id'],
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'].strip(),
                'duration': seg['end'] - seg['start']
            }
            segments.append(segment)
            
            # チャプター候補（30秒以上の間隔）
            if seg['start'] - last_chapter_time >= 30:
                chapters.append({
                    'time': self._format_time(seg['start']),
                    'timestamp': seg['start'],
                    'title': seg['text'][:50].strip() + ('...' if len(seg['text']) > 50 else '')
                })
                last_chapter_time = seg['start']
        
        # 全体の構造化データ
        return {
            'text': result.get('text', ''),
            'segments': segments,
            'chapters': chapters,
            'language': result.get('language', 'ja'),
            'duration': segments[-1]['end'] if segments else 0
        }
    
    def _format_time(self, seconds: float) -> str:
        """秒を MM:SS 形式に変換"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def _save_transcript(self, data: Dict, output_dir: Path):
        """文字起こしデータを保存"""
        
        # JSON形式で保存
        json_path = output_dir / "transcript.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # テキスト形式で保存
        text_path = output_dir / "transcript.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(data['text'])
        
        # タイムスタンプ付きで保存
        timestamps_path = output_dir / "transcript_timestamps.txt"
        with open(timestamps_path, 'w', encoding='utf-8') as f:
            for seg in data['segments']:
                f.write(f"[{self._format_time(seg['start'])} - {self._format_time(seg['end'])}]\n")
                f.write(f"{seg['text']}\n\n")
        
        logger.info(f"✓ 文字起こし保存完了: {output_dir}")


class BatchTranscriber:
    """バッチ処理用文字起こしクラス"""
    
    def __init__(self, config: Dict):
        self.transcriber = VideoTranscriber(config)
    
    def process_videos(self, video_paths: List[Path], output_base: Path) -> List[Dict]:
        """複数の動画を処理"""
        results = []
        
        for video_path in tqdm(video_paths, desc="動画処理中"):
            try:
                output_dir = output_base / video_path.stem
                output_dir.mkdir(exist_ok=True)
                
                result = self.transcriber.transcribe(video_path, output_dir)
                results.append({
                    'video': str(video_path),
                    'success': True,
                    'data': result
                })
            except Exception as e:
                logger.error(f"処理失敗 {video_path}: {e}")
                results.append({
                    'video': str(video_path),
                    'success': False,
                    'error': str(e)
                })
        
        return results