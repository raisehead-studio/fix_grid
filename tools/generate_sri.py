#!/usr/bin/env python3
"""
SRI (Subresource Integrity) 雜湊值生成工具
用於為外部 CDN 資源生成 integrity 屬性值
"""

import hashlib
import base64
import urllib.request
import sys

def generate_sri_hash(url, algorithm='sha384'):
    """
    從 URL 下載資源並生成 SRI 雜湊值
    
    Args:
        url (str): 資源的 URL
        algorithm (str): 雜湊算法 (sha256, sha384, sha512)
    
    Returns:
        str: SRI 雜湊值
    """
    try:
        print(f"正在下載: {url}")
        
        # 設定 User-Agent 以避免被阻擋
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(content)
        
        # 生成 base64 編碼的雜湊值
        hash_b64 = base64.b64encode(hash_obj.digest()).decode('utf-8')
        sri_hash = f"{algorithm}-{hash_b64}"
        
        print(f"成功生成 SRI 雜湊值: {sri_hash}")
        return sri_hash
        
    except Exception as e:
        print(f"錯誤: 無法生成 {url} 的 SRI 雜湊值: {e}")
        return None

def main():
    """主要函數"""
    # 定義需要生成 SRI 的資源
    resources = [
        {
            'url': 'https://cdn.tailwindcss.com',
            'type': 'script',
            'description': 'Tailwind CSS CDN'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
            'type': 'script',
            'description': 'XLSX.js Library v0.18.5'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js',
            'type': 'script',
            'description': 'XLSX.js Library (latest)'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/xlsx-populate/browser/xlsx-populate.min.js',
            'type': 'script',
            'description': 'XLSX-Populate Library'
        },
        {
            'url': 'https://cdn.jsdelivr.net/npm/chart.js',
            'type': 'script',
            'description': 'Chart.js Library'
        }
    ]
    
    print("=== SRI 雜湊值生成工具 ===\n")
    
    results = {}
    
    for resource in resources:
        print(f"處理: {resource['description']}")
        sri_hash = generate_sri_hash(resource['url'])
        
        if sri_hash:
            results[resource['url']] = sri_hash
            print(f"HTML 標籤範例:")
            if resource['type'] == 'script':
                print(f'<script src="{resource["url"]}" integrity="{sri_hash}" crossorigin="anonymous"></script>')
            elif resource['type'] == 'link':
                print(f'<link href="{resource["url"]}" integrity="{sri_hash}" crossorigin="anonymous" rel="stylesheet">')
            print()
        else:
            print(f"❌ 無法為 {resource['description']} 生成 SRI 雜湊值\n")
    
    # 輸出所有結果的摘要
    print("=== 所有 SRI 雜湊值摘要 ===")
    for url, sri_hash in results.items():
        print(f"{url}: {sri_hash}")

if __name__ == "__main__":
    main() 