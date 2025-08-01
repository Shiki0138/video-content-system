#!/usr/bin/env python3
"""
人物画像生成デバッグ
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import uuid

async def debug_portrait():
    """人物画像生成のデバッグ"""
    
    api_key = "L14OZVbzaiAfoSVBsRSE667t0rjVleqq"
    
    print("🔍 人物画像生成デバッグ")
    
    output_dir = Path("output/debug_portrait") / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # シンプルな人物プロンプト
    prompt = "professional headshot of smiling Japanese businessman, clean background, high quality"
    negative = "blurry, low quality, distorted face"
    
    payload = [
        {
            "taskType": "imageInference",
            "taskUUID": str(uuid.uuid4()),
            "model": "civitai:25694@143906",
            "positivePrompt": prompt,
            "negativePrompt": negative,
            "height": 704,
            "width": 1280,
            "numberResults": 1,
            "outputFormat": "PNG",
            "outputType": "URL",
            "steps": 25,
            "CFGScale": 7.0
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"📤 リクエスト送信中...")
            async with session.post(
                "https://api.runware.ai/v1",
                headers=headers,
                json=payload
            ) as response:
                print(f"📥 レスポンス受信: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 成功レスポンス:")
                    print(json.dumps(result, indent=2))
                    
                    if 'data' in result and len(result['data']) > 0:
                        image_info = result['data'][0]
                        image_url = image_info.get('imageURL')
                        
                        if image_url:
                            print(f"🖼️ 画像URL: {image_url}")
                            
                            # 画像ダウンロード
                            async with session.get(image_url) as img_response:
                                if img_response.status == 200:
                                    image_bytes = await img_response.read()
                                    
                                    file_path = output_dir / "debug_portrait.png"
                                    with open(file_path, 'wb') as f:
                                        f.write(image_bytes)
                                    
                                    print(f"💾 保存成功: {file_path}")
                                else:
                                    print(f"❌ 画像ダウンロード失敗: {img_response.status}")
                        else:
                            print("❌ 画像URLが見つかりません")
                    else:
                        print("❌ データが空です")
                else:
                    error_text = await response.text()
                    print(f"❌ APIエラー ({response.status}): {error_text}")
                    
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_portrait())