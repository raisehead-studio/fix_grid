#!/usr/bin/env python3
"""
暫時移除 Tailwind CSS 的 SRI 屬性以解決 CORS 問題
適用於開發環境
"""

import os
import re

def remove_tailwind_sri(file_path):
    """
    移除 Tailwind CSS 的 SRI 屬性
    
    Args:
        file_path (str): 文件路徑
    
    Returns:
        bool: 是否成功更新
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配有 integrity 屬性的 Tailwind CSS script 標籤
        pattern = r'<script src="https://cdn\.tailwindcss\.com" integrity="[^"]*" crossorigin="anonymous"></script>'
        replacement = '<script src="https://cdn.tailwindcss.com"></script>'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

def main():
    """主要函數"""
    templates_dir = '../app/templates'
    
    print("=== 移除 Tailwind CSS SRI 屬性 ===\n")
    
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
        if remove_tailwind_sri(file_path):
            print(f"  ✓ 已移除 Tailwind CSS SRI")
            updated_count += 1
        else:
            print(f"  - 無需更新")
        print()
    
    print(f"=== 更新完成 ===")
    print(f"總文件數: {len(html_files)}")
    print(f"已更新: {updated_count}")
    print(f"無需更新: {len(html_files) - updated_count}")
    print("\n注意：這只是暫時的解決方案，適用於開發環境。")
    print("生產環境建議使用本地 Tailwind CSS 文件或固定版本的 CDN。")

if __name__ == "__main__":
    main() 