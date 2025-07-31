#!/usr/bin/env python3
"""
VideoAI Studio - 統合ウィザードWebアプリケーション
動画から全コンテンツを生成する直感的なUIシステム
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# ローカルモジュール
from main import VideoContentProcessor
from modules.utils import setup_logging
import yaml

# 設定読み込み
with open('config.yaml', 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f)

# FastAPIアプリ初期化
app = FastAPI(
    title="VideoAI Studio",
    description="動画から全コンテンツを自動生成するAIスタジオ",
    version="1.0.0"
)

# 静的ファイルとテンプレート
app.mount("/static", StaticFiles(directory="web_static"), name="static")
templates = Jinja2Templates(directory="web_templates")

# ロギング設定
logger = setup_logging()

# グローバル変数
processor = None
current_session = {}

class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, session_id: str) -> Dict:
        """新しいセッションを作成"""
        self.sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'status': 'initialized',
            'steps_completed': [],
            'data': {},
            'files': {}
        }
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """セッション取得"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, data: Dict):
        """セッション更新"""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)

session_manager = SessionManager()

@app.on_event("startup")
async def startup_event():
    """アプリ起動時の初期化"""
    global processor
    
    # VideoContentProcessorを初期化
    processor = VideoContentProcessor(CONFIG)
    
    # 必要なディレクトリを作成
    Path("web_static").mkdir(exist_ok=True)
    Path("web_templates").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    Path("temp_sessions").mkdir(exist_ok=True)
    
    logger.info("🚀 VideoAI Studio が起動しました")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """ホームページ（ウィザード開始）"""
    
    # 新しいセッションを作成
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session = session_manager.create_session(session_id)
    
    return templates.TemplateResponse("next_gen_wizard.html", {
        "request": request,
        "session_id": session_id,
        "config": CONFIG
    })

@app.get("/classic", response_class=HTMLResponse)
async def classic_home(request: Request):
    """クラシック版ウィザード"""
    
    # 新しいセッションを作成
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session = session_manager.create_session(session_id)
    
    return templates.TemplateResponse("wizard.html", {
        "request": request,
        "session_id": session_id,
        "config": CONFIG
    })

@app.post("/api/upload")
async def upload_video(
    session_id: str = Form(...),
    video: UploadFile = File(...)
):
    """動画アップロード処理"""
    
    try:
        # セッション取得
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        # ファイル検証
        if not video.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            raise HTTPException(status_code=400, detail="対応していない動画形式です")
        
        # アップロードディレクトリ作成
        upload_dir = Path("uploads") / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル保存
        video_path = upload_dir / video.filename
        with open(video_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'video_uploaded',
            'steps_completed': ['upload'],
            'files': {'video': str(video_path)},
            'data': {
                'video_filename': video.filename,
                'video_size': len(content),
                'upload_time': datetime.now().isoformat()
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "動画アップロード完了",
            "video_info": {
                "filename": video.filename,
                "size": f"{len(content) / 1024 / 1024:.1f} MB",
                "path": str(video_path)
            }
        })
        
    except Exception as e:
        logger.error(f"動画アップロードエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/transcribe")
async def process_transcribe(request: Request):
    """音声文字起こし処理"""
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        video_path = session['files']['video']
        
        # Whisper処理（非同期）
        logger.info(f"🎤 文字起こし開始: {video_path}")
        transcript_data = processor.transcriber.transcribe(Path(video_path))
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'transcribed',
            'steps_completed': session['steps_completed'] + ['transcribe'],
            'data': {
                **session['data'],
                'transcript': transcript_data,
                'transcript_time': datetime.now().isoformat()
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "文字起こし完了",
            "transcript": {
                "text_preview": transcript_data['text'][:500] + "...",
                "duration": transcript_data.get('duration', 0),
                "word_count": len(transcript_data['text'].split())
            }
        })
        
    except Exception as e:
        logger.error(f"文字起こしエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/caption")
async def process_caption(request: Request):
    """キャプション作成処理"""
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        caption_style = data.get('style', 'standard')  # standard, dynamic, minimal
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        transcript_data = session['data']['transcript']
        
        # キャプション生成
        captions = generate_captions(transcript_data, caption_style)
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'caption_created',
            'steps_completed': session['steps_completed'] + ['caption'],
            'data': {
                **session['data'],
                'captions': captions,
                'caption_style': caption_style,
                'caption_time': datetime.now().isoformat()
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "キャプション作成完了",
            "captions": {
                "total_segments": len(captions),
                "style": caption_style,
                "preview": captions[:3]  # 最初の3セグメント
            }
        })
        
    except Exception as e:
        logger.error(f"キャプション作成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/content")
async def process_content(request: Request):
    """コンテンツ生成処理（ブログ・X投稿・YouTube）"""
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        title = data.get('title', '動画コンテンツ')
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        transcript_data = session['data']['transcript']
        video_path = Path(session['files']['video'])
        
        # コンテンツ生成
        logger.info(f"✍️ コンテンツ生成開始: {title}")
        content = processor.generator.generate_all(
            transcript_data=transcript_data,
            title=title,
            video_info=processor._get_video_info(video_path)
        )
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'content_generated',
            'steps_completed': session['steps_completed'] + ['content'],
            'data': {
                **session['data'],
                'content': content,
                'title': title,
                'content_time': datetime.now().isoformat()
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "コンテンツ生成完了",
            "content": {
                "blog_sections": len(content['blog'].get('sections', [])),
                "x_post_length": len(content.get('twitter', '')),
                "youtube_desc_length": len(content.get('youtube', '')),
                "keywords": content['blog'].get('keywords', [])[:5]
            }
        })
        
    except Exception as e:
        logger.error(f"コンテンツ生成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/thumbnail")
async def process_thumbnail(request: Request):
    """サムネイル生成処理"""
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        thumbnail_style = data.get('style', 'modern')  # modern, minimal, vibrant
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        title = session['data']['title']
        content = session['data']['content']
        
        # サムネイル生成
        logger.info(f"🎨 サムネイル生成開始: {thumbnail_style}")
        
        # 出力ディレクトリ
        output_dir = Path("temp_sessions") / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # サムネイル作成
        thumbnail_path = processor.thumbnail_creator.create(
            title=title,
            subtitle=content['thumbnail'].get('subtitle', ''),
            output_path=output_dir / "thumbnail.png"
        )
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'thumbnail_created',
            'steps_completed': session['steps_completed'] + ['thumbnail'],
            'files': {
                **session['files'],
                'thumbnail': str(thumbnail_path)
            },
            'data': {
                **session['data'],
                'thumbnail_style': thumbnail_style,
                'thumbnail_time': datetime.now().isoformat()
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "サムネイル生成完了",
            "thumbnail": {
                "path": str(thumbnail_path),
                "style": thumbnail_style,
                "url": f"/api/file/{session_id}/thumbnail.png"
            }
        })
        
    except Exception as e:
        logger.error(f"サムネイル生成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """セッション情報取得"""
    
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    return JSONResponse(session)

@app.get("/api/file/{session_id}/{filename}")
async def get_file(session_id: str, filename: str):
    """生成ファイルの取得"""
    
    file_path = Path("temp_sessions") / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    
    return FileResponse(
        file_path,
        media_type="image/png" if filename.endswith('.png') else "application/octet-stream"
    )

@app.post("/api/export")
async def export_content(request: Request):
    """最終コンテンツのエクスポート"""
    
    try:
        data = await request.json()
        session_id = data.get('session_id')
        export_formats = data.get('formats', ['blog', 'x', 'youtube'])
        
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        # エクスポート処理
        export_dir = Path("exports") / session_id
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        if 'blog' in export_formats:
            # Jekyll記事として保存
            jekyll_writer = processor.jekyll_writer
            post_path = jekyll_writer.create_post(
                title=session['data']['title'],
                content=session['data']['content']['blog'],
                transcript=session['data']['transcript'],
                output_dir=Path("_posts")
            )
            exported_files['blog'] = str(post_path)
        
        if 'x' in export_formats:
            # X投稿保存
            x_path = export_dir / "x_post.txt"
            x_path.write_text(session['data']['content']['twitter'], encoding='utf-8')
            exported_files['x'] = str(x_path)
        
        if 'youtube' in export_formats:
            # YouTube説明文保存
            youtube_path = export_dir / "youtube_description.txt"
            youtube_path.write_text(session['data']['content']['youtube'], encoding='utf-8')
            exported_files['youtube'] = str(youtube_path)
        
        # セッション更新
        session_manager.update_session(session_id, {
            'status': 'exported',
            'steps_completed': session['steps_completed'] + ['export'],
            'files': {
                **session['files'],
                **exported_files
            },
            'data': {
                **session['data'],
                'export_time': datetime.now().isoformat(),
                'export_formats': export_formats
            }
        })
        
        return JSONResponse({
            "success": True,
            "message": "エクスポート完了",
            "exported_files": exported_files
        })
        
    except Exception as e:
        logger.error(f"エクスポートエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_captions(transcript_data: Dict, style: str) -> List[Dict]:
    """キャプション生成関数"""
    
    text = transcript_data.get('text', '')
    words = text.split()
    
    captions = []
    words_per_segment = 8 if style == 'dynamic' else 12 if style == 'standard' else 15
    
    for i in range(0, len(words), words_per_segment):
        segment_words = words[i:i + words_per_segment]
        segment_text = ' '.join(segment_words)
        
        # 簡易的なタイミング計算
        start_time = i * 0.5  # 仮の計算
        end_time = (i + len(segment_words)) * 0.5
        
        captions.append({
            'start_time': start_time,
            'end_time': end_time,
            'text': segment_text,
            'style': style
        })
    
    return captions

if __name__ == "__main__":
    print("🎬 VideoAI Studio を起動しています...")
    print("📱 ブラウザで http://localhost:8003 を開いてください")
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )