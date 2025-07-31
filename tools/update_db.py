#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫更新腳本
用於更新三張表格的結構，包含 report_updated_time 欄位
同時更新 power_reports 的 count 欄位約束和 original_count 欄位
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
        print("🔍 驗證表格結構...")
        
        # 檢查 power_reports 表格
        cursor.execute("PRAGMA table_info(power_reports)")
        power_columns = cursor.fetchall()
        power_column_names = [col[1] for col in power_columns]
        
        # 檢查 water_reports 表格
        cursor.execute("PRAGMA table_info(water_reports)")
        water_columns = cursor.fetchall()
        water_column_names = [col[1] for col in water_columns]
        
        # 檢查 taiwater_power_reports 表格
        cursor.execute("PRAGMA table_info(taiwater_power_reports)")
        taiwater_columns = cursor.fetchall()
        taiwater_column_names = [col[1] for col in taiwater_columns]
        
        # 驗證結果
        success = True
        
        if 'report_updated_time' in power_column_names:
            print("✅ power_reports 表格已新增 report_updated_time 欄位")
        else:
            print("❌ power_reports 表格缺少 report_updated_time 欄位")
            success = False
            
        if 'original_count' in power_column_names:
            print("✅ power_reports 表格已新增 original_count 欄位")
        else:
            print("❌ power_reports 表格缺少 original_count 欄位")
            success = False
            
        if 'report_updated_time' in water_column_names:
            print("✅ water_reports 表格已新增 report_updated_time 欄位")
        else:
            print("❌ water_reports 表格缺少 report_updated_time 欄位")
            success = False
            
        if 'report_updated_time' in taiwater_column_names:
            print("✅ taiwater_power_reports 表格已新增 report_updated_time 欄位")
        else:
            print("❌ taiwater_power_reports 表格缺少 report_updated_time 欄位")
            success = False
        
        conn.close()
        return success
        
    except Exception as e:
        print(f"❌ 執行 SQL 腳本時發生錯誤: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """主函數"""
    print("🚀 開始更新資料庫...")
    print("=" * 50)
    print("📝 本次更新內容：")
    print("   • power_reports: 新增 original_count 和 report_updated_time 欄位")
    print("   • water_reports: 新增 report_updated_time 欄位")
    print("   • taiwater_power_reports: 新增 report_updated_time 欄位")
    print("   • power_reports: count 欄位允許 0 值")
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
        print("💡 更新完成，現在系統支援：")
        print("   • 停電戶數可以設為 0，系統會自動將狀態改為已復電")
        print("   • 所有通報都有 report_updated_time 欄位記錄最後編輯時間")
        print("   • power_reports 有 original_count 欄位記錄原始戶數")
    else:
        print("❌ 資料庫更新失敗！")
        print(f"📁 備份檔案: {backup_file}")
        print("💡 您可以手動還原備份檔案")
        sys.exit(1)

if __name__ == "__main__":
    main() 