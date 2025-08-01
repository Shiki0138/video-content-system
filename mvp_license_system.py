"""
VideoAI Studio MVP ライセンスシステム
シンプルな認証とプラン管理機能
"""

import json
import os
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Optional
import requests
from functools import wraps

class LicenseManager:
    """ライセンス管理クラス"""
    
    def __init__(self):
        self.license_file = Path.home() / ".videoai_studio" / "license.json"
        self.license_file.parent.mkdir(exist_ok=True)
        self.api_endpoint = "https://api.videoai-studio.com/v1"  # 将来のAPI
        self.plans = {
            "free": {
                "name": "Free Plan",
                "monthly_limit": 5,
                "max_duration": 600,  # 10分
                "features": ["basic"],
                "watermark": True
            },
            "pro": {
                "name": "Pro Plan", 
                "monthly_limit": 50,
                "max_duration": 1800,  # 30分
                "features": ["basic", "advanced", "priority"],
                "watermark": False,
                "price": 2980
            },
            "business": {
                "name": "Business Plan",
                "monthly_limit": -1,  # 無制限
                "max_duration": 3600,  # 60分
                "features": ["basic", "advanced", "priority", "api", "support"],
                "watermark": False,
                "price": 9980
            }
        }
    
    def activate_license(self, license_key: str) -> Dict:
        """ライセンスキーを検証してアクティベート"""
        # MVP版: シンプルなキー検証
        # 実際の実装ではAPIサーバーと通信
        
        # デモ用のハードコードされたキー
        demo_keys = {
            "DEMO-PRO-2024": "pro",
            "DEMO-BIZ-2024": "business"
        }
        
        if license_key in demo_keys:
            plan_type = demo_keys[license_key]
            license_data = {
                "key": license_key,
                "plan": plan_type,
                "activated_at": datetime.datetime.now().isoformat(),
                "expires_at": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
                "usage": {
                    "current_month": 0,
                    "last_reset": datetime.datetime.now().isoformat()
                }
            }
            
            # ライセンス情報を保存
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            
            return {
                "success": True,
                "message": f"{self.plans[plan_type]['name']}をアクティベートしました",
                "plan": plan_type
            }
        else:
            return {
                "success": False,
                "message": "無効なライセンスキーです"
            }
    
    def get_current_plan(self) -> str:
        """現在のプランを取得"""
        if not self.license_file.exists():
            return "free"
        
        try:
            with open(self.license_file, 'r') as f:
                data = json.load(f)
            
            # 有効期限チェック
            expires_at = datetime.datetime.fromisoformat(data['expires_at'])
            if expires_at < datetime.datetime.now():
                return "free"
            
            return data['plan']
        except:
            return "free"
    
    def check_usage_limit(self) -> Dict:
        """使用制限をチェック"""
        plan = self.get_current_plan()
        plan_info = self.plans[plan]
        
        if not self.license_file.exists():
            usage = {"current_month": 0}
        else:
            with open(self.license_file, 'r') as f:
                data = json.load(f)
                usage = data.get('usage', {"current_month": 0})
        
        # 月次リセットチェック
        if 'last_reset' in usage:
            last_reset = datetime.datetime.fromisoformat(usage['last_reset'])
            if last_reset.month != datetime.datetime.now().month:
                usage['current_month'] = 0
                usage['last_reset'] = datetime.datetime.now().isoformat()
                self._update_usage(usage)
        
        return {
            "plan": plan,
            "current_usage": usage['current_month'],
            "monthly_limit": plan_info['monthly_limit'],
            "remaining": -1 if plan_info['monthly_limit'] == -1 else plan_info['monthly_limit'] - usage['current_month'],
            "can_process": plan_info['monthly_limit'] == -1 or usage['current_month'] < plan_info['monthly_limit']
        }
    
    def increment_usage(self):
        """使用回数を増やす"""
        if not self.license_file.exists():
            usage = {"current_month": 1, "last_reset": datetime.datetime.now().isoformat()}
        else:
            with open(self.license_file, 'r') as f:
                data = json.load(f)
                usage = data.get('usage', {"current_month": 0})
                usage['current_month'] += 1
        
        self._update_usage(usage)
    
    def _update_usage(self, usage: Dict):
        """使用状況を更新"""
        if self.license_file.exists():
            with open(self.license_file, 'r') as f:
                data = json.load(f)
            data['usage'] = usage
            with open(self.license_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def check_video_duration(self, duration_seconds: int) -> bool:
        """動画の長さ制限をチェック"""
        plan = self.get_current_plan()
        max_duration = self.plans[plan]['max_duration']
        return duration_seconds <= max_duration
    
    def should_add_watermark(self) -> bool:
        """透かしを追加すべきか"""
        plan = self.get_current_plan()
        return self.plans[plan]['watermark']


# デコレーター: ライセンスチェック
def require_license(feature: str = "basic"):
    """ライセンスチェックデコレーター"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lm = LicenseManager()
            plan = lm.get_current_plan()
            plan_features = lm.plans[plan]['features']
            
            if feature not in plan_features:
                raise PermissionError(f"この機能は{feature}プラン以上で利用可能です")
            
            # 使用制限チェック
            usage_info = lm.check_usage_limit()
            if not usage_info['can_process']:
                raise PermissionError(f"月間処理数の上限に達しました（{usage_info['monthly_limit']}本）")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 使用例
if __name__ == "__main__":
    # ライセンスマネージャーの初期化
    lm = LicenseManager()
    
    # 現在のプランを確認
    print(f"現在のプラン: {lm.get_current_plan()}")
    
    # 使用状況を確認
    usage = lm.check_usage_limit()
    print(f"使用状況: {usage['current_usage']}/{usage['monthly_limit']}")
    
    # デモライセンスをアクティベート
    result = lm.activate_license("DEMO-PRO-2024")
    print(result['message'])