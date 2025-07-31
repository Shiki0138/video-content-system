"""
ユーティリティ関数とヘルパー
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import colorama
from colorama import Fore, Back, Style

# カラー出力を有効化
colorama.init()


def setup_logging(log_file: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    """ロギング設定"""
    
    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラー（カラー付き）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    
    # ルートロガー設定
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー（指定時）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class ColoredFormatter(logging.Formatter):
    """カラー付きログフォーマッター"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def format_duration(seconds: float) -> str:
    """秒数を読みやすい形式に変換"""
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}時間{minutes}分"


def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを読みやすい形式に変換"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def clean_text(text: str) -> str:
    """テキストをクリーンアップ"""
    import re
    
    # 余分な空白を削除
    text = re.sub(r'\s+', ' ', text)
    
    # 句読点の前後の空白を調整
    text = re.sub(r'\s+([。、！？])', r'\1', text)
    text = re.sub(r'([。！？])\s*', r'\1 ', text)
    
    # 改行を正規化
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def split_text_by_sentences(text: str, max_length: int = 500) -> List[str]:
    """テキストを文単位で分割"""
    import re
    
    sentences = re.split(r'([。！？\n]+)', text)
    chunks = []
    current_chunk = ""
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
        
        if len(current_chunk) + len(sentence) + len(delimiter) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + delimiter
        else:
            current_chunk += sentence + delimiter
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def estimate_reading_time(text: str, wpm: int = 400) -> int:
    """読了時間を推定（分）"""
    word_count = len(text)
    reading_time = max(1, word_count // wpm)
    return reading_time


def sanitize_filename(filename: str) -> str:
    """ファイル名を安全な形式に変換"""
    import re
    
    # 使用不可文字を置換
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 連続するアンダースコアを1つに
    filename = re.sub(r'_+', '_', filename)
    # 前後の空白とアンダースコアを削除
    filename = filename.strip('_ ')
    
    return filename[:200]  # 最大200文字


def create_progress_bar(total: int, desc: str = "処理中") -> 'tqdm':
    """プログレスバーを作成"""
    from tqdm import tqdm
    
    return tqdm(
        total=total,
        desc=desc,
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
        ncols=100
    )


class Timer:
    """処理時間計測クラス"""
    
    def __init__(self, name: str = "処理"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logging.info(f"{self.name}を開始...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        logging.info(f"{self.name}完了 (所要時間: {duration.total_seconds():.2f}秒)")
    
    def elapsed(self) -> float:
        """経過時間を取得（秒）"""
        if self.start_time is None:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


def find_video_files(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """ディレクトリから動画ファイルを検索"""
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    
    video_files = []
    for ext in extensions:
        video_files.extend(directory.glob(f"*{ext}"))
        video_files.extend(directory.glob(f"*{ext.upper()}"))
    
    return sorted(video_files)


def validate_environment() -> bool:
    """実行環境を検証"""
    issues = []
    
    # Python バージョンチェック
    if sys.version_info < (3, 8):
        issues.append("Python 3.8以上が必要です")
    
    # 必要なコマンドチェック
    import shutil
    
    if not shutil.which('ffmpeg'):
        issues.append("ffmpegがインストールされていません")
    
    if not shutil.which('ffprobe'):
        issues.append("ffprobeがインストールされていません")
    
    # 必要なディレクトリ作成
    required_dirs = ['output', 'logs', 'templates', '_posts']
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    if issues:
        for issue in issues:
            logging.error(f"❌ {issue}")
        return False
    
    return True