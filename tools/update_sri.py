#!/usr/bin/env python3
"""
批量更新 HTML 模板文件，添加 SRI (Subresource Integrity) 屬性
"""

import os
import re

# SRI 雜湊值對應表
SRI_HASHES = {
    'https://cdn.tailwindcss.com': 'sha384-igm5BeiBt36UU4gqwWS7imYmelpTsZlQ45FZf+XBn9MuJbn4nQr7yx1yFydocC/K',
    'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js': 'sha384-vtjasyidUo0kW94K5MXDXntzOJpQgBKXmE7e2Ga4LG0skTTLeBi97eFAXsqewJjw',
    'https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js': 'sha384-vtjasyidUo0kW94K5MXDXntzOJpQgBKXmE7e2Ga4LG0skTTLeBi97eFAXsqewJjw',
    'https://cdn.jsdelivr.net/npm/xlsx-populate/browser/xlsx-populate.min.js': 'sha384-YnsK3VaaV54M5EcU58Pt9SdJqzL0iZpQzQAcav+18Kgn5tbwk16y/3g6FpT2d83h',
    'https://cdn.jsdelivr.net/npm/chart.js': 'sha384-XcdcwHqIPULERb2yDEM4R0XaQKU3YnDsrTmjACBZyfdVVqjh6xQ4/DCMd7XLcA6Y'
}

def update_file_sri(file_path):
    """
    更新單個文件的 SRI 屬性
    
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
        for url, sri_hash in SRI_HASHES.items():
            # 匹配沒有 integrity 屬性的 script 標籤
            pattern = rf'<script src="{re.escape(url)}"></script>'
            replacement = f'<script src="{url}" integrity="{sri_hash}" crossorigin="anonymous"></script>'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated = True
                print(f"  ✓ 已更新: {url}")
        
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
    
    print("=== 批量更新 SRI 屬性 ===\n")
    
    if not os.path.exists(templates_dir):
        print(f"❌ 模板目錄不存在: {templates_dir}")
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
        if update_file_sri(file_path):
            updated_count += 1
        print()
    
    print(f"=== 更新完成 ===")
    print(f"總文件數: {len(html_files)}")
    print(f"已更新: {updated_count}")
    print(f"無需更新: {len(html_files) - updated_count}")

if __name__ == "__main__":
    main() 