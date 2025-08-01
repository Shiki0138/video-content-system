#!/usr/bin/env python3
"""
設定管理モジュール
ユーザーがWebUIで画像生成APIキーを設定・管理するための機能
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class ConfigManager:
    """設定ファイルの管理とAPI設定の更新"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.local_config_path = Path("config.local.yaml")
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み（メイン設定とローカル設定をマージ）"""
        try:
            # メイン設定ファイルを読み込み
            config = {}
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # ローカル設定ファイルを読み込み（機密情報）
            if self.local_config_path.exists():
                with open(self.local_config_path, 'r', encoding='utf-8') as f:
                    local_config = yaml.safe_load(f) or {}
                    
                # ローカル設定をメイン設定にマージ
                config = self._deep_merge(config, local_config)
                self.logger.info("ローカル設定ファイルを読み込みました")
            
            return config
            
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """辞書の深いマージ"""
        result = base_dict.copy()
        
        for key, value in update_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self) -> bool:
        """設定ファイルを保存"""
        try:
            # バックアップ作成
            backup_path = self.config_path.with_suffix('.yaml.backup')
            if self.config_path.exists():
                import shutil
                shutil.copy2(self.config_path, backup_path)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info("設定ファイルを正常に保存しました")
            return True
            
        except Exception as e:
            self.logger.error(f"設定ファイル保存エラー: {e}")
            return False
    
    def get_api_settings(self) -> Dict[str, Any]:
        """現在のAPI設定を取得"""
        return self.config.get('thumbnail', {}).get('api_settings', {})
    
    def update_dalle3_settings(self, settings: Dict[str, Any]) -> bool:
        """DALL-E 3 API設定を更新（ローカル設定ファイルに保存）"""
        try:
            # ローカル設定ファイルを読み込み
            local_config = {}
            if self.local_config_path.exists():
                with open(self.local_config_path, 'r', encoding='utf-8') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # 構造を初期化
            if 'thumbnail' not in local_config:
                local_config['thumbnail'] = {}
            if 'dalle3' not in local_config['thumbnail']:
                local_config['thumbnail']['dalle3'] = {}
            
            # DALL-E 3設定を更新
            local_config['thumbnail']['dalle3'] = settings
            
            # DALL-E 2も同じAPIキーを使用（コスト効率のため）
            if 'dalle2' not in local_config['thumbnail']:
                local_config['thumbnail']['dalle2'] = {}
            local_config['thumbnail']['dalle2']['api_key'] = settings.get('api_key', '')
            
            # ローカル設定ファイルに保存
            success = self._save_local_config(local_config)
            
            if success:
                # メイン設定の画像プロバイダーを更新
                if 'thumbnail' not in self.config:
                    self.config['thumbnail'] = {}
                if 'image_providers' not in self.config['thumbnail']:
                    self.config['thumbnail']['image_providers'] = {}
                
                # デフォルト設定: サムネイル=DALL-E 3, ブログ=DALL-E 2
                self.config['thumbnail']['image_providers'].update({
                    'youtube_thumbnails': 'dalle3',
                    'blog_featured': 'dalle3',
                    'blog_sections': 'dalle2'
                })
                self._save_config()
                
                # 設定を再読み込み
                self.config = self._load_config()
                self.logger.info("DALL-E 3 API設定をローカル設定ファイルに保存しました")
            
            return success
            
        except Exception as e:
            self.logger.error(f"DALL-E 3 API設定更新エラー: {e}")
            return False

    def update_runware_settings(self, settings: Dict[str, Any]) -> bool:
        """Runware API設定を更新（ローカル設定ファイルに保存）"""
        try:
            # ローカル設定ファイルを読み込み
            local_config = {}
            if self.local_config_path.exists():
                with open(self.local_config_path, 'r', encoding='utf-8') as f:
                    local_config = yaml.safe_load(f) or {}
            
            # 構造を初期化
            if 'thumbnail' not in local_config:
                local_config['thumbnail'] = {}
            if 'runware' not in local_config['thumbnail']:
                local_config['thumbnail']['runware'] = {}
            
            # Runware設定を更新
            local_config['thumbnail']['runware'] = settings
            
            # ローカル設定ファイルに保存
            success = self._save_local_config(local_config)
            
            if success:
                # メイン設定のプロバイダーも更新
                if 'thumbnail' not in self.config:
                    self.config['thumbnail'] = {}
                self.config['thumbnail']['image_provider'] = 'runware'
                self._save_config()
                
                # 設定を再読み込み
                self.config = self._load_config()
                self.logger.info("Runware API設定をローカル設定ファイルに保存しました")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Runware API設定更新エラー: {e}")
            return False

    def update_stable_diffusion_settings(self, provider: str, settings: Dict[str, Any]) -> bool:
        """[DEPRECATED] この機能は廃止されました
        
        現在のシステムでは画像生成APIの直接設定は不要です。
        代わりに画像プロンプト生成機能を使用してください。
        """
        self.logger.warning("update_stable_diffusion_settings は廃止されました。画像プロンプト生成機能を使用してください。")
        return False
    
    def _save_local_config(self, local_config: Dict[str, Any]) -> bool:
        """ローカル設定ファイルを保存"""
        try:
            with open(self.local_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(local_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info("ローカル設定ファイルを保存しました")
            return True
            
        except Exception as e:
            self.logger.error(f"ローカル設定ファイル保存エラー: {e}")
            return False
    
    def validate_api_settings(self, provider: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """API設定の検証
        
        Returns:
            Dict with 'valid': bool and 'errors': List[str]
        """
        errors = []
        
        if provider == 'replicate':
            if not settings.get('api_token'):
                errors.append("Replicate API Tokenが必要です")
            elif not settings['api_token'].startswith('r8_'):
                errors.append("Replicate API Tokenは 'r8_' で始まる必要があります")
            
            if not settings.get('model'):
                errors.append("Replicateモデル名が必要です")
        
        elif provider == 'huggingface':
            if not settings.get('api_token'):
                errors.append("Hugging Face API Tokenが必要です")
            elif not settings['api_token'].startswith('hf_'):
                errors.append("Hugging Face API Tokenは 'hf_' で始まる必要があります")
            
            if not settings.get('model'):
                errors.append("Hugging Faceモデル名が必要です")
        
        elif provider == 'local':
            if not settings.get('server_url'):
                errors.append("ローカルサーバーURLが必要です")
            
            # URLの形式チェック
            server_url = settings.get('server_url', '')
            if server_url and not (server_url.startswith('http://') or server_url.startswith('https://')):
                errors.append("サーバーURLは http:// または https:// で始まる必要があります")
        
        else:
            errors.append(f"未知のプロバイダー: {provider}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def test_api_connection(self, provider: str) -> Dict[str, Any]:
        """API接続テスト"""
        try:
            settings = self.get_api_settings().get(provider, {})
            
            if provider == 'replicate':
                return self._test_replicate_connection(settings)
            elif provider == 'huggingface':
                return self._test_huggingface_connection(settings)
            elif provider == 'local':
                return self._test_local_connection(settings)
            else:
                return {'success': False, 'error': f'未知のプロバイダー: {provider}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_replicate_connection(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Replicate API接続テスト"""
        import requests
        
        api_token = settings.get('api_token')
        if not api_token:
            return {'success': False, 'error': 'API Tokenが設定されていません'}
        
        try:
            headers = {'Authorization': f'Token {api_token}'}
            response = requests.get('https://api.replicate.com/v1/predictions', 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Replicate API接続成功'}
            else:
                return {'success': False, 'error': f'API接続エラー: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'接続エラー: {str(e)}'}
    
    def _test_huggingface_connection(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Hugging Face API接続テスト"""
        import requests
        
        api_token = settings.get('api_token')
        if not api_token:
            return {'success': False, 'error': 'API Tokenが設定されていません'}
        
        try:
            headers = {'Authorization': f'Bearer {api_token}'}
            response = requests.get('https://huggingface.co/api/whoami', 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Hugging Face API接続成功'}
            else:
                return {'success': False, 'error': f'API接続エラー: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'接続エラー: {str(e)}'}
    
    def _test_local_connection(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """[DEPRECATED] ローカル接続テストは廃止されました"""
        return {'success': False, 'error': 'この機能は廃止されました。画像プロンプト生成機能を使用してください。'}
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """全プロバイダーの状態を取得"""
        providers = ['replicate', 'huggingface', 'local']
        status = {}
        
        for provider in providers:
            settings = self.get_api_settings().get(provider, {})
            
            # 設定の有無をチェック
            configured = False
            if provider == 'replicate':
                configured = bool(settings.get('api_token'))
            elif provider == 'huggingface':
                configured = bool(settings.get('api_token'))
            elif provider == 'local':
                configured = bool(settings.get('server_url'))
            
            status[provider] = {
                'configured': configured,
                'settings': settings,
                'last_test': None  # 接続テスト結果をキャッシュする場合
            }
        
        return status
    
    def export_settings(self) -> Dict[str, Any]:
        """設定をエクスポート（機密情報は除外）"""
        config_copy = self.config.copy()
        
        # API Tokenを除外
        if 'thumbnail' in config_copy and 'api_settings' in config_copy['thumbnail']:
            api_settings = config_copy['thumbnail']['api_settings']
            
            for provider in api_settings:
                if 'api_token' in api_settings[provider]:
                    api_settings[provider]['api_token'] = '***HIDDEN***'
        
        return config_copy
    
    def get_thumbnail_config(self) -> Dict[str, Any]:
        """サムネイル関連設定を取得"""
        return self.config.get('thumbnail', {})
    
    def update_thumbnail_config(self, updates: Dict[str, Any]) -> bool:
        """サムネイル設定を更新"""
        try:
            if 'thumbnail' not in self.config:
                self.config['thumbnail'] = {}
            
            # API設定以外の更新
            for key, value in updates.items():
                if key != 'api_settings':  # API設定は別メソッドで管理
                    self.config['thumbnail'][key] = value
            
            return self._save_config()
            
        except Exception as e:
            self.logger.error(f"サムネイル設定更新エラー: {e}")
            return False

if __name__ == "__main__":
    # テスト実行
    manager = ConfigManager()
    
    print("現在のAPI設定:")
    print(json.dumps(manager.get_api_settings(), indent=2, ensure_ascii=False))
    
    print("\nプロバイダー状態:")
    print(json.dumps(manager.get_provider_status(), indent=2, ensure_ascii=False))