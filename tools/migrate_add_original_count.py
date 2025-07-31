#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 original_count 欄位到 power_reports 表
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_add_original_count():
    """添加 original_count 欄位"""
    try:
        # 連接到資料庫
        conn = sqlite3.connect("kao_power_water.db")
        cursor = conn.cursor()
        
        print("🔄 開始添加 original_count 欄位...")
        
        # 1. 檢查欄位是否已存在（僅用於顯示資訊）
        cursor.execute("PRAGMA table_info(power_reports)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'original_count' in columns:
            print("ℹ️ original_count 欄位已存在，將重新建立表格")
        else:
            print("ℹ️ original_count 欄位不存在，將重新建立表格")
        
        print("📝 備份現有資料...")
        # 2. 檢查並刪除已存在的備份表格
        cursor.execute("DROP TABLE IF EXISTS power_reports_backup")
        
        # 3. 備份現有資料
        cursor.execute("CREATE TABLE power_reports_backup AS SELECT * FROM power_reports")
        print(f"✅ 已備份 {cursor.rowcount} 筆資料")
        
        print("🔧 刪除現有表格並重新建立...")
        # 3. 刪除現有表格
        cursor.execute("DROP TABLE power_reports")
        
        # 4. 重新建立表格（執行 power_reports.sql）
        with open("db/power_reports.sql", 'r', encoding='utf-8') as f:
            sql_content = f.read()
        cursor.executescript(sql_content)
        
        print("🔄 還原資料...")
        # 5. 將備份資料還原到新表格
        cursor.execute("""
            INSERT INTO power_reports (
                id, district_id, village_id, location, reason, count, 
                contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
                report_status, report_restored_at, taipower_status, taipower_restored_at, 
                taipower_note, taipower_eta_hours, taipower_support, original_count
            )
            SELECT 
                id, district_id, village_id, location, reason, count,
                contact_name, contact_phone, created_by, created_at, updated_at, deleted_at,
                report_status, report_restored_at, taipower_status, taipower_restored_at,
                taipower_note, taipower_eta_hours, taipower_support, count as original_count
            FROM power_reports_backup
        """)
        restored_count = cursor.rowcount
        print(f"✅ 已還原 {restored_count} 筆資料")
        
        # 6. 刪除備份表格
        cursor.execute("DROP TABLE power_reports_backup")
        print("✅ 已刪除備份表格")
        
        # 7. 驗證資料
        cursor.execute("SELECT COUNT(*) FROM power_reports WHERE original_count = 0")
        zero_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM power_reports")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 驗證結果:")
        print(f"   - 總筆數: {total_count}")
        print(f"   - 已還原: {restored_count}")
        print(f"   - 未還原: {zero_count}")
        
        # 8. 顯示範例資料
        cursor.execute("SELECT id, count, original_count FROM power_reports LIMIT 5")
        samples = cursor.fetchall()
        
        print(f"\n📋 資料範例:")
        for sample in samples:
            print(f"   - ID {sample[0]}: count={sample[1]}, original_count={sample[2]}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 遷移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 開始執行資料庫遷移...")
    print("=" * 50)
    
    if migrate_add_original_count():
        print("\n✅ 遷移成功！")
    else:
        print("\n❌ 遷移失敗！")
        sys.exit(1) 