#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫更新腳本
用於更新 power_reports 表格的 count 欄位約束，允許 count 為 0
"""

import sqlite3
import os
import sys
from datetime import datetime

def backup_database():
    """備份資料庫"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"kao_power_water_backup_{timestamp}.db"
    
    if os.path.exists("kao_power_water.db"):
        import shutil
        shutil.copy2("kao_power_water.db", backup_name)
        print(f"✅ 資料庫已備份為: {backup_name}")
        return backup_name
    else:
        print("❌ 找不到 kao_power_water.db 檔案")
        return None

def execute_sql_script(script_path):
    """執行 SQL 腳本"""
    try:
        # 連接到資料庫
        conn = sqlite3.connect("kao_power_water.db")
        cursor = conn.cursor()
        
        # 讀取 SQL 腳本
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 執行 SQL 腳本
        print("🔄 正在執行 SQL 腳本...")
        cursor.executescript(sql_script)
        
        # 提交變更
        conn.commit()
        
        # 驗證更新
        cursor.execute("PRAGMA table_info(power_reports)")
        columns = cursor.fetchall()
        
        # 找到 count 欄位
        count_column = None
        for col in columns:
            if col[1] == 'count':
                count_column = col
                break
        
        if count_column:
            print(f"✅ count 欄位約束已更新: {count_column[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 執行 SQL 腳本時發生錯誤: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """主函數"""
    print("🚀 開始更新資料庫...")
    print("=" * 50)
    
    # 檢查 SQL 腳本是否存在
    script_path = "db/update_count_constraint.sql"
    if not os.path.exists(script_path):
        print(f"❌ 找不到 SQL 腳本: {script_path}")
        sys.exit(1)
    
    # 備份資料庫
    backup_file = backup_database()
    if not backup_file:
        sys.exit(1)
    
    # 執行 SQL 腳本
    if execute_sql_script(script_path):
        print("✅ 資料庫更新成功！")
        print(f"📁 備份檔案: {backup_file}")
        print("=" * 50)
        print("💡 現在停電戶數可以設為 0，系統會自動將狀態改為已復電")
    else:
        print("❌ 資料庫更新失敗！")
        print(f"📁 備份檔案: {backup_file}")
        print("💡 您可以手動還原備份檔案")
        sys.exit(1)

if __name__ == "__main__":
    main() 