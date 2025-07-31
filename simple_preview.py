#!/usr/bin/env python3
"""
シンプルブログプレビューサーバー
依存関係なしでブログ記事をプレビュー
"""

import re
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote

class SimpleBlogHandler(SimpleHTTPRequestHandler):
    """シンプルなブログプレビューハンドラー"""
    
    def do_GET(self):
        """GETリクエストの処理"""
        
        if self.path == '/':
            self.serve_index()
        elif self.path == '/style.css':
            self.serve_css()
        elif self.path.startswith('/post/'):
            self.serve_post()
        else:
            super().do_GET()
    
    def serve_index(self):
        """記事一覧ページ"""
        
        posts_dir = Path("_posts")
        posts_html = ""
        
        if posts_dir.exists():
            # 記事ファイルを日付順でソート
            post_files = sorted(posts_dir.glob("*.md"), reverse=True)
            
            for i, post_file in enumerate(post_files):
                try:
                    # ファイル名から日付とタイトルを抽出
                    filename = post_file.stem
                    date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.*)', filename)
                    
                    if date_match:
                        year, month, day, slug = date_match.groups()
                        display_date = f"{year}年{month}月{day}日"
                    else:
                        display_date = "日付不明"
                    
                    # ファイル内容を少し読んでタイトルを取得
                    content = post_file.read_text(encoding='utf-8')
                    title_match = re.search(r'title:\s*(.+)', content)
                    title = title_match.group(1).strip(' "\'') if title_match else filename
                    
                    # 記事のURL
                    post_url = f"/post/{i}"
                    
                    posts_html += f"""
                    <div class="post-card">
                        <h2><a href="{post_url}">{title}</a></h2>
                        <div class="post-meta">📅 {display_date} • 📝 動画から自動生成</div>
                        <div class="post-info">ファイル: {post_file.name}</div>
                    </div>
                    """
                except Exception as e:
                    print(f"記事読み込みエラー {post_file}: {e}")
        
        html = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🎬 Video Content System - ブログプレビュー</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🎬 Video Content System</h1>
                    <p>AI生成動画ブログのプレビュー</p>
                </header>
                
                <main>
                    {posts_html}
                </main>
                
                <footer>
                    <p>💡 記事をクリックして内容を確認できます</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_post(self):
        """個別記事表示"""
        
        try:
            # URLからインデックスを取得
            post_index = int(self.path.split('/')[-1])
            
            posts_dir = Path("_posts")
            post_files = sorted(posts_dir.glob("*.md"), reverse=True)
            
            if 0 <= post_index < len(post_files):
                post_file = post_files[post_index]
                content = post_file.read_text(encoding='utf-8')
                
                # タイトルを抽出
                title_match = re.search(r'title:\s*(.+)', content)
                title = title_match.group(1).strip(' "\'') if title_match else post_file.stem
                
                # Front Matterを除去
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        body_content = parts[2].strip()
                    else:
                        body_content = content
                else:
                    body_content = content
                
                html = f"""
                <!DOCTYPE html>
                <html lang="ja">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title} - Video Content System</title>
                    <link rel="stylesheet" href="/style.css">
                </head>
                <body>
                    <div class="container">
                        <header>
                            <h1>🎬 Video Content System</h1>
                            <p>AI生成動画ブログ</p>
                        </header>
                        
                        <nav>
                            <a href="/" class="nav-link">← 記事一覧に戻る</a>
                        </nav>
                        
                        <article class="post-content">
                            <h1>{title}</h1>
                            <div class="post-meta">📁 {post_file.name}</div>
                            
                            <div class="content">
                                {body_content}
                            </div>
                        </article>
                        
                        <nav>
                            <a href="/" class="nav-link">← 記事一覧に戻る</a>
                        </nav>
                    </div>
                </body>
                </html>
                """
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return
        
        except (ValueError, IndexError, FileNotFoundError):
            pass
        
        self.send_error(404, "記事が見つかりません")
    
    def serve_css(self):
        """CSSスタイル"""
        
        css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .post-card {
            background: white;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border-left: 5px solid #667eea;
        }
        
        .post-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .post-card h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #2c3e50;
        }
        
        .post-card h2 a {
            text-decoration: none;
            color: inherit;
            transition: color 0.2s ease;
        }
        
        .post-card h2 a:hover {
            color: #667eea;
        }
        
        .post-meta {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        
        .post-info {
            color: #888;
            font-size: 0.85rem;
            font-family: monospace;
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 5px;
            margin-top: 1rem;
        }
        
        .nav-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            border-radius: 25px;
            margin: 1rem 0;
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .post-content {
            background: white;
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin: 2rem 0;
        }
        
        .post-content h1 {
            color: #2c3e50;
            font-size: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #667eea;
        }
        
        .post-content h2 {
            color: #34495e;
            font-size: 1.5rem;
            margin: 2rem 0 1rem 0;
            padding-left: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .post-content h3 {
            color: #34495e;
            font-size: 1.2rem;
            margin: 1.5rem 0 0.8rem 0;
        }
        
        .post-content p {
            margin: 1rem 0;
            color: #444;
        }
        
        .post-content ol, .post-content ul {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        .post-content li {
            margin: 0.5rem 0;
            color: #444;
        }
        
        .post-content img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .post-content .featured-image {
            text-align: center;
            margin: 2rem 0;
        }
        
        .post-content .section-image {
            text-align: center;
            margin: 1.5rem 0;
        }
        
        .post-content .toc {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 2rem 0;
            border: 1px solid #e9ecef;
        }
        
        .post-content .article-footer {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            margin-top: 3rem;
            border-top: 3px solid #667eea;
        }
        
        footer {
            text-align: center;
            margin: 2rem 0;
            padding: 1rem;
            color: #666;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            header {
                padding: 1.5rem;
            }
            
            header h1 {
                font-size: 2rem;
            }
            
            .post-card {
                padding: 1.5rem;
            }
            
            .post-content {
                padding: 1.5rem;
            }
        }
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/css; charset=utf-8')
        self.end_headers()
        self.wfile.write(css.encode('utf-8'))


def main():
    """サーバー起動"""
    port = 8002
    server_address = ('', port)
    
    print(f"🚀 ブログプレビューサーバーを起動中...")
    print(f"📱 ブラウザで http://localhost:{port} を開いてください")
    print(f"🛑 終了するには Ctrl+C を押してください")
    print()
    
    httpd = HTTPServer(server_address, SimpleBlogHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ サーバーを停止しました")
        httpd.shutdown()


if __name__ == "__main__":
    main()