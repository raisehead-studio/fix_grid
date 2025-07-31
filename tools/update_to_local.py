#!/usr/bin/env python3
"""
更新 HTML 模板，將 CDN 引用改為本地 JavaScript 文件
"""

import os
import re

# CDN URL 到本地文件的映射
CDN_TO_LOCAL = {
    'https://cdn.tailwindcss.com': '/static/js/tailwindcss.js',
    'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js': '/static/js/xlsx.full.min.js',
    'https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js': '/static/js/xlsx.latest.min.js',
    'https://cdn.jsdelivr.net/npm/xlsx-populate/browser/xlsx-populate.min.js': '/static/js/xlsx-populate.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js': '/static/js/chart.js'
}

def update_file_to_local(file_path):
    """
    更新單個文件，將 CDN 引用改為本地文件
    
    Args:
        file_path (str): 文件路徑
    
    Returns:
        bool: 是否成功更新
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # 更新每個 CDN 資源
        for cdn_url, local_path in CDN_TO_LOCAL.items():
            # 匹配有或沒有 integrity 屬性的 script 標籤
            pattern_with_integrity = rf'<script src="{re.escape(cdn_url)}" integrity="[^"]*" crossorigin="anonymous"></script>'
            pattern_without_integrity = rf'<script src="{re.escape(cdn_url)}"></script>'
            
            replacement = f'<script src="{local_path}"></script>'
            
            # 先檢查有 integrity 的版本
            if re.search(pattern_with_integrity, content):
                content = re.sub(pattern_with_integrity, replacement, content)
                updated = True
                print(f"  ✓ 已更新 (有 SRI): {cdn_url} -> {local_path}")
            # 再檢查沒有 integrity 的版本
            elif re.search(pattern_without_integrity, content):
                content = re.sub(pattern_without_integrity, replacement, content)
                updated = True
                print(f"  ✓ 已更新 (無 SRI): {cdn_url} -> {local_path}")
        
        # 如果有更新，寫回文件
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print(f"  - 無需更新")
            return False
            
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

def main():
    """主要函數"""
    templates_dir = 'app/templates'
    
    print("=== 更新 HTML 模板為本地 JavaScript 文件 ===\n")
    
    if not os.path.exists(templates_dir):
        print(f"❌ 模板目錄不存在: {templates_dir}")
        return
    
    # 檢查本地 JavaScript 文件是否存在
    js_dir = 'app/js'
    if not os.path.exists(js_dir):
        print(f"❌ JavaScript 目錄不存在: {js_dir}")
        print("請先運行 download_js_libs.py 下載 JavaScript 庫")
        return
    
    # 獲取所有 HTML 文件
    html_files = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"找到 {len(html_files)} 個 HTML 文件\n")
    
    updated_count = 0
    
    for file_path in sorted(html_files):
        print(f"處理: {file_path}")
        if update_file_to_local(file_path):
            updated_count += 1
        print()
    
    print(f"=== 更新完成 ===")
    print(f"總文件數: {len(html_files)}")
    print(f"已更新: {updated_count}")
    print(f"無需更新: {len(html_files) - updated_count}")
    
    print("\n=== 本地文件映射 ===")
    for cdn_url, local_path in CDN_TO_LOCAL.items():
        print(f"{cdn_url} -> {local_path}")
    
    print("\n注意：")
    print("1. 所有 JavaScript 文件現在都從本地載入")
    print("2. 不再需要 SRI 屬性，因為文件是本地控制的")
    print("3. 確保 Flask 應用程式正確配置了靜態文件路由")

if __name__ == "__main__":
    main() 