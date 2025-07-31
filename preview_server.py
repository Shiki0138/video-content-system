#!/usr/bin/env python3
"""
軽量ブログプレビューサーバー
Jekyllサイトのプレビューを簡単に表示
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
import markdown
from typing import Dict, List

class BlogPreviewHandler(SimpleHTTPRequestHandler):
    """ブログプレビュー用のHTTPハンドラー"""
    
    def __init__(self, *args, **kwargs):
        self.posts_dir = Path("_posts")
        self.config_file = Path("_config.yml")
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """GETリクエストの処理"""
        
        if self.path == '/':
            self.serve_index()
        elif self.path.startswith('/posts/'):
            self.serve_post()
        elif self.path.endswith('.css'):
            self.serve_css()
        else:
            super().do_GET()
    
    def serve_index(self):
        """インデックスページ（記事一覧）を表示"""
        
        try:
            # 設定ファイル読み込み
            config = self.load_config()
            
            # 記事一覧取得
            posts = self.get_all_posts()
            
            # HTMLを生成
            html = self.generate_index_html(config, posts)
            
            # レスポンス送信
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_post(self):
        """個別記事を表示"""
        
        try:
            # URLから記事ファイル名を特定
            path_parts = self.path.strip('/').split('/')
            if len(path_parts) >= 4:
                year, month, day = path_parts[1:4]
                slug = path_parts[4] if len(path_parts) > 4 else "post"
                
                # 記事ファイルを検索
                post_file = self.find_post_file(year, month, day, slug)
                
                if post_file and post_file.exists():
                    config = self.load_config()
                    post_data = self.parse_post_file(post_file)
                    html = self.generate_post_html(config, post_data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    return
            
            self.send_error(404, "Post not found")
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_css(self):
        """CSSファイルを提供"""
        
        css_content = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            text-align: center;
            border-radius: 10px;
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .post-list {
            display: grid;
            gap: 1.5rem;
        }
        
        .post-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .post-title {
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }
        
        .post-title a {
            text-decoration: none;
            color: inherit;
        }
        
        .post-title a:hover {
            color: #667eea;
        }
        
        .post-meta {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .post-excerpt {
            color: #555;
        }
        
        .post-content {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .post-content h2 {
            color: #2c3e50;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }
        
        .post-content p {
            margin: 1rem 0;
        }
        
        .post-content ol, .post-content ul {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        .post-content li {
            margin: 0.5rem 0;
        }
        
        .featured-image {
            text-align: center;
            margin: 2rem 0;
        }
        
        .featured-image img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .section-image {
            text-align: center;
            margin: 1.5rem 0;
        }
        
        .section-image img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        
        .toc {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }
        
        .toc h2 {
            margin-top: 0;
            color: #495057;
            border-bottom: none;
        }
        
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        
        .toc li {
            padding: 0.3rem 0;
        }
        
        .toc a {
            text-decoration: none;
            color: #667eea;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        .article-footer {
            margin-top: 3rem;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .article-meta {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 0.5rem 1rem;
            margin: 1rem 0;
        }
        
        .article-meta dt {
            font-weight: bold;
            color: #495057;
        }
        
        .key-points {
            margin-top: 2rem;
        }
        
        .key-points ul {
            list-style: none;
            padding-left: 0;
        }
        
        .key-points li {
            background: #e3f2fd;
            margin: 0.5rem 0;
            padding: 0.8rem;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }
        
        .nav-link {
            display: inline-block;
            margin: 2rem 0;
            padding: 0.8rem 1.5rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.2s ease;
        }
        
        .nav-link:hover {
            background: #5a6fd8;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .post-content {
                padding: 1rem;
            }
            
            h1 {
                font-size: 1.5rem;
            }
        }
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/css; charset=utf-8')
        self.end_headers()
        self.wfile.write(css_content.encode('utf-8'))
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        return {
            'title': 'Video Content System',
            'description': 'AI生成動画ブログ'
        }
    
    def get_all_posts(self) -> List[Dict]:
        """全記事を取得"""
        
        posts = []
        
        if self.posts_dir.exists():
            for post_file in sorted(self.posts_dir.glob("*.md"), reverse=True):
                try:
                    post_data = self.parse_post_file(post_file)
                    post_data['filename'] = post_file.name
                    posts.append(post_data)
                except Exception as e:
                    print(f"記事解析エラー {post_file}: {e}")
                    continue
        
        return posts
    
    def parse_post_file(self, post_file: Path) -> Dict:
        """記事ファイルを解析"""
        
        content = post_file.read_text(encoding='utf-8')
        
        # Front Matterを抽出
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1])
                post_content = parts[2].strip()
            else:
                front_matter = {}
                post_content = content
        else:
            front_matter = {}
            post_content = content
        
        return {
            'front_matter': front_matter,
            'content': post_content,
            'title': front_matter.get('title', 'Untitled'),
            'date': front_matter.get('date', ''),
            'excerpt': front_matter.get('excerpt', '')
        }
    
    def find_post_file(self, year: str, month: str, day: str, slug: str) -> Path:
        """記事ファイルを検索"""
        
        # 標準的なJekyllファイル名パターンで検索
        pattern = f"{year}-{month}-{day}-*"
        
        for post_file in self.posts_dir.glob(pattern):
            return post_file
        
        return None
    
    def generate_index_html(self, config: Dict, posts: List[Dict]) -> str:
        """インデックスページのHTMLを生成"""
        
        posts_html = ""
        for post in posts:
            # URLを生成
            filename = post['filename']
            date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.*?)\.md', filename)
            if date_match:
                year, month, day, slug = date_match.groups()
                post_url = f"/posts/{year}/{month}/{day}/{slug}/"
            else:
                post_url = "#"
            
            posts_html += f"""
            <div class="post-card">
                <h2 class="post-title">
                    <a href="{post_url}">{post['title']}</a>
                </h2>
                <div class="post-meta">
                    📅 {post['date']} • 📝 動画から自動生成
                </div>
                <div class="post-excerpt">
                    {post['excerpt'][:200]}{'...' if len(post['excerpt']) > 200 else ''}
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{config.get('title', 'Video Blog')}</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🎬 {config.get('title', 'Video Blog')}</h1>
                    <div class="subtitle">{config.get('description', 'AI生成動画ブログ')}</div>
                </header>
                
                <main class="post-list">
                    {posts_html}
                </main>
            </div>
        </body>
        </html>
        """
    
    def generate_post_html(self, config: Dict, post_data: Dict) -> str:
        """記事ページのHTMLを生成"""
        
        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{post_data['title']} - {config.get('title', 'Video Blog')}</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🎬 {config.get('title', 'Video Blog')}</h1>
                    <div class="subtitle">{config.get('description', 'AI生成動画ブログ')}</div>
                </header>
                
                <a href="/" class="nav-link">← 記事一覧に戻る</a>
                
                <article class="post-content">
                    <h1>{post_data['title']}</h1>
                    <div class="post-meta">📅 {post_data['date']} • 📝 動画から自動生成</div>
                    
                    <div class="post-body">
                        {post_data['content']}
                    </div>
                </article>
                
                <a href="/" class="nav-link">← 記事一覧に戻る</a>
            </div>
        </body>
        </html>
        """


def start_preview_server(port: int = 8000):
    """プレビューサーバーを起動"""
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, BlogPreviewHandler)
    
    print(f"🚀 ブログプレビューサーバーを起動しました")
    print(f"📱 ブラウザで http://localhost:{port} を開いてください")
    print(f"🛑 終了するには Ctrl+C を押してください")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ サーバーを停止しました")
        httpd.shutdown()


if __name__ == "__main__":
    import sys
    
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("ポート番号は数値で指定してください")
            sys.exit(1)
    
    start_preview_server(port)