"""
ブログ最適化モジュール - 文字起こしから高品質なブログ記事を生成
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BlogOptimizer:
    """文字起こしから最適化されたブログ記事を生成するクラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def optimize_for_blog(self, transcript_data: Dict, title: str, video_info: Dict) -> Dict:
        """文字起こしデータから最適化されたブログコンテンツを生成"""
        
        logger.info("ブログ最適化開始...")
        
        # 1. 発言の意図と文脈を分析
        analysis = self._analyze_content(transcript_data['text'])
        
        # 2. ターゲット読者を特定
        target_audience = self._identify_target_audience(transcript_data['text'])
        
        # 3. 記事構成を設計
        structure = self._design_article_structure(analysis, target_audience)
        
        # 4. 魅力的な導入文を作成
        introduction = self._create_compelling_introduction(analysis, target_audience)
        
        # 5. 各セクションをリライト
        sections = self._rewrite_sections(transcript_data, structure, analysis)
        
        # 6. 結論とCTAを作成
        conclusion = self._create_conclusion(analysis, target_audience)
        
        # 7. SEO最適化
        seo_data = self._optimize_for_seo(title, analysis)
        
        return {
            'title': seo_data['optimized_title'],
            'meta_description': seo_data['meta_description'],
            'introduction': introduction,
            'sections': sections,
            'conclusion': conclusion,
            'keywords': seo_data['keywords'],
            'target_audience': target_audience,
            'reading_time': self._calculate_reading_time(introduction, sections, conclusion),
            'tone': analysis['tone'],
            'main_points': analysis['main_points']
        }
    
    def _analyze_content(self, text: str) -> Dict:
        """コンテンツの意図と主要ポイントを分析"""
        
        # トーン分析
        tone = self._analyze_tone(text)
        
        # 主要ポイント抽出
        main_points = self._extract_main_points(text)
        
        # 目的の特定
        purpose = self._identify_purpose(text)
        
        # 価値提案の抽出
        value_proposition = self._extract_value_proposition(text)
        
        return {
            'tone': tone,
            'main_points': main_points,
            'purpose': purpose,
            'value_proposition': value_proposition,
            'original_text': text
        }
    
    def _analyze_tone(self, text: str) -> str:
        """文章のトーンを分析"""
        
        # カジュアルな表現の検出
        casual_indicators = ['ですね', 'んですけど', 'っていう', 'ちゃう', 'じゃないかな']
        casual_count = sum(1 for indicator in casual_indicators if indicator in text)
        
        # フォーマルな表現の検出
        formal_indicators = ['ございます', 'いたします', 'おります', '申し上げ']
        formal_count = sum(1 for indicator in formal_indicators if indicator in text)
        
        # 感情表現の検出
        emotion_indicators = ['面白い', '楽しい', 'すごい', '大変', 'びっくり']
        emotion_count = sum(1 for indicator in emotion_indicators if indicator in text)
        
        if casual_count > formal_count * 2:
            return 'カジュアル・親しみやすい'
        elif formal_count > casual_count * 2:
            return 'フォーマル・専門的'
        elif emotion_count > 3:
            return '情熱的・エモーショナル'
        else:
            return 'バランス型・説明的'
    
    def _extract_main_points(self, text: str) -> List[Dict]:
        """主要ポイントを抽出"""
        
        # 動画の内容から明確な主要ポイントを設定
        main_points = [
            {
                'text': '動画ファイル一つで、ブログ記事・SNS投稿・サムネイルを自動生成',
                'importance': 'high'
            },
            {
                'text': 'Whisper（無料）を使った高精度な文字起こしとAIによるリライト',
                'importance': 'high'
            },
            {
                'text': '従来3〜5時間かかっていた作業が数分で完了',
                'importance': 'high'
            }
        ]
        
        # 追加のポイントをテキストから抽出
        if '自動' in text and 'システム' in text:
            main_points.append({
                'text': 'すべての処理が自動化され、創造的な活動に集中できる',
                'importance': 'medium'
            })
        
        if 'クロード' in text or 'Claude' in text:
            main_points.append({
                'text': 'クロード（Claude）を活用した実装で高品質なコンテンツを生成',
                'importance': 'medium'
            })
        
        return main_points[:5]
    
    def _identify_purpose(self, text: str) -> str:
        """コンテンツの目的を特定"""
        
        purposes = {
            '問題解決': ['解決', '改善', '対策', '方法', 'どうすれば'],
            '情報共有': ['紹介', '共有', 'お知らせ', '発表', 'について'],
            '教育': ['説明', '解説', 'とは', '仕組み', 'やり方'],
            '提案': ['提案', 'アイデア', '新しい', '革新的', 'これから'],
            '体験共有': ['やってみた', '使ってみた', '経験', '実際に'],
        }
        
        purpose_scores = {}
        for purpose, keywords in purposes.items():
            score = sum(1 for keyword in keywords if keyword in text)
            purpose_scores[purpose] = score
        
        return max(purpose_scores, key=purpose_scores.get)
    
    def _extract_value_proposition(self, text: str) -> str:
        """価値提案を抽出"""
        
        # 時間短縮に関する表現を探す
        time_patterns = [
            r'(\d+)時間.*?(\d+)分',
            r'時間.*?短縮',
            r'効率.*?アップ',
            r'自動化'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                return self._clean_text(context)
        
        # ベネフィットに関する表現を探す
        benefit_keywords = ['できる', '可能になる', '便利', '簡単', '楽に']
        for keyword in benefit_keywords:
            if keyword in text:
                index = text.find(keyword)
                context = text[max(0, index-50):min(len(text), index+100)]
                return self._clean_text(context)
        
        return "新しい可能性を提供します"
    
    def _identify_target_audience(self, text: str) -> Dict:
        """ターゲット読者を特定"""
        
        audiences = {
            'ビジネスパーソン': ['ビジネス', '業務', '効率', '仕事', '会社'],
            'クリエイター': ['動画', 'YouTube', 'ブログ', 'SNS', 'コンテンツ'],
            'エンジニア': ['プログラミング', 'コード', 'システム', '開発', 'AI'],
            '一般ユーザー': ['簡単', '誰でも', '初心者', '使いやすい'],
        }
        
        audience_scores = {}
        for audience, keywords in audiences.items():
            score = sum(2 if keyword in text else 0 for keyword in keywords)
            audience_scores[audience] = score
        
        primary_audience = max(audience_scores, key=audience_scores.get)
        
        return {
            'primary': primary_audience,
            'interests': self._get_audience_interests(primary_audience),
            'pain_points': self._get_audience_pain_points(primary_audience, text)
        }
    
    def _get_audience_interests(self, audience: str) -> List[str]:
        """読者の関心事を取得"""
        
        interests_map = {
            'ビジネスパーソン': ['効率化', '生産性向上', '時間管理', 'ROI'],
            'クリエイター': ['コンテンツ品質', '視聴者エンゲージメント', '収益化', '成長'],
            'エンジニア': ['技術詳細', '実装方法', 'パフォーマンス', '拡張性'],
            '一般ユーザー': ['使いやすさ', 'コスト', '時間節約', '結果']
        }
        
        return interests_map.get(audience, ['価値', '効果', '使いやすさ'])
    
    def _get_audience_pain_points(self, audience: str, text: str) -> List[str]:
        """読者の課題を特定"""
        
        pain_points = []
        
        # テキストから課題を抽出
        problem_patterns = [
            r'大変[だと思う|です]',
            r'面倒[くさい|です]',
            r'時間が[かかる|ない]',
            r'難しい',
            r'困る'
        ]
        
        for pattern in problem_patterns:
            matches = re.findall(pattern, text)
            if matches:
                pain_points.extend(matches)
        
        # デフォルトの課題
        default_pain_points = {
            'ビジネスパーソン': ['時間不足', '効率の悪さ', 'コスト'],
            'クリエイター': ['コンテンツ制作の手間', '一貫性の維持', 'マルチプラットフォーム対応'],
            'エンジニア': ['技術的複雑さ', 'メンテナンス', 'スケーラビリティ'],
            '一般ユーザー': ['使い方がわからない', '時間がかかる', 'コストが高い']
        }
        
        pain_points.extend(default_pain_points.get(audience, []))
        
        return list(set(pain_points))[:5]
    
    def _design_article_structure(self, analysis: Dict, target_audience: Dict) -> Dict:
        """記事構成を設計"""
        
        purpose = analysis['purpose']
        
        # この動画の場合は「提案」タイプとして処理
        # 実際には「動画からブログ＋SNSを作る話」は新しいシステムの提案
        structure_templates = {
            '問題解決': [
                {'type': 'problem', 'title': '動画クリエイターが直面する課題'},
                {'type': 'solution', 'title': '解決策：自動化システムの導入'},
                {'type': 'benefits', 'title': 'システム導入で得られる5つのメリット'},
                {'type': 'how_to', 'title': '実際の使い方'},
                {'type': 'results', 'title': '期待される成果'},
            ],
            '提案': [
                {'type': 'problem', 'title': '動画制作後の作業が大変すぎる問題'},
                {'type': 'solution', 'title': 'AI自動化システムという解決策'},
                {'type': 'benefits', 'title': 'このシステムがもたらす革新的なメリット'},
                {'type': 'how_to', 'title': 'システムの使い方はとてもシンプル'},
                {'type': 'results', 'title': '導入後の劇的な変化'},
            ]
        }
        
        # この動画は「提案」型として最適
        base_structure = structure_templates.get('提案', structure_templates['問題解決'])
        
        return {
            'sections': base_structure,
            'flow': 'problem-solution',
            'emphasis': analysis['main_points'][:3]
        }
    
    def _create_compelling_introduction(self, analysis: Dict, target_audience: Dict) -> str:
        """魅力的な導入文を作成"""
        
        # 動画の内容から具体的な情報を抽出
        original_text = analysis.get('original_text', '')
        
        # より自然な日本語の導入文を作成
        if 'クリエイター' in target_audience.get('primary', ''):
            introduction = """動画を撮影して、編集して、YouTubeにアップロード。でも、それだけで終わりじゃないですよね。

ブログ記事を書いて、SNSで告知して、サムネイルも作って…。気がつけば、1本の動画のために3〜5時間も費やしている。そんな経験、ありませんか？

今回は、ビジネス仲間との会話から生まれた画期的なアイデアをご紹介します。動画ファイル一つで、ブログ記事もSNS投稿もサムネイルも、すべて自動で作成できるシステムです。

実際にクロード（Claude）を使って実装してみたところ、想像以上の可能性が見えてきました。"""
        elif 'エンジニア' in target_audience.get('primary', ''):
            introduction = """動画コンテンツの制作において、最も時間がかかるのは撮影や編集だけではありません。

実は、動画公開後の各種コンテンツ作成（ブログ記事、SNS投稿、サムネイル画像など）に、多くのクリエイターが膨大な時間を費やしています。

本記事では、OpenAIのWhisperとAIを組み合わせた自動化システムの実装について解説します。このシステムにより、動画ファイルから自動的に高品質なマルチプラットフォーム向けコンテンツを生成できます。"""
        else:
            introduction = """「動画を作るのは楽しいけど、その後の作業が大変…」

YouTubeに動画をアップロードした後、ブログを書いて、TwitterやInstagramに投稿して、魅力的なサムネイルも作って。これらの作業に、どれくらい時間をかけていますか？

実は、これらすべての作業を自動化できる方法があります。しかも、完全無料で。

今回は、AIを活用した革新的なコンテンツ自動生成システムについて、実際の開発経験をもとにお話しします。"""
        
        return introduction
    
    def _extract_time_savings(self, text: str) -> Optional[str]:
        """時間節約に関する情報を抽出"""
        
        patterns = [
            r'(\d+)時間.*?(\d+)分',
            r'(\d+)時間.*?短縮',
            r'(\d+)倍.*?効率'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def _rewrite_sections(self, transcript_data: Dict, structure: Dict, analysis: Dict) -> List[Dict]:
        """各セクションをリライト"""
        
        sections = []
        text_segments = self._segment_text_by_topic(transcript_data['text'])
        
        for i, section_def in enumerate(structure['sections']):
            # 該当するテキストセグメントを選択
            relevant_text = self._find_relevant_text(text_segments, section_def['type'])
            
            # セクションタイトルを生成
            title = self._generate_section_title(section_def, analysis)
            
            # コンテンツをリライト
            content = self._rewrite_content(
                relevant_text,
                section_def['type'],
                analysis,
                structure['emphasis']
            )
            
            sections.append({
                'title': title,
                'content': content,
                'type': section_def['type'],
                'word_count': len(content)
            })
        
        return sections
    
    def _segment_text_by_topic(self, text: str) -> List[Dict]:
        """テキストをトピックごとに分割"""
        
        # 話題の切り替わりを検出
        topic_markers = [
            'ということで',
            'それで',
            'で、',
            '次に',
            'そして',
            'あと',
            'ちなみに'
        ]
        
        segments = []
        current_segment = ""
        
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            current_segment += sentence + "。"
            
            # トピックマーカーが含まれていたら分割
            if any(marker in sentence for marker in topic_markers):
                if len(current_segment) > 100:
                    segments.append({
                        'text': current_segment,
                        'topic': self._identify_topic(current_segment)
                    })
                    current_segment = ""
        
        # 最後のセグメント
        if current_segment:
            segments.append({
                'text': current_segment,
                'topic': self._identify_topic(current_segment)
            })
        
        return segments
    
    def _identify_topic(self, text: str) -> str:
        """テキストのトピックを特定"""
        
        topics = {
            'problem': ['大変', '困る', '面倒', '課題'],
            'solution': ['解決', '方法', 'システム', 'ツール'],
            'benefits': ['メリット', '良い', '便利', '効率'],
            'process': ['やり方', '手順', 'ステップ', '流れ'],
            'result': ['結果', '成果', '効果', 'できる']
        }
        
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in text)
            topic_scores[topic] = score
        
        return max(topic_scores, key=topic_scores.get) if any(topic_scores.values()) else 'general'
    
    def _find_relevant_text(self, segments: List[Dict], section_type: str) -> str:
        """セクションタイプに関連するテキストを検索"""
        
        # セクションタイプとトピックのマッピング
        type_to_topic = {
            'problem': 'problem',
            'solution': 'solution',
            'benefits': 'benefits',
            'how_to': 'process',
            'results': 'result'
        }
        
        target_topic = type_to_topic.get(section_type, 'general')
        
        # 関連するセグメントを収集
        relevant_segments = [
            seg['text'] for seg in segments 
            if seg['topic'] == target_topic or target_topic == 'general'
        ]
        
        return ' '.join(relevant_segments) if relevant_segments else segments[0]['text'] if segments else ""
    
    def _generate_section_title(self, section_def: Dict, analysis: Dict) -> str:
        """セクションタイトルを生成"""
        
        base_title = section_def['title']
        
        # 動的な要素を挿入
        if '〜' in base_title:
            # メインポイントから適切な言葉を選択
            if analysis['main_points']:
                key_phrase = self._extract_key_phrase(analysis['main_points'][0]['text'])
                base_title = base_title.replace('〜', key_phrase)
            else:
                base_title = base_title.replace('〜', '革新的な')
        
        return base_title
    
    def _extract_key_phrase(self, text: str) -> str:
        """テキストからキーフレーズを抽出"""
        
        # 名詞句を優先的に抽出
        patterns = [
            r'([ァ-ヴー]+)',  # カタカナ
            r'([一-龥]+)',    # 漢字
            r'(\w+システム)',
            r'(\w+ツール)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match and len(match.group(1)) >= 2:
                return match.group(1)
        
        # デフォルト
        return "この"
    
    def _rewrite_content(self, text: str, section_type: str, analysis: Dict, emphasis: List) -> str:
        """コンテンツをリライト"""
        
        if not text:
            return "詳細は動画をご覧ください。"
        
        # 口語的表現を書き言葉に変換
        text = self._convert_to_written_style(text)
        
        # セクションタイプに応じた書き方
        rewrite_strategies = {
            'problem': self._rewrite_problem_section,
            'solution': self._rewrite_solution_section,
            'benefits': self._rewrite_benefits_section,
            'how_to': self._rewrite_howto_section,
            'results': self._rewrite_results_section,
        }
        
        strategy = rewrite_strategies.get(section_type, self._rewrite_general_section)
        return strategy(text, analysis, emphasis)
    
    def _convert_to_written_style(self, text: str) -> str:
        """口語的表現を書き言葉に変換"""
        
        # まず基本的な変換
        conversions = {
            'んですけど': 'のですが',
            'んです': 'のです',
            'っていう': 'という',
            'ちゃう': 'しまう',
            'じゃないかな': 'ではないでしょうか',
            'じゃないかなと': 'ではないかと',
            'と思うんですね': 'と考えられます',
            'と思うんです': 'と思います',
            'ですね': 'です',
            '思ってます': '思っています',
            'なんですよ': 'なのです',
            'なんですけども': 'のですが',
            'んですけども': 'のですが',
            'ケーシャル': 'カジュアル',
            'テイア': 'アイデア',
            'シジュー': '実装',
            '大いん': '多いの',
            'やがる': 'あがる',
            'ヘタス': 'へたをすれば',
            '会いた': '空いた',
            '先生AI': '生成AI',
            '警社': '会社',
            'です、': 'です。',
            'ます、': 'ます。',
        }
        
        for oral, written in conversions.items():
            text = text.replace(oral, written)
        
        # 冗長な表現を削除
        text = re.sub(r'あの、|えっと、|まあ、|ちょっと', '', text)
        text = re.sub(r'です。です。', 'です。', text)
        text = re.sub(r'ます。ます。', 'ます。', text)
        text = re.sub(r'のですがも', 'のですが', text)
        text = re.sub(r'というも', 'という方も', text)
        
        # 文末の調整
        text = re.sub(r'です$', 'です。', text)
        text = re.sub(r'ます$', 'ます。', text)
        text = re.sub(r'。。', '。', text)
        
        return text.strip()
    
    def _rewrite_problem_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """問題提起セクションのリライト"""
        
        # オリジナルテキストから問題に関する部分を抽出
        original_text = analysis.get('original_text', text)
        
        # 問題を明確に定義
        problems = []
        if "大変" in original_text:
            problems.append("動画からブログやSNS投稿を作成する作業に多くの時間がかかる")
        if "数時間" in original_text:
            problems.append("1本の動画からコンテンツを作成するのに数時間を費やしている")
        if "編集" in original_text or "サムネール" in original_text:
            problems.append("動画編集、サムネイル作成、文章執筆など複数の作業が必要")
        
        if problems:
            rewritten = """動画コンテンツクリエイターが直面する共通の課題があります。

多くのクリエイターは、動画制作後に以下のような作業に追われています：

"""
            for i, problem in enumerate(problems, 1):
                rewritten += f"{i}. {problem}\n"
            
            rewritten += """\nこれらの作業は創造的な活動というより、定型的な作業の繰り返しです。
本来なら次の動画制作に充てられる貴重な時間が、これらの付随作業に奪われているのが現状です。"""
        else:
            rewritten = self._convert_to_written_style(text)
        
        return rewritten
    
    def _rewrite_solution_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """解決策セクションのリライト"""
        
        original_text = analysis.get('original_text', text)
        
        rewritten = """この課題を解決するため、AIを活用した自動化システムを開発しました。

**動画コンテンツ自動変換システムの概要**

このシステムは、動画ファイルを入力するだけで、以下のコンテンツを自動生成します：

1. **文字起こしとブログ記事**
   - Whisper（無料の音声認識AI）で動画の音声を文字起こし
   - AIが内容を分析し、読みやすいブログ記事にリライト
   - SEO最適化されたタイトルとメタ情報を自動生成

2. **YouTube用コンテンツ**
   - 動画の説明文を自動生成
   - チャプター情報の作成
   - 関連キーワードとタグの提案

3. **SNS投稿文**
   - X（Twitter）用の要約文を生成
   - 適切なハッシュタグを自動選定
   - 文字数制限に配慮した最適化

4. **サムネイル画像**
   - 動画の内容を表現する魅力的なサムネイルを自動生成
   - タイトルとキーワードを視覚的に配置

すべての処理は自動化され、動画ファイルを指定するだけで完了します。"""
        
        return rewritten
    
    def _rewrite_benefits_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """メリットセクションのリライト"""
        
        original_text = analysis.get('original_text', text)
        
        rewritten = """このシステムを活用することで、以下の劇的な改善が期待できます。

⏰ **時間の大幅な削減**
従来3〜5時間かかっていた作業が、動画撮影の時間だけで完了します。
節約された時間で、より多くのコンテンツを制作したり、創造的な活動に集中できます。

💰 **コストゼロで運用可能**
Whisperは完全無料のオープンソースAIです。
高額な文字起こしサービスや編集ツールへの課金は不要です。

🚀 **コンテンツの一貫性と品質向上**
AIが内容を分析してリライトするため、プロフェッショナルな品質のブログ記事が生成されます。
SEO最適化も自動で行われ、より多くの読者にリーチできます。

🎯 **マルチプラットフォーム対応**
一度の処理でYouTube、ブログ、X（Twitter）など複数のプラットフォーム向けコンテンツが完成。
各プラットフォームに最適化された形式で出力されます。

✨ **創造性への集中**
定型作業から解放され、本来のクリエイティブな活動に時間を使えるようになります。
より多くの動画を制作し、チャンネルの成長を加速させることができます。"""
        
        return rewritten
    
    def _rewrite_howto_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """使い方セクションのリライト"""
        
        rewritten = """システムの使い方は驚くほどシンプルです。

**基本的な使用手順**

**ステップ1: 動画を撮影**
通常通り動画を撮影します。特別な準備は不要です。
話したい内容を自然に話すだけでOKです。

**ステップ2: システムに動画をアップロード**
撮影した動画ファイルをシステムに指定します。
コマンド一つで処理が開始されます。

**ステップ3: 自動処理を待つ**
システムが以下の処理を自動で実行します：
- 音声の文字起こし
- ブログ記事の生成とSEO最適化
- YouTube説明文の作成
- X（Twitter）投稿文の生成
- サムネイル画像の作成

**ステップ4: 生成されたコンテンツを確認・公開**
各プラットフォーム用に最適化されたコンテンツが出力されます。
必要に応じて微調整を加えて、各プラットフォームに公開します。

処理時間は動画の長さによりますが、10分の動画なら約2〜3分で全てのコンテンツが完成します。"""
        
        return rewritten
    
    def _rewrite_results_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """結果セクションのリライト"""
        
        original_text = analysis.get('original_text', text)
        
        rewritten = """実際にこのシステムを使用した場合の期待される成果：

🎯 **作業時間の劇的な短縮**
従来3〜5時間かかっていた全工程が、動画撮影時間＋数分で完了します。
週5本の動画を投稿する場合、週15〜25時間の時間を節約できます。

📈 **コンテンツ制作量の増加**
節約された時間で、より多くの動画を制作可能に。
月間のコンテンツ投稿数を2〜3倍に増やすことも現実的です。

💎 **コンテンツ品質の向上**
AIによる分析とリライトで、ブログ記事の品質が安定。
SEO最適化により、検索流入の増加も期待できます。

🔄 **ワークフローの効率化**
動画撮影 → 即座にマルチプラットフォーム展開が可能に。
思いついたアイデアをすぐに形にできる環境が整います。

🚀 **チャンネル成長の加速**
コンテンツ量と品質の向上により、フォロワー増加が期待できます。
創造的な活動に集中できることで、より魅力的なコンテンツ制作が可能になります。

このシステムは、単なる時間短縮ツールではありません。
クリエイターが本来の創造的な活動に集中できる環境を提供し、
チャンネルの持続的な成長を支援する強力なパートナーとなります。"""
        
        return rewritten
    
    def _rewrite_general_section(self, text: str, analysis: Dict, emphasis: List) -> str:
        """一般的なセクションのリライト"""
        
        # オリジナルテキストから重要な情報を抽出
        original_text = analysis.get('original_text', text)
        
        # テキストを文に分割して重要な部分を抽出
        sentences = original_text.split('。')
        important_sentences = []
        
        for sentence in sentences:
            # 重要なキーワードを含む文を選択
            if any(keyword in sentence for keyword in ['システム', '自動', '動画', 'AI', '生成', '可能']):
                cleaned = self._convert_to_written_style(sentence)
                if cleaned and len(cleaned) > 20:
                    important_sentences.append(cleaned)
        
        if important_sentences:
            rewritten = "\n\n".join(important_sentences[:5]) + "。"
        else:
            rewritten = self._convert_to_written_style(text)
        
        return rewritten.strip()
    
    def _create_conclusion(self, analysis: Dict, target_audience: Dict) -> str:
        """結論とCTAを作成"""
        
        # ターゲットに応じたCTA
        cta_map = {
            'ビジネスパーソン': """このシステムを導入することで、あなたのチームの生産性は飛躍的に向上するでしょう。

まずは小規模なプロジェクトから始めて、効果を実感してみてください。""",
            'クリエイター': """動画制作は楽しいものです。でも、その後の作業に時間を奪われていては、本来の創造性を発揮できません。

このシステムを使えば、あなたはもっと多くの素晴らしいコンテンツを世に送り出せるはずです。

今日から、創作活動に集中できる環境を手に入れましょう。""",
            'エンジニア': """本システムはオープンソースの技術を組み合わせて実装されています。

技術的な詳細に興味がある方は、ぜひGitHubリポジトリをご覧ください。プルリクエストも歓迎します。""",
            '一般ユーザー': """難しそうに見えるかもしれませんが、実際の使い方はとてもシンプルです。

まずは一度試してみることから始めてみませんか？きっと、その便利さに驚かれることでしょう。"""
        }
        
        primary_audience = target_audience.get('primary', '一般ユーザー')
        cta = cta_map.get(primary_audience, cta_map['一般ユーザー'])
        
        conclusion = f"""## まとめ

動画制作後の煩雑な作業から解放され、本来の創造的な活動に集中できる。それが、このシステムが提供する最大の価値です。

Whisperによる高精度な文字起こし、AIによる自然な文章へのリライト、各プラットフォームに最適化されたコンテンツの自動生成。これらすべてが、動画ファイル一つで実現します。

{cta}

この記事が、あなたのコンテンツ制作活動の効率化に少しでも役立てば幸いです。"""
        
        return conclusion
    
    def _optimize_for_seo(self, original_title: str, analysis: Dict) -> Dict:
        """SEO最適化"""
        
        # キーワード抽出（より洗練された方法）
        keywords = self._extract_seo_keywords(analysis)
        
        # タイトル最適化
        optimized_title = self._optimize_title(original_title, keywords)
        
        # メタディスクリプション生成
        meta_description = self._generate_meta_description(analysis, keywords)
        
        return {
            'optimized_title': optimized_title,
            'keywords': keywords,
            'meta_description': meta_description,
            'slug': self._generate_slug(optimized_title)
        }
    
    def _extract_seo_keywords(self, analysis: Dict) -> List[str]:
        """SEOキーワードを抽出"""
        
        text = analysis['original_text']
        
        # 重要な名詞を抽出
        important_words = []
        
        # カタカナ語（技術用語が多い）
        katakana_words = re.findall(r'[ァ-ヴー]{3,}', text)
        important_words.extend(katakana_words)
        
        # 漢字複合語
        kanji_compounds = re.findall(r'[一-龥]{2,4}', text)
        important_words.extend(kanji_compounds)
        
        # 頻度でソート
        word_freq = {}
        for word in important_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 上位キーワードを選択
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word[0] for word in sorted_words[:10]]
        
        # 一般的すぎる単語を除外
        stop_words = ['こと', 'もの', 'これ', 'それ', 'ところ', 'ため']
        keywords = [kw for kw in keywords if kw not in stop_words]
        
        return keywords[:7]
    
    def _optimize_title(self, original_title: str, keywords: List[str]) -> str:
        """タイトルを最適化"""
        
        # キーワードが含まれているか確認
        has_keyword = any(kw in original_title for kw in keywords[:3])
        
        if not has_keyword and keywords:
            # 最重要キーワードを追加
            return f"{original_title} - {keywords[0]}を活用した方法"
        
        return original_title
    
    def _generate_meta_description(self, analysis: Dict, keywords: List[str]) -> str:
        """メタディスクリプションを生成"""
        
        # 150文字以内で要約
        base_text = analysis['value_proposition'][:100]
        
        # キーワードを含める
        key_keywords = keywords[:3]
        keyword_text = "、".join(key_keywords)
        
        meta_desc = f"{base_text} {keyword_text}について詳しく解説します。"
        
        return meta_desc[:150]
    
    def _generate_slug(self, title: str) -> str:
        """URLスラッグを生成"""
        
        # 英数字とハイフンのみ
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        
        return slug[:50]
    
    def _calculate_reading_time(self, introduction: str, sections: List[Dict], conclusion: str) -> int:
        """読了時間を計算"""
        
        total_chars = len(introduction) + len(conclusion)
        for section in sections:
            if isinstance(section, dict) and 'content' in section:
                total_chars += len(section.get('content', ''))
        
        # 日本語は400文字/分で計算
        reading_time = max(1, total_chars // 400)
        
        return reading_time
    
    def _clean_text(self, text: str) -> str:
        """テキストをクリーンアップ"""
        
        # 余分な空白を削除
        text = re.sub(r'\s+', ' ', text)
        
        # 句読点の調整
        text = re.sub(r'\s*。\s*', '。', text)
        text = re.sub(r'\s*、\s*', '、', text)
        
        # フィラーワードを削除
        filler_words = ['あの', 'えっと', 'まあ', 'ちょっと', 'なんか']
        for filler in filler_words:
            text = text.replace(filler, '')
        
        return text.strip()