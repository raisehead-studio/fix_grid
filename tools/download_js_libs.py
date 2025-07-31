#!/usr/bin/env python3
"""
下載外部 JavaScript 庫到本地 app/js 資料夾
"""

import os
import urllib.request
import hashlib

# 需要下載的 JavaScript 庫
JS_LIBRARIES = [
    {
        'url': 'https://cdn.tailwindcss.com',
        'filename': 'tailwindcss.js',
        'description': 'Tailwind CSS'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
        'filename': 'xlsx.full.min.js',
        'description': 'XLSX.js v0.18.5'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js',
        'filename': 'xlsx.latest.min.js',
        'description': 'XLSX.js (latest)'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/xlsx-populate/browser/xlsx-populate.min.js',
        'filename': 'xlsx-populate.min.js',
        'description': 'XLSX-Populate'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/chart.js',
        'filename': 'chart.js',
        'description': 'Chart.js'
    }
]

def download_file(url, filename, description):
    """
    下載文件到本地
    
    Args:
        url (str): 下載 URL
        filename (str): 本地文件名
        description (str): 文件描述
    
    Returns:
        bool: 是否成功下載
    """
    try:
        output_path = os.path.join('app/js', filename)
        
        print(f"正在下載: {description}")
        print(f"URL: {url}")
        print(f"保存到: {output_path}")
        
        # 設定 User-Agent 以避免被阻擋
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        
        # 寫入文件
        with open(output_path, 'wb') as f:
            f.write(content)
        
        # 計算文件大小
        file_size = len(content)
        print(f"✓ 成功下載: {filename} ({file_size:,} bytes)")
        
        # 生成 SHA-384 雜湊值
        hash_obj = hashlib.new('sha384')
        hash_obj.update(content)
        hash_b64 = hash_obj.digest().hex()
        print(f"  SHA-384: {hash_b64[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return False

def main():
    """主要函數"""
    js_dir = 'app/js'
    
    print("=== 下載 JavaScript 庫到本地 ===\n")
    
    # 確保目錄存在
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
        print(f"創建目錄: {js_dir}")
    
    success_count = 0
    
    for lib in JS_LIBRARIES:
        print(f"\n處理: {lib['description']}")
        if download_file(lib['url'], lib['filename'], lib['description']):
            success_count += 1
        print()
    
    print(f"=== 下載完成 ===")
    print(f"成功下載: {success_count}/{len(JS_LIBRARIES)}")
    
    if success_count == len(JS_LIBRARIES):
        print("\n所有文件已下載完成！")
        print("接下來可以運行 update_to_local.py 來更新 HTML 模板。")
    else:
        print("\n部分文件下載失敗，請檢查網路連接。")

if __name__ == "__main__":
    main() 