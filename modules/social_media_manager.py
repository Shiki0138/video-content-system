"""
ソーシャルメディア投稿管理モジュール
X（Twitter）への投稿と連携機能を提供
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class XPostGenerator:
    """X（Twitter）投稿生成クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_length = config.get('max_length', 140)  # 日本語は140文字
        self.thread_mode = config.get('thread_mode', False)
        self.include_link = config.get('include_link', True)
        self.hashtag_strategy = config.get('hashtag_strategy', 'smart')
        
    def generate_post_variations(self, blog_content: Dict, video_info: Dict) -> Dict[str, str]:
        """複数のX投稿バリエーションを生成"""
        
        logger.info("X投稿バリエーション生成開始...")
        
        # ブログの要点を抽出
        key_points = self._extract_key_points(blog_content)
        
        variations = {
            'hook_style': self._generate_hook_style(blog_content, key_points),
            'benefit_style': self._generate_benefit_style(blog_content, key_points),
            'question_style': self._generate_question_style(blog_content, key_points),
            'statistics_style': self._generate_statistics_style(blog_content, key_points),
            'announcement_style': self._generate_announcement_style(blog_content, key_points)
        }
        
        # スレッド形式も生成
        if self.thread_mode:
            variations['thread'] = self._generate_thread(blog_content, key_points)
        
        return variations
    
    def _extract_key_points(self, blog_content: Dict) -> List[Dict]:
        """ブログから要点を抽出"""
        
        key_points = []
        
        # メインポイントから抽出
        if blog_content.get('main_points'):
            for point in blog_content['main_points'][:3]:
                key_points.append({
                    'text': point['text'],
                    'type': 'main',
                    'emoji': self._get_emoji_for_point(point['text'])
                })
        
        # メリットから抽出
        if blog_content.get('sections'):
            for section in blog_content['sections']:
                if section.get('type') == 'benefits':
                    # メリットセクションから重要な数値を抽出
                    numbers = re.findall(r'(\d+)[\s]*(?:時間|分|倍|％)', section.get('content', ''))
                    if numbers:
                        key_points.append({
                            'text': f"{numbers[0]}の改善",
                            'type': 'statistic',
                            'emoji': '📊'
                        })
        
        return key_points
    
    def _generate_hook_style(self, blog_content: Dict, key_points: List[Dict]) -> str:
        """フック型投稿を生成"""
        
        title = blog_content.get('title', '')
        hook = "動画制作者必見！"
        
        main_benefit = "動画ファイル1つで、ブログ・SNS投稿・サムネイルが自動生成"
        
        post = f"""{hook}

{main_benefit}

✅ Whisper（無料）で文字起こし
✅ AIが自動でリライト
✅ 作業時間を3-5時間→数分に短縮

詳細はブログで👇
"""
        
        # 文字数調整
        if self.include_link:
            post = self._adjust_length_with_link(post)
        
        # ハッシュタグ追加
        hashtags = self._generate_hashtags(blog_content)
        post = self._add_hashtags(post, hashtags)
        
        return post
    
    def _generate_benefit_style(self, blog_content: Dict, key_points: List[Dict]) -> str:
        """ベネフィット型投稿を生成"""
        
        post = """【もう動画の後処理で消耗しない】

従来：動画撮影→編集→ブログ執筆→SNS投稿→サムネ作成
👉 3〜5時間の作業

これから：動画撮影→自動化システム
👉 数分で全て完成

空いた時間で次の動画制作へ💪

仕組みの詳細→"""
        
        if self.include_link:
            post = self._adjust_length_with_link(post)
        
        hashtags = ['動画制作', 'AI活用', '時短術']
        post = self._add_hashtags(post, hashtags[:2])
        
        return post
    
    def _generate_question_style(self, blog_content: Dict, key_points: List[Dict]) -> str:
        """質問型投稿を生成"""
        
        post = """動画投稿後、こんな作業してませんか？

☑️ ブログ記事を1から書く
☑️ SNS用に要約文を作成
☑️ サムネイルをデザイン
☑️ 各プラットフォームに最適化

実はこれ、全部自動化できます。

その方法とは？→"""
        
        if self.include_link:
            post = self._adjust_length_with_link(post)
        
        return post
    
    def _generate_statistics_style(self, blog_content: Dict, key_points: List[Dict]) -> str:
        """統計型投稿を生成"""
        
        post = """【数字で見る動画制作の効率化】

Before:
・ブログ執筆：90分
・SNS投稿作成：30分  
・サムネ制作：60分
計：3時間

After:
・全自動処理：3分
⏰ 97%の時間削減

実現方法を解説↓"""
        
        if self.include_link:
            post = self._adjust_length_with_link(post)
        
        hashtags = ['生産性向上', 'DX']
        post = self._add_hashtags(post, hashtags)
        
        return post
    
    def _generate_announcement_style(self, blog_content: Dict, key_points: List[Dict]) -> str:
        """告知型投稿を生成"""
        
        post = """🎬 新記事公開

「動画からブログ＋SNSを作る話」

動画ファイル1つで
・ブログ記事（SEO最適化済）
・YouTube説明文
・SNS投稿文
・サムネイル画像

すべて自動生成する仕組みを解説しました。

▼詳細はこちら"""
        
        if self.include_link:
            post = self._adjust_length_with_link(post)
        
        return post
    
    def _generate_thread(self, blog_content: Dict, key_points: List[Dict]) -> List[str]:
        """スレッド形式の投稿を生成"""
        
        thread = []
        
        # 1つ目：フック
        thread.append("""動画クリエイターの皆さん、
動画投稿後の作業、大変じゃないですか？

ブログ書いて、SNS投稿作って、サムネイル作って...

実は、これ全部自動化できるんです。

その方法を解説します🧵""")
        
        # 2つ目：問題提起
        thread.append("""多くのクリエイターが直面する問題：

1️⃣ 1本の動画から派生コンテンツ作成に3-5時間
2️⃣ 各プラットフォームごとに最適化が必要
3️⃣ 本来の創作活動の時間が削られる

これ、AIで解決できます。""")
        
        # 3つ目：解決策
        thread.append("""解決策：動画自動変換システム

🎯 Whisper（無料）で文字起こし
🎯 AIがブログ記事にリライト
🎯 各SNS用に最適化
🎯 サムネイルも自動生成

動画ファイルを入力するだけ！""")
        
        # 4つ目：メリット
        thread.append("""導入メリット：

✅ 作業時間97%削減
✅ 完全無料で運用可能
✅ SEO最適化済みコンテンツ
✅ マルチプラットフォーム対応

浮いた時間で、より多くの動画制作が可能に。""")
        
        # 5つ目：CTA
        cta = """詳しい実装方法はブログで解説しています。

気になる方はぜひチェックしてみてください👇
"""
        if self.include_link:
            cta += "\n[ブログURL]"
        
        thread.append(cta)
        
        return thread
    
    def _adjust_length_with_link(self, post: str, link_placeholder: str = "[ブログURL]") -> str:
        """リンク用のスペースを考慮して文字数調整"""
        
        # URLは23文字として計算（t.co短縮URL）
        url_length = 23
        available_length = self.max_length - url_length - 1  # スペース分
        
        if len(post) > available_length:
            # 省略記号を含めて調整
            post = post[:available_length - 3] + "..."
        
        return post
    
    def _generate_hashtags(self, blog_content: Dict) -> List[str]:
        """適切なハッシュタグを生成"""
        
        hashtags = []
        
        # キーワードから生成
        keywords = blog_content.get('keywords', [])
        for keyword in keywords[:3]:
            if len(keyword) <= 10:  # 長すぎないもののみ
                hashtags.append(keyword)
        
        # デフォルトハッシュタグ
        default_tags = ['動画制作', 'AI活用', 'ブログ自動化', '時短']
        
        # スマート選択
        if self.hashtag_strategy == 'smart':
            # 文脈に応じて選択
            if 'Whisper' in str(blog_content):
                hashtags.append('Whisper')
            if 'Claude' in str(blog_content):
                hashtags.append('Claude')
        
        # 重複を除いて返す
        return list(dict.fromkeys(hashtags + default_tags))[:4]
    
    def _add_hashtags(self, post: str, hashtags: List[str]) -> str:
        """投稿にハッシュタグを追加"""
        
        hashtag_text = ' '.join([f'#{tag}' for tag in hashtags])
        
        # 文字数チェック
        if len(post) + len(hashtag_text) + 2 <= self.max_length:
            return f"{post}\n\n{hashtag_text}"
        
        return post
    
    def _get_emoji_for_point(self, text: str) -> str:
        """ポイントに適した絵文字を選択"""
        
        emoji_map = {
            '時間': '⏰',
            '自動': '🤖',
            '無料': '💰',
            '簡単': '👍',
            '効率': '🚀',
            'AI': '🧠',
            '動画': '🎬',
            'ブログ': '📝'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in text:
                return emoji
        
        return '✨'


class SocialMediaScheduler:
    """ソーシャルメディア投稿スケジューラー"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.schedule_file = Path(config.get('schedule_file', 'social_schedule.json'))
        
    def schedule_post(self, post_data: Dict, platform: str = 'x') -> Dict:
        """投稿をスケジュールに追加"""
        
        scheduled_post = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'platform': platform,
            'content': post_data,
            'scheduled_at': datetime.now().isoformat(),
            'status': 'pending',
            'blog_url': post_data.get('blog_url', ''),
            'video_url': post_data.get('video_url', '')
        }
        
        # スケジュールファイルに追加
        schedule = self._load_schedule()
        schedule['posts'].append(scheduled_post)
        self._save_schedule(schedule)
        
        logger.info(f"✓ 投稿をスケジュールに追加: {scheduled_post['id']}")
        
        return scheduled_post
    
    def _load_schedule(self) -> Dict:
        """スケジュールファイルを読み込み"""
        
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'posts': []}
    
    def _save_schedule(self, schedule: Dict):
        """スケジュールファイルを保存"""
        
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)


class XPostAutomation:
    """X自動投稿機能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_credentials = config.get('api_credentials', {})
        
    def post_to_x(self, content: str, media_paths: Optional[List[Path]] = None) -> Dict:
        """Xに投稿（実装はAPI認証が必要）"""
        
        # 注意：実際の投稿にはTwitter API v2の認証が必要
        logger.warning("X API認証が設定されていません。手動投稿用のテキストを生成しました。")
        
        return {
            'status': 'manual_required',
            'content': content,
            'instruction': 'このテキストをコピーしてXに手動で投稿してください。'
        }